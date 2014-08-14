from infi.logging.plugins import InjectorPlugin, FormatterPlugin

try:
    import setproctitle

    def get_proc_title():
        return setproctitle.getproctitle()
except ImportError:
    def get_proc_title():
        return None


PROCNAME_KEY = 'procname'
_procname = None


def set_procname(s):
    """
    Sets the process name to be used in logging. This is useful if setproctitle package doesn't exist and you want to
    manually set the process name.
    :param s: process name
    :type s: str
    """
    global _procname
    _procname = s


def get_procname():
    """
    Returns the process name used for logging, calls `refresh_procname_if_none()` to make sure there's a process name.
    :returns: process name str (not None)
    """
    global _procname
    refresh_procname_if_none()
    return _procname


def refresh_procname_if_none(force=False):
    """
    If process name is None or `force` is True, fetches the process name by using `setproctitle` package and raises
    an error if it doesn't exist.
    :param force: even if there is already a process name, refresh it from `setproctitle`.
    """
    global _procname
    if _procname is None or force:
        _procname = get_proc_title()


def inject_procname(record):
    """
    Sets the process name on `record.extra`.
    :param record: logbook record
    """
    record.extra[PROCNAME_KEY] = get_procname()


def get_procname_from_record(record):
    """
    :param record: logbook record
    :returns: current process name retrieved from the logbook record
    """
    return record.extra.get(PROCNAME_KEY, '')


class ProcnameInjectorPlugin(InjectorPlugin):
    def inject(self, record):
        return inject_procname(record)


class ProcnameFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_procname_from_record(record)

    def get_format_string(self):
        return "{: <28}"

    def get_format_key(self):
        return "procname"
