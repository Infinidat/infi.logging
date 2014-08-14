import pkg_resources

FORMATTER_PLUGIN_ENTRYPOINT = 'infi_logging_formatter_plugins'
INJECTOR_PLUGIN_ENTRYPOINT = 'infi_logging_injector_plugins'

_formatter_plugins = None
_injector_plugins = None


class InjectorPlugin(object):
    def inject(self, record):
        raise NotImplementedError()  # subclass must override this method


class FormatterPlugin(object):
    def get_value(self, record):
        raise NotImplementedError()  # subclass must override this method

    def get_format_string(self):
        raise NotImplementedError()  # subclass must override this method

    def get_format_key(self):
        raise NotImplementedError()  # subclass must override this method


def _true(name):
    return True


def load_plugins_by_entry_point(entry_point_key, predicate=_true, strict=False):
    plugins = dict()
    for entrypoint in pkg_resources.iter_entry_points(entry_point_key):
        if predicate(entrypoint.name):
            try:
                plugins[entrypoint.name] = entrypoint.load()
            except ImportError:
                if strict:
                    raise
    return plugins


def load_formatter_plugins(predicate=_true, strict=False):
    global _formatter_plugins
    if _formatter_plugins is None:
        _formatter_plugins = load_plugins_by_entry_point(FORMATTER_PLUGIN_ENTRYPOINT, predicate, strict)
    return _formatter_plugins


def load_injector_plugins(predicate=_true, strict=False):
    global _injector_plugins
    if _injector_plugins is None:
        _injector_plugins = load_plugins_by_entry_point(INJECTOR_PLUGIN_ENTRYPOINT, predicate, strict)
    return _injector_plugins


def get_injector_plugins(predicate=_true):
    plugins = load_injector_plugins()
    return dict((k, v) for k, v in plugins.iteritems() if predicate(k))


def get_formatter_plugins(predicate=_true):
    plugins = load_formatter_plugins()
    return dict((k, v) for k, v in plugins.iteritems() if predicate(k))


def clear_formatter_plugins():
    global _formatter_plugins
    _formatter_plugins = None


def clear_injector_plugins():
    global _injector_plugins
    _injector_plugins = None


def clear_plugins():
    clear_formatter_plugins()
    clear_injector_plugins()
