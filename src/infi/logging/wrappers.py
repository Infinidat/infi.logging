import logbook
import sys
import os
from infi.pyutils.contexts import contextmanager
from infi.pyutils.decorators import wraps

from .compat import redirect_python_logging_to_logbook
from .processors import create_processor
from .handlers import RotatingFileHandler
from .formatters import create_default_formatter
from .plugins import _true
from .plugins.procname import get_procname

try:
    from .handlers import SyslogHandler
    _has_syslog_handler = True
except ImportError:
    _has_syslog_handler = False


def _not_time(s):
    return s != 'time'


def _syslog_pred(s):
    return s not in ['time', 'hostname', 'procname', 'process_id']


def create_rotating_file_handler(path, mode='a', encoding='utf-8', level=logbook.DEBUG, delay=False,
                                 max_size=1024 * 1024, backup_count=32, formatter_plugin_predicate=_true):
    """Convenience function to create a rotating file handler with the default formatter."""
    handler = RotatingFileHandler(filename=path, mode=mode, encoding=encoding, level=level, delay=delay,
                                  max_size=max_size, backup_count=backup_count, bubble=True)
    handler.formatter = create_default_formatter(formatter_plugin_predicate)
    return handler


def create_stream_handler(stream, level=logbook.INFO, formatter_plugin_predicate=_not_time):
    """Convenience function to create a stream handler with the default formatter (w/o time field)."""
    handler = logbook.StreamHandler(sys.stderr, level=level, bubble=True)
    handler.formatter = create_default_formatter(formatter_plugin_predicate)
    return handler


def create_stdout_handler(level=logbook.INFO, formatter_plugin_predicate=_not_time):
    """Convenience function to create an STDOUT handler with the default formatter (w/o time field)."""
    return create_stream_handler(sys.stdout, level, formatter_plugin_predicate)


def create_stderr_handler(level=logbook.INFO, formatter_plugin_predicate=_not_time):
    """Convenience function to create an STDERR handler with the default formatter (w/o time field)."""
    return create_stream_handler(sys.stderr, level, formatter_plugin_predicate)


def create_syslog_handler(facility=logbook.SyslogHandler.LOG_LOCAL1, buffer_size=1024, message_size=32768,
                          address=("127.0.0.1", 514), level=logbook.DEBUG, formatter_plugin_predicate=_syslog_pred):
    """Convenience function to create an syslog handler with the default formatter."""
    from socket import gethostname
    application_name = get_procname()
    if application_name is None:
        application_name = 'python'
    handler = SyslogHandler(facility=facility, host_name=gethostname(), application_name=application_name,
                            process_id=str(os.getpid()), address=address, level=level, bubble=True,
                            syslog_buffer_size=buffer_size, syslog_message_size=message_size)
    handler.formatter = create_default_formatter(formatter_plugin_predicate)
    return handler


@contextmanager
def script_logging_context(syslog=_has_syslog_handler, syslog_facility=logbook.SyslogHandler.LOG_LOCAL1,
                           syslog_buffer_size=1024, syslog_message_size=32768, syslog_address=("127.0.0.1", 514),
                           syslog_level=logbook.DEBUG, logfile=True, logfile_path="logfile", logfile_mode='a',
                           logfile_encoding='utf-8', logfile_level=logbook.DEBUG, logfile_delay=False,
                           logfile_max_size=1024 * 1024, logfile_backup_count=32, stderr=True,
                           stderr_level=logbook.INFO):
    """
    Context manager that creates a setup of logbook handlers based on the parameters received and sensible defaults.
    """
    from logbook.concurrency import enable_gevent
    enable_gevent()
    redirect_python_logging_to_logbook()

    processor = create_processor()
    flags = logbook.Flags(errors='silent')
    handlers = [logbook.NullHandler()]

    if syslog:
        handlers.append(create_syslog_handler(facility=syslog_facility, buffer_size=syslog_buffer_size,
                                              message_size=syslog_message_size, address=syslog_address,
                                              level=syslog_level))
    if logfile:
        handlers.append(create_rotating_file_handler(path=logfile_path, mode=logfile_mode,
                                                     encoding=logfile_encoding, level=logfile_level,
                                                     delay=logfile_delay, max_size=logfile_max_size,
                                                     backup_count=logfile_backup_count))
    if stderr:
        handlers.append(create_stderr_handler(level=stderr_level))

    with logbook.NestedSetup([processor, flags] + handlers).applicationbound():
        yield


def script_logging_decorator(func=None, *args, **kwargs):
    """Decorator equivalent for `script_logging_context`"""
    def decorate(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            with script_logging_context():
                return f(*args, **kwargs)
        return decorator
    if func is None:
        return decorate
    else:
        return decorate(func)
