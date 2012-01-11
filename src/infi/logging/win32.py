from ctypes import *
from infi.registry import *

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
