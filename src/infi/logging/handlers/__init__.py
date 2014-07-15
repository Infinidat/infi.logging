__all__ = ['RotatingFileHandler']
from .rotating_file_handler import RotatingFileHandler

try:
    import infi.tracing
    _has_infi_tracing = True
except ImportError:
    _has_infi_tracing = False

if _has_infi_tracing:
    __all__ += ['SyslogHandler']
    from .syslog_handler import SyslogHandler
