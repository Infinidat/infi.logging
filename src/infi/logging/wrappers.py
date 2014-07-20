import logbook
import sys
import os
from socket import gethostname
from infi.pyutils.contexts import contextmanager
from infi.pyutils.decorators import wraps

from .compat import redirect_python_logging_to_logbook
from .processors import create_inject_extra_data, refresh_procname_if_none, set_procname
from .handlers import RotatingFileHandler
from .formatters import create_file_formatter, create_syslog_formatter
from .dependencies import USE_DEFAULT, should_use_procname, should_use_syslog


def _new_handler(klass, formatter, *args, **kwargs):
    handler = klass(*args, **kwargs)
    handler.formatter = formatter
    return handler


@contextmanager
def script_logging_context(process_name=USE_DEFAULT,
                           host_name=None,
                           syslog=USE_DEFAULT,
                           syslog_facility=logbook.SyslogHandler.LOG_LOCAL1,
                           syslog_buffer_size=1024,
                           syslog_message_size=32768,
                           syslog_address=("localhost", 514),
                           syslog_level=logbook.DEBUG,
                           logfile=True,
                           logfile_path=None,
                           logfile_mode='a',
                           logfile_encoding='utf-8',
                           logfile_level=logbook.DEBUG,
                           logfile_delay=False,
                           logfile_max_size=1024 * 1024,
                           logfile_backup_count=32,
                           stderr=True,
                           stderr_level=logbook.INFO):
    """
    Context manager that creates a setup of logbook handlers based on the parameters received and sensible defaults.
    :param process_name: can be one of the following:
      * str or unicode: manaully set the process name used in logging
      * None or False: don't add the process name to logging
      * USE_DEFAULT: if `setproctitle` package exists then use it to discover the process name, otherwise don't add
                     process name.
    :param host_name: host name, if None `gethostname()` will be used
    :param syslog: if True then syslog handler will be added and the rest of the syslog parameters will be used to
                   initialize it. If USE_DEFAULT then it depends on the dependencies.
    :param logfile: if True then a rotating file handler will be added and the rest of the logfile parameters will be
                    used to initialize it.
    :param stderr: if True then a stderr stream handler will be added and the rest of the stderr parameters will be used
                   to initialize it.
    """
    if isinstance(process_name, (str, unicode)):
        set_procname(process_name)
        process_name = True
    else:
        process_name = should_use_procname(process_name)
        if process_name:
            refresh_procname_if_none()

    if host_name is None:
        host_name = gethostname()

    redirect_python_logging_to_logbook()

    processor = logbook.Processor(create_inject_extra_data(procname=process_name))
    flags = logbook.Flags(errors='silent')
    handlers = [logbook.NullHandler(bubble=False)]

    if should_use_syslog(syslog):
        from .handlers import SyslogHandler
        syslog_formatter = create_syslog_formatter(procname=process_name)
        handlers.append(_new_handler(SyslogHandler, syslog_formatter,
                                     facility=syslog_facility,
                                     host_name=host_name,
                                     application_name=process_name,
                                     process_id=os.getpid(),
                                     address=syslog_address,
                                     level=syslog_level,
                                     bubble=True,
                                     syslog_buffer_size=syslog_buffer_size,
                                     syslog_message_size=syslog_message_size))

    file_formatter = create_file_formatter(hostname=host_name, procname=process_name)
    if logfile:
        handlers.append(_new_handler(RotatingFileHandler, file_formatter,
                                     filename=logfile_path,
                                     mode=logfile_mode,
                                     encoding=logfile_encoding,
                                     level=logfile_level,
                                     delay=logfile_delay,
                                     max_size=logfile_max_size,
                                     backup_count=logfile_backup_count,
                                     bubble=True))
    if stderr:
            handlers.append(_new_handler(logbook.StreamHandler, file_formatter, sys.stderr,
                                         level=stderr_level, bubble=True))

    with logbook.NestedSetup([processor, flags] + handlers).applicationbound():
        yield


def script_logging_decorator(func=None, *args, **kwargs):
    """Decorator equivalent for `script_logging_context`"""
    def decorate(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            with script_logging_context():
                return func(*args, **kwargs)
        return decorator
    if func is None:
        return decorate
    else:
        return decorate(func)

# def entry_point_logging_decorator(name, syslog=has_syslog_handler, logfile=False, stderr=False):
#     def wrapped(func):
#         @wraps(func)
#         def decorator(*args, **kwargs):
#             context = script_logging_context(name, syslog, logfile, stderr)
#             context.__enter__()
#             return_value = func(*args, **kwargs)
#             return return_value
#         return decorator
#     return wrapped
