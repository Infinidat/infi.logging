from infi.logging.plugins import FormatterPlugin


class ProcessIDFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return record.process

    def get_format_string(self):
        return "{:0>5}"

    def get_format_key(self):
        return "process_id"
