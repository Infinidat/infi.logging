from infi.logging.plugins import InjectorPlugin, FormatterPlugin
from socket import gethostname

HOST_NAME_KEY = 'host_name'


def get_host_name_from_record(record):
    """
    :param record: logbook record
    :returns: current thread ID from record
    """
    return record.extra.get(HOST_NAME_KEY, '')


def inject_host_name(record):
    """
    Sets the current thread ID on `record.extra`.
    :param record: logbook record
    """
    record.extra[HOST_NAME_KEY] = gethostname()


class HostNameInjectorPlugin(InjectorPlugin):
    def inject(self, record):
        return inject_host_name(record)


class HostNameFormatterPlugin(FormatterPlugin):
    def get_value(self, record):
        return get_host_name_from_record(record)

    def get_format_string(self):
        return "{}"

    def get_format_key(self):
        return "hostname"
