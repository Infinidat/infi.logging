from infi.logging.plugins import InjectorPlugin, FormatterPlugin
from thread import get_ident

THREAD_ID_KEY = 'thread_id'
THREAD_ID_MODULU = 32768


def get_thread_id_from_record(record):
    """
    :param record: logbook record
    :returns: current thread ID from record
    """
    return record.extra.get(THREAD_ID_KEY, record.thread)


def inject_thread_id(record):
    """
    Sets the current thread ID on `record.extra`.
    :param record: logbook record
    """
    record.extra[THREAD_ID_KEY] = get_ident()


class ThreadIDInjectorPlugin(InjectorPlugin):
    def inject(self, record):
        return inject_thread_id(record)


class ThreadIDFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_thread_id_from_record(record) % THREAD_ID_MODULU

    def get_format_string(self):
        return "{:0>5}"

    def get_format_key(self):
        return "thread_id"
