try:
    import gevent as ge
    has_gevent = True
except:
    has_gevent = False

try:
    import infi.tracing
    has_infi_tracing = True
except:
    has_infi_tracing = False

try:
    import setproctitle as sp
    has_setproctitle = True
except:
    has_setproctitle = False


import time as t
import logbook

_time = t.time
_logger = logbook.Logger('infi.logging')


_use_gevent = has_gevent
_use_syslog = has_infi_tracing
_use_procname = has_setproctitle
_use_infi_tracing = has_infi_tracing
_use_setproctitle = has_setproctitle

USE_DEFAULT = type('UseDefault', (object,), {})()  # singleton object


def set_dependencies(gevent=has_gevent, syslog=has_infi_tracing, procname=has_setproctitle,
                     infi_tracing=has_infi_tracing, setproctitle=has_setproctitle,
                     _time=None, _logger=None):
    """
    Explicitly set which optional dependencies to use and the default settings - gevent, syslog, procname,
    infi.tracing and setproctitle.

    :param gevent: if True, use gevent and log greenlets
    :param syslog: if True, enable syslog by default
    :param procname: if True, enable procname by default
    :param infi_tracing: if True, use infi.tracing
    :param setproctitle: if True, use setproctitle
    """
    global _use_gevent, _use_syslog, _use_procname, _use_infi_tracing, _use_setproctitle, time, logger
    if syslog and not infi_tracing:
        raise ValueError("cannot use syslog without infi.tracing, please install infi.tracing")
    _use_gevent = gevent
    _use_syslog = syslog
    _use_procname = procname
    _use_infi_tracing = infi_tracing
    _use_setproctitle = setproctitle
    if _time is not None:
        set_time_func(_time)
    if _logger is not None:
        set_logger(_logger)


def should_use_feature(feature, has_feature):
    if feature == USE_DEFAULT and has_feature:
        return True
    return bool(feature)


def should_use_gevent(flag=USE_DEFAULT):
    global _use_gevent
    return should_use_feature(flag, _use_gevent)


def should_use_procname(flag=USE_DEFAULT):
    global _use_procname
    return should_use_feature(flag, _use_procname)


def should_use_syslog(flag=USE_DEFAULT):
    global _use_syslog
    return should_use_feature(flag, _use_syslog)


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
