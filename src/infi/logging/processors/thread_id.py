from thread import get_ident

THREAD_ID_KEY = 'thread_id'


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
