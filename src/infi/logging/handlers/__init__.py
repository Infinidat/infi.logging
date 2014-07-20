from infi.logging.dependencies import has_infi_tracing
from .rotating_file_handler import RotatingFileHandler

__all__ = ['RotatingFileHandler']

if has_infi_tracing:
    from .syslog_handler import SyslogHandler
    __all__.append('SyslogHandler')
