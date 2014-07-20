import logbook
from infi.tracing import SyslogWriter


class SyslogHandler(logbook.Handler, logbook.StringFormatterHandlerMixin):
    """Handler that uses infi.tracing's `SyslogWriter` to truly asynchronously write to syslog."""

    def __init__(self, facility, host_name="", application_name="python", process_id="", address=("127.0.0.1", 514),
                 level=logbook.NOTSET, format_string=None, filter=None, bubble=False,
                 syslog_buffer_size=1024, syslog_message_size=32768):
        logbook.Handler.__init__(self, level, filter, bubble)
        logbook.StringFormatterHandlerMixin.__init__(self, format_string)

        self.writer = SyslogWriter(syslog_buffer_size, syslog_message_size, facility=facility, address=address,
                                   host_name=host_name, application_name=application_name, process_id=process_id,
                                   rfc5424=True)
        self.writer.start()

    def emit(self, record):
        self.writer.write(logbook.SyslogHandler.level_priority_map.get(record.level,
                                                                       logbook.SyslogHandler.LOG_WARNING),
                          self.format(record))

    def close(self):
        self.writer.stop()
