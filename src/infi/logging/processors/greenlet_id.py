from gevent.thread import get_ident

GREENLET_ID_KEY = 'greenlet_id'


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
