"""
Greenlet/thread-friendly request ID tagging for log messages.
"""
import logbook
import random
from infi.pyutils.decorators import wraps
from infi.pyutils.contexts import contextmanager

from infi.logging.plugins import InjectorPlugin, FormatterPlugin
from infi.logging.globals import new_threadlocal, get_logger


REQUEST_ID_TAG_KEY = 'request_id'
_threadlocal = None


def _get_threadlocal():
    global _threadlocal
    if _threadlocal is None:  # Lazy creation of threadlocal so user can configure which threadlocal to use
        _threadlocal = new_threadlocal()
    return _threadlocal


def get_tag():
    """
    :returns: current request ID tag for the current greenlet if exists or None if no request ID tag is set
    :rtype: str or None
    """
    return getattr(_get_threadlocal(), REQUEST_ID_TAG_KEY, None)


def set_tag(tag):
    """
    Sets the request ID tag on the current greenlet.
    :param tag: tag string for the current request
    :type tag: str or None to clear the tag
    """
    setattr(_get_threadlocal(), REQUEST_ID_TAG_KEY, tag)


def new_random_tag():
    """
    :returns: new random str (8 character random hex string)
    :rtype: str
    """
    return hex(random.getrandbits(32))[2:-1].zfill(8)


def set_random_tag():
    """
    Sets a new random tag on the current greenlet.
    """
    set_tag(new_random_tag())


def get_request_id_tag_from_record(record):
    """
    :returns: request ID tag set on the logbook record or None if not found
    :rtype: str or None
    """
    return record.extra.get(REQUEST_ID_TAG_KEY, '')


def inject_request_id_tag(record):
    """Logbook processor function that sets REQUEST_ID_TAG_KEY attribute on the log record to the current tag (or None)"""
    tag = get_tag()
    if tag is not None:
        record.extra[REQUEST_ID_TAG_KEY] = tag


@contextmanager
def _null_context():
    yield


@contextmanager
def request_id_tag_context(title=None, tag=None, logger=None):
    """
    Context that adds a request ID tag logging processor.

    :param title: title to write in the log when setting a new tag (if a previous tag was not set).
                  If ``None`` no log message will be generated.
    :param tag: tag to set before calling func. If tag is None and no existing tag is set a new random tag will be
                created.
    :param logger: logger to use, if None use default logger
    """
    if logger is None:
        logger = get_logger()

    prev_tag, new_tag = get_tag(), tag
    if new_tag is not None:
        set_tag(new_tag)
    elif prev_tag is None:
        new_tag = new_random_tag()
        set_tag(new_tag)

    # We create a logbook.Processor context only if we didn't have a previous tag, otherwise there must already
    # be a context in place somewhere down the call stack.
    with (logbook.Processor(inject_request_id_tag).greenletbound() if prev_tag is None else _null_context()):
        if prev_tag is None and title is not None:
            # Log this function since it's our first "tagged" entry to the greenlet
            logger.debug("setting new tag {} on greenlet {}".format(new_tag, title))
        try:
            yield
        finally:
            set_tag(prev_tag)


def request_id_tag(func=None, tag=None, logger=None):
    """
    Decorator that wraps func and adds a request ID tag logging processor that adds the request ID attribute to log
    records within the same greenlet.

    It can be used in several methods:
    ```
    @request_id_tag  # this will use existing tag on the greenlet or a new random tag
    def foo():
        some_logger.info("hi ya!")

    @request_id_tag(tag='hardcode')  # this will set the tag to 'hardcore' from hereon on this greenlet
    def foo():
        some_logger.info("hi ya!")

    wrapped_func = request_id_tag(foo, tag=get_tag())  # call explicitly so we can pass tag between greenlets
    gevent.spawn(wrapped_func)
    ```

    :param func: function to wrap
    :param tag: tag to set before calling func. If tag is None and no existing tag is set a new random tag will be
                created.
    :param logger: logger to use, if None use default logger
    :returns: wrapped function
    """
    def decorate(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            with request_id_tag_context(f.__name__, tag, logger):
                return f(*args, **kwargs)
        return wrapped

    if func is None:
        return decorate
    else:
        return decorate(func)


class RequestIDTagInjectorPlugin(InjectorPlugin):
    def inject(self, record):
        return inject_request_id_tag(record)


class RequestIDTagFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_request_id_tag_from_record(record)

    def get_format_string(self):
        return "{:0>8}"

    def get_format_key(self):
        return "request_id_tag"
