from infi.logging.plugins import FormatterPlugin


def get_channel_from_record(record):
    """
    :param record: lobgook record
    :returns: record's log module
    """
    return record.channel


class ChannelFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_channel_from_record(record)

    def get_format_string(self):
        return "{: <40}"

    def get_format_key(self):
        return "channel"
