from infi.pyutils.decorators import wraps
from infi.pyutils.contexts import contextmanager
from .dependencies import get_time, get_logger, has_gevent


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


if has_gevent:
    import gevent
    import greenlet
    from functools import partial

    _slow_greenlet_max_duration = 1.0
    _last_switch_time = None

    def _switch_time_tracer(logger, what, (origin, target)):
        global _slow_greenlet_max_duration, _last_switch_time
        now = get_time()
        if _last_switch_time and origin != gevent.get_hub():  # gevent.hub can block for as long as it wants
            duration = now - _last_switch_time
            if duration >= _slow_greenlet_max_duration:
                msg = "greenlet id {} was running for at least {:.4f} seconds"
                logger.warn(msg.format(id(origin), duration))
        _last_switch_time = now

    def enable_slow_greenlet_log_warning(max_duration=1.0, logger=None):
        """
        Enables warnings about slow greenlet written to the log
        :param max_duration: maximum duration in seconds afterwhich a greenlet is considered slow
        :param logger: logger to use, or None if using the default logger
        """
        global _slow_greenlet_max_duration, _last_switch_time, _logger
        if logger is None:
            logger = get_logger()
        now = get_time()
        _slow_greenlet_max_duration = max_duration
        _last_switch_time = now
        current_id = id(gevent.getcurrent())
        logger.debug("enabling logging of greenlet switching, current greenlet (main) is {}".format(current_id))
        greenlet.settrace(partial(_switch_time_tracer, logger))

    def disable_slow_greenlet_log_warning():
        """Disables the slow greenlet log warnings by removing the trace function from greenlet."""
        greenlet.settrace(None)
