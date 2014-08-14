from infi.pyutils.decorators import wraps
from infi.pyutils.contexts import contextmanager
from .globals import get_time, get_logger


@contextmanager
def log_timing_context(title, logger=None, log_level="DEBUG"):
    """
    Log the execution time of the context. It generates two log messages: before yielding and after.
    :param title: str to add to the log messages
    :param logger: logger to use, or None if using the default logger
    :param log_level: str log level to use [TRACE|DEBUG|INFO|...]
    """
    global _logger
    if logger is None:
        logger = get_logger()
    log = getattr(logger, log_level.lower())
    t0 = get_time()
    log("started timing {} at {:.4f}".format(title, t0))
    try:
        yield
    finally:
        t1 = get_time()
        log("ended timing {} at {:.4f}. time taken: {:.4f} seconds".format(title, t1, t1 - t0))


def log_timing(func=None, logger=None, log_level="DEBUG"):
    """
    Decorator to log the decorated function execution time. See `log_timing_context` for more details.
    It can be used in several methods:
    ```
    @log_timing
    def foo():
        pass

    @log_timing(logger=my_logger)
    def foo():
        pass

    @log_timing(logger=my_logger, log_level='DEBUG')
    def foo():
        pass
    ```

    :param func: function to decorate
    :param logger: logger to use, or None if using the default logger
    :param log_level: str log level to use [TRACE|DEBUG|INFO|...]
    """
    def decorate(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            with log_timing_context("function {!r}".format(f.func_name), logger=logger, log_level=log_level):
                return f(*args, **kwargs)
        return wrapped
    if func is None:
        return decorate
    else:
        return decorate(func)
