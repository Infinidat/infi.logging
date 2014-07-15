from logbook import Handler, StringFormatterHandlerMixin, NOTSET, DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL
from ctypes import c_wchar_p, WinError, windll

from infi.registry import RegistryValueFactory, LocalComputer

RegisterEventSourceW = windll.advapi32.RegisterEventSourceW
DeregisterEventSource = windll.advapi32.DeregisterEventSource
ReportEventW = windll.advapi32.ReportEventW

# From http://msdn.microsoft.com/en-us/library/windows/desktop/aa363679%28v=VS.85%29.aspx
EVENTLOG_SUCCESS = 0x0000
EVENTLOG_AUDIT_FAILURE = 0x0010
EVENTLOG_AUDIT_SUCCESS = 0x0008
EVENTLOG_ERROR_TYPE = 0x0001
EVENTLOG_INFORMATION_TYPE = 0x0004
EVENTLOG_WARNING_TYPE = 0x0002


def register_application(app_name, message_file_path=None):
    """Registers an application as an event log source so it can later create events.

    :param app_name: Application name (use the same name later when registering the event source)
    :param message_file_path: resource DLL file path
    """
    # See http://msdn.microsoft.com/en-us/library/windows/desktop/aa363661%28v=VS.85%29.aspx

    if message_file_path is None:
        import sys
        from pkg_resources import resource_filename
        fname = "eventlog_amd64.dll" if sys.maxsize > (1 << 31) else "eventlog_x86.dll"
        message_file_path = resource_filename("infi.logging", fname)

    value_factory = RegistryValueFactory()
    event_log = LocalComputer().local_machine['SYSTEM']['CurrentControlSet']['Services']['Eventlog']
    event_log['Application'][app_name] = None
    app_key = event_log['Application'][app_name]
    app_key.values_store['EventMessageFile'] = value_factory.by_value(message_file_path)
    app_key.values_store['TypesSupported'] = value_factory.by_value(7)  # All severity types


def unregister_application(app_name):
    """Unregisters an application as a log source by removing it from the registry."""
    event_log = LocalComputer().local_machine['SYSTEM']['CurrentControlSet']['Services']['Eventlog']
    event_log['Application'].pop(app_name, None)


def register_event_source(app_name):
    """Registers an event source and returns an open handle. Raises WinError on error."""
    handle = RegisterEventSourceW(None, unicode(app_name))
    if handle == 0:
        raise WinError()
    return handle


def deregister_event_source(handle):
    """Closes an open event source handle."""
    DeregisterEventSource(handle)


def report_event(handle, type, category, event_id, strings, raw_data):
    """Reports an event to Windows event log. Raises WinError on error.

    :param handle: handle to an open event source, previously opened with register_event_source
    :param type: event type: one of the EVENTLOG_xxxx constants
    :param category: category to use (number). If using our resource DLL, leave this as 0.
    :param event_id: event ID to use (number).
    :param strings: a list of strings that will be formatted as the event message. IF using our resource DLL, only a single
                    string is supported.
    :param raw_data: a blob (string)
    """
    # See http://msdn.microsoft.com/en-us/library/windows/desktop/aa363679%28v=VS.85%29.aspx
    raw_data_len = 0 if raw_data is None else len(raw_data)
    strings_ptr = (c_wchar_p * len(strings))()
    for i in xrange(len(strings)):
        strings_ptr[i] = c_wchar_p(unicode(strings[i]))
    result = ReportEventW(handle, type, category, event_id, None, len(strings), raw_data_len, strings_ptr, raw_data)
    if result != 1:
        raise WinError()


class Win32EventLogHandler(Handler, StringFormatterHandlerMixin):
    default_format_string = "{record.message}"

    def __init__(self, application_name, level=NOTSET, format_string=None, filter=None, bubble=False):
        Handler.__init__(self, level, filter, bubble)
        StringFormatterHandlerMixin.__init__(self, format_string)

        self._application_name = application_name
        self._default_type = EVENTLOG_INFORMATION_TYPE
        self._type_map = {
            DEBUG:      EVENTLOG_INFORMATION_TYPE,
            INFO:       EVENTLOG_INFORMATION_TYPE,
            NOTICE:     EVENTLOG_INFORMATION_TYPE,
            WARNING:    EVENTLOG_WARNING_TYPE,
            ERROR:      EVENTLOG_ERROR_TYPE,
            CRITICAL:   EVENTLOG_ERROR_TYPE
        }
        self._win32_handle = register_event_source(self._application_name)

    def close(self):
        if self._win32_handle != 0:
            deregister_event_source(self._win32_handle)
            self._win32_handle = 0

    def get_message_id(self, record):
        for dic in (record.extra, record.kwargs):
            id = dic.get('eventid', 0)
            if id != 0:
                return id

        # TODO: warn on debug that we have no id for this event.
        return 0

    def get_event_category(self, record):
        for dic in (record.extra, record.kwargs):
            category = dic.get('eventcategory', 0)
            if category != 0:
                return category
        return 0

    def get_event_type(self, record):
        return self._type_map.get(record.level, self._default_type)

    def get_raw_data(self, record):
        for dic in (record.extra, record.kwargs):
            raw_data = dic.get('raw_data', None)
            if raw_data is not None:
                return raw_data
        return None

    def emit(self, record):
        id = self.get_message_id(record)
        cat = self.get_event_category(record)
        type = self.get_event_type(record)
        message = self.format(record)
        raw_data = self.get_raw_data(record)
        report_event(self._win32_handle, type, cat, id, [message], raw_data)
