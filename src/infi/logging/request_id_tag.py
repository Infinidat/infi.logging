"""
Greenlet-friendly request ID tagging for log messages.
"""
import logbook
import gevent
import random
from infi.pyutils.decorators import wraps
from infi.pyutils.contexts import contextmanager


TAG_NAME = 'request_id'

_threadlocal = gevent.local.local()
_logger = logbook.Logger(__name__)


def get_tag():
    """
    :returns: current request ID tag for the current greenlet if exists or None if no request ID tag is set
    :rtype: str or None
    """
    global _threadlocal
    return getattr(_threadlocal, TAG_NAME, None)


def set_tag(tag):
    """
    Sets the request ID tag on the current greenlet.
    :param tag: tag string for the current request
    :type tag: str or None to clear the tag
    """
    global _threadlocal
    setattr(_threadlocal, TAG_NAME, tag)


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


def _inject_request_id_tag(record):
    """Logbook processor function that sets TAG_NAME attribute on the log record to the current tag (or None)"""
    tag = get_tag()
    if tag is not None:
        record.extra[TAG_NAME] = tag


@contextmanager
def _null_context():
    yield


def request_id_tag(func=None, tag=None):
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
    :returns: wrapped function
    """
    def decorate(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            prev_tag, new_tag = get_tag(), tag
            if new_tag is not None:
                set_tag(new_tag)
            elif prev_tag is None:
                new_tag = new_random_tag()
                set_tag(new_tag)

            # We create a logbook.Processor context only if we didn't have a previous tag, otherwise there must already
            # be a context in place somewhere down the call stack.
            with (logbook.Processor(_inject_request_id_tag).threadbound() if prev_tag is None else _null_context()):
                if prev_tag is None:
                    # Log this function since it's our first "tagged" entry to the greenlet
                    _logger.debug("setting new tag {} on greenlet {}".format(new_tag, f.__name__))
                try:
                    return f(*args, **kwargs)
                finally:
                    set_tag(prev_tag)

        return wrapped

    if func is None:
        return decorate
    else:
        return decorate(func)