from infi.logging.plugins import FormatterPlugin


class MessageFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        if record.formatted_exception:
            return record.message + "\n" + record.formatted_exception
        else:
            return record.message

    def get_format_string(self):
        return "{}"

    def get_format_key(self):
        return "message"
