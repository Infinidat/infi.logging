from .plugins import get_formatter_plugins, _true


def create_formatter(plugin_names):
    """
    Creates a formatter that uses a list of plugin names.
    :param plugin_names: list of plugin names
    :returns: formatter function
    """
    available_formatters = get_formatter_plugins(lambda k: k in plugin_names)
    formatters = [available_formatters[k]() for k in plugin_names]
    format_string = " ".join("{}={}".format(f.get_format_key(), f.get_format_string()) for f in formatters)
    return create_formatter_by_format_string(format_string, plugin_names)


def create_formatter_by_format_string(format_string, plugin_names):
    """
    Creates a formatter that uses a given format string and a list of plugin names.
    The format string needs to have fields in place to format all the plugins.
    :param format_string: format string (e.g. "a={} b={}")
    :param plugin_names: list of plugin names
    :returns: formatter function
    """
    formatter_classes = get_formatter_plugins(lambda k: k in plugin_names)
    formatters = [formatter_classes[k]() for k in plugin_names]
    getters = [f.get_value for f in formatters]

    def formatter(record, handler):
        return format_string.format(*(g(record) for g in getters))
    return formatter


def create_default_formatter(plugin_predicate=_true):
    """
    Creates a default formatter that uses a custom format string.

    The full format string is:
    <time> <hostname> pid=<pid>:<pname> tid=<tid>:<gid> tag=<rid_tag> module=<channel> level=<log_level> [other plugins] msg=<message>

    The builder takes into account plugins the are disabled to generate a more compact output, for example if procname
    if empty:
    pid=<pid>

    Or if gevent is not available/disabled:
    tid=<tid>

    :param plugin_predicate: predicate over plugin names to choose which plugins to use.
    :returns: formatter function
    """
    available_formatters = dict((k, v()) for k, v in get_formatter_plugins(plugin_predicate).iteritems())

    strformats = []
    getters = []
    used_fields = set(['message'])  # we want message to be last

    def extend_format(str, *keys):
        used_fields.update(keys)
        getters.extend([available_formatters[f].get_value for f in keys])
        strformats.append(str.format(*[available_formatters[f].get_format_string() for f in keys]))

    if 'time' in available_formatters:
        extend_format('{}', 'time')

    if 'hostname' in available_formatters:
        extend_format('{}', 'hostname')

    if 'process_id' in available_formatters and 'procname' in available_formatters:
        extend_format('pid={}:{}', 'process_id', 'procname')
    elif 'process_id' in available_formatters:
        extend_format('pid={}', 'process_id')
    elif 'procname' in available_formatters:
        extend_format('pname={}', 'procname')

    if 'thread_id' in available_formatters and 'greenlet_id' in available_formatters:
        extend_format('tid={}:{}', 'thread_id', 'greenlet_id')
    elif 'thread_id' in available_formatters:
        extend_format('tid={}', 'thread_id')
    elif 'greenlet_id' in available_formatters:
        extend_format('gid={}', 'greenlet_id')

    if 'request_id_tag' in available_formatters:
        extend_format('tag={}', 'request_id_tag')
    if 'channel' in available_formatters:
        extend_format('module={}', 'channel')  # for backward compatibility we call this module
    if 'log_level' in available_formatters:
        extend_format('level={}', 'log_level')

    for f in sorted(set(available_formatters.keys()) - used_fields):
        extend_format(available_formatters[f].get_format_key() + '={}', f)

    if 'message' in available_formatters:
        extend_format('msg={}', 'message')

    strformat = " ".join(strformats)

    def formatter(record, handler):
        return strformat.format(*(g(record) for g in getters))
    return formatter
