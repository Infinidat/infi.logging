from logging_test_case import LoggingTestCase
from infi.logging.plugins import clear_plugins, load_formatter_plugins, load_injector_plugins


class PluginsTestCase(LoggingTestCase):
    def setUp(self):
        super(PluginsTestCase, self).setUp()
        clear_plugins()

    def test_load_formatter_plugins__default_plugins_no_predicate(self):
        plugins = load_formatter_plugins().keys()
        self.assertTrue(set(('message', 'log_level', 'channel', 'process_id', 'thread_id')) & set(plugins))

    def test_load_formatter_plugins__predicate(self):
        plugins = load_formatter_plugins(lambda p: p != 'log_level').keys()
        self.assertNotIn('log_level', plugins)

    def test_load_injector_plugins__default_plugins_no_predicate(self):
        plugins = load_injector_plugins().keys()
        self.assertIn('thread_id', plugins)

    def test_load_injector_plugins__predicate(self):
        plugins = load_injector_plugins(lambda p: p != 'thread_id').keys()
        self.assertNotIn('thread_id', plugins)
