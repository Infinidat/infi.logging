from socket import gethostname
from .request_id_tag import get_request_id_tag_from_record
from .processors import get_thread_id_from_record
from .dependencies import USE_DEFAULT, should_use_gevent, should_use_procname

MODULU = 32768


def create_file_formatter(*args, **kwargs):
    """
    Similar to `create_syslog_formatter` but adds the date, time and host name to the formatted message.
    :param hostname: optional kwarg to set the host name. If None `socket.gethostname()` will be used.
    """
    hostname = kwargs.pop('hostname', None)
    if hostname is None:
        hostname = gethostname()
    syslog_formatter = create_syslog_formatter(*args, **kwargs)

    def formatter(record, handler):
        return "{:%Y-%m-%d %H:%M:%S} {} ".format(record.time, hostname) + syslog_formatter(record, handler)
    return formatter


def create_syslog_formatter(pid=True, procname=USE_DEFAULT, thread_id=True, greenlet_id=USE_DEFAULT,
                            thread_modulu=MODULU, request_id_tag=True, module=True, level=True, msg=True):
    """
    Builds a formatter function with the list of fields specified in the arguments.
    :param pid: add pid=<pid> to the formatted message
    :param procname: if pid is True adds a pid=<pid>:<pname>, if pid is False adds pname=<pname>. Depends on either
                     manually setting procname with `infi.logging.processors.procname.set_procname()` or having the
                     `setproctitle` package installed.
    :param thread_id: add a tid=<tid> to the formatted message where tid is the thread ID modulu `thread_modulu`.
    :param greenlet_id: if thread_id is True adds a tid=<tid>:<gid> to the formatted message where tid and gid are the
                        thread ID and greenlet ID modulu `thread_modulu` (requires gevent).
    :param thread_modulu: the modulu used when writing tid and gid.
    :param request_id_tag: if True adds a tag=<requestidtag> to the formatted message.
    :param module: if True adds a module=<logchannel> to the formatted message.
    :param level: if True adds a level=<level> to the formatted message.
    :param msg: if True adds a msg=<msg> to the formatted message.
    :returns: formatter function (f(record, handler): str)

    So using all defaults:
    formatter = create_syslog_formatter()
    formatter(record) -->  # whitespaces between fields below were clipped so it'll fit in a single line
      pid=00042:myproc tid=00001:00004 tag=00000foo module=mymodule level=DEBUG msg=message
    """
    strformats = []
    getters = []
    greenlet_id = should_use_gevent(greenlet_id)
    procname = should_use_procname(procname)

    field_to_getter = dict(pid=lambda r: r.process,
                           thread_id=lambda r: get_thread_id_from_record(r) % thread_modulu,
                           request_id_tag=lambda r: get_request_id_tag_from_record(r) or 0,
                           module=lambda r: r.channel,
                           level=lambda r: 'TRACE' if r.extra.get('trace', False) else r.level_name,
                           msg=lambda r: r.message + ('\n' + r.formatted_exception if r.formatted_exception else ''))
    if procname:
        from .processors import get_procname_from_record
        field_to_getter['procname'] = lambda r: get_procname_from_record(r)
    if greenlet_id:
        from .processors import get_greenlet_id_from_record
        field_to_getter['greenlet_id'] = lambda r: get_greenlet_id_from_record(r) % thread_modulu
    field_to_format = dict(pid='{:0>5}',
                           procname='{: <28}',
                           thread_id='{:0>5}',
                           greenlet_id='{:0>5}',
                           request_id_tag='{:0>8}',
                           module='{: <40}',
                           level='{: <7}',
                           msg='{}')

    def extend_format(str, *field_names):
        getters.extend([field_to_getter[f] for f in field_names])
        strformats.append(str.format(*(field_to_format[f] for f in field_names)))

    if pid and procname:
        extend_format('pid={}:{}', 'pid', 'procname')
    elif pid:
        extend_format('pid={}', 'pid')
    elif procname:
        extend_format('pname={}', 'procname')

    if thread_id and greenlet_id:
        extend_format('tid={}:{}', 'thread_id', 'greenlet_id')
    elif thread_id:
        extend_format('tid={}', 'thread_id')
    elif greenlet_id:
        extend_format('gid={}', 'greenlet_id')

    if request_id_tag:
        extend_format('tag={}', 'request_id_tag')
    if module:
        extend_format('module={}', 'module')
    if level:
        extend_format('level={}', 'level')
    if msg:
        extend_format('msg={}', 'msg')

    strformat = " ".join(strformats)

    def formatter(record, handler):
        return strformat.format(*(g(record) for g in getters))
    return formatter
