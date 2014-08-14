from infi.logging.plugins import InjectorPlugin, FormatterPlugin
from gevent.thread import get_ident

GREENLET_ID_KEY = 'greenlet_id'
GREENLET_ID_MODULU = 32768


def get_greenlet_id_from_record(record):
    """
    :param record: lobgook record
    :returns: greenlet ID of the logbook record or -1 if not set
    """
    return record.extra.get(GREENLET_ID_KEY, -1)


def inject_greenlet_id(record):
    """
    Sets the greenlet ID on `record.extra`.
    :param record: logbook record
    """
    record.extra[GREENLET_ID_KEY] = get_ident()


class GreenletIDInjectorPlugin(InjectorPlugin):
    def inject(self, record):
        return inject_greenlet_id(record)


class GreenletIDFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_greenlet_id_from_record(record) % GREENLET_ID_MODULU

    def get_format_string(self):
        return "{:0>5}"

    def get_format_key(self):
        return "greenlet_id"
