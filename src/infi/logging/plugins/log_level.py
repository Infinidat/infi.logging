from infi.logging.plugins import FormatterPlugin


def get_log_level_name_from_record(record):
    """
    :param record: lobgook record
    :returns: record's log level name
    """
    return 'TRACE' if record.extra.get('TRACE', False) else record.level_name


class LogLevelFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_log_level_name_from_record(record)

    def get_format_string(self):
        return "{: <7}"

    def get_format_key(self):
        return "log_level"
