"""
Slow greenlet logging utility
"""
import gevent
import greenlet
from functools import partial

from .globals import get_time, get_logger

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
