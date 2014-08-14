import time as t
import logbook

_time = t.time
_logger = logbook.Logger('infi.logging')
_threadlocal_factory = None


def set_time_func(f):
    """
    Allow user to set the time function used for time measurements. By default the time function is Python's standard
    library time.time(), but the user can choose a different one, for example by using infi.monotonic_time.
    :param f: a function that has no arguments and returns a float representing seconds
    """
    global _time
    _time = f


def get_time_func():
    global _time
    return _time


def get_time():
    global _time
    return _time()


def set_logger(l):
    """
    Allow user to set the logger used to log the time measurements. By default the logger is a local logger created.
    :param l: logbook.Logger object
    """
    global _logger
    _logger = l


def get_logger():
    global _logger
    return _logger


def get_threadlocal_factory():
    global _threadlocal_factory
    if _threadlocal_factory is None:
        try:
            import gevent
            _threadlocal_factory = gevent.local.local
        except ImportError:
            import threading
            _threadlocal_factory = threading.local
    return _threadlocal_factory


def set_threadlocal_factory(factory):
    global _threadlocal_factory
    _threadlocal_factory = factory


def new_threadlocal(*args, **kwargs):
    return get_threadlocal_factory()(*args, **kwargs)
