from ctypes import *
from infi.registry import *

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

def register_application(app_name, message_file_path):
    """Registers an application as an event log source so it can later create events.
    
    app_name - Application name (use the same name later when registering the event source)
    message_file_path - resource DLL file path
    """
    # See http://msdn.microsoft.com/en-us/library/windows/desktop/aa363661%28v=VS.85%29.aspx
    value_factory = RegistryValueFactory()
    event_log = LocalComputer().local_machine['SYSTEM']['CurrentControlSet']['Services']['Eventlog']
    event_log['Application'][app_name] = None
    app_key = event_log['Application'][app_name]
    app_key.values_store['EventMessageFile'] = value_factory.by_value(message_file_path)
    app_key.values_store['TypesSupported'] = value_factory.by_value(7) # All severity types

def unregister_application(app_name):
    """Unregisters an application as a log source by removing it from the registry."""
    event_log = LocalComputer().local_machine['SYSTEM']['CurrentControlSet']['Services']['Eventlog']
    del event_log['Application'][app_name]

def register_event_source(app_name):
    handle = RegisterEventSourceW(None, unicode(app_name))
    if handle == 0:
        raise WinError()
    return handle

def deregister_event_source(handle):
    DeregisterEventSource(handle)

def report_event(handle, type, category, event_id, strings, raw_data):
    raw_data_len = 0 if raw_data is None else len(raw_data)
    strings_ptr = (c_wchar_p * len(strings))()
    for i in xrange(len(strings)):
        strings_ptr[i] = c_wchar_p(unicode(strings[i]))
    return ReportEventW(handle, type, category, event_id, None, len(strings), raw_data_len, strings_ptr, raw_data)
