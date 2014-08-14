import logbook
from infi.logging.plugins import get_injector_plugins, _true


def create_inject_extra_data(plugin_predicate=_true):
    """
    Composes all the injector plugins and returns a data injection function.
    :param plugin_predicate: predicate that chooses which plugins to enable
    :returns: function(record: logbook record)
    """
    injectors = [injector() for injector in get_injector_plugins(plugin_predicate).values()]

    def inject_extra_data(record):
        """Wrapper that injects all the data available from the loaded injector plugins"""
        for injector in injectors:
            injector.inject(record)
    return inject_extra_data


def create_processor(plugin_predicate=_true):
    """
    Returns a new logbook Processor object that injects to each record's `extra` dict whatever the enabled plugins
    choose to put there.
    :param plugin_predicate: predicate that chooses which plugins to enable
    :returns: logbook.Processor object
    """
    return logbook.Processor(create_inject_extra_data(plugin_predicate))
