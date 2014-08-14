from infi.logging.plugins import FormatterPlugin


def get_time_from_record(record):
    """
    :param record: logbook record
    :returns: time from record
    """
    return record.time


class TimeFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_time_from_record(record)

    def get_format_string(self):
        return "{:%Y-%m-%d %H:%M:%S}"

    def get_format_key(self):
        return "time"
