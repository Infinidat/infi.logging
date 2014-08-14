import re
from munch import Munch
from unittest import TestCase, SkipTest
from infi.logging.formatters import create_default_formatter, create_formatter_by_format_string, create_formatter


class RecordBuilder(object):
    def __init__(self):
        self.record = Munch(process=None, formatted_exception=None, thread=None, extra=Munch(), channel=None,
                            level_name=None, message=None)

    def process(self, n=42, procname=None):
        self.record.process = n
        self.record.extra.procname = procname
        return self

    def thread(self, thread=1, thread_id=None, greenlet_id=None):
        self.record.thread = thread
        self.record.extra.thread_id = thread_id
        self.record.extra.greenlet_id = greenlet_id
        return self

    def channel(self, s):
        self.record.channel = s
        return self

    def level_name(self, s):
        self.record.level_name = s
        return self

    def request_id(self, s):
        self.record.extra.request_id = s
        return self

    def message(self, s):
        self.record.message = s
        return self

    def formatted_exception(self, s):
        self.record.formatted_exception = s
        return self

    def create(self):
        return self.record

    def fill(self):
        self.process(42, 'myproc') \
            .thread(1, 1, 1) \
            .channel('mychannel') \
            .level_name('DEBUG') \
            .request_id('ffff') \
            .message('mymessage') \
            .formatted_exception(None)
        return self


class CreateDefaultFormatterTestCase(TestCase):
    def test_default(self):
        enabled_plugins = set(('process_id', 'thread_id', 'request_id_tag', 'channel', 'log_level', 'message'))
        fields = self._default_format_and_split(RecordBuilder().fill().create(),
                                                plugin_predicate=enabled_plugins.__contains__)
        self.assertEquals(fields, ['pid=00042', 'tid=00001', 'tag=0000ffff', 'module=mychannel', 'level=DEBUG', 'msg=mymessage'])

    def test_default_with_gid(self):
        try:
            import gevent
        except ImportError:
            raise SkipTest("gevent not installed")
        enabled_plugins = set(('thread_id', 'greenlet_id'))
        fields = self._default_format_and_split(RecordBuilder().fill().create(),
                                                plugin_predicate=enabled_plugins.__contains__)
        self.assertEquals(fields[0], 'tid=00001:00001')

    def test_default_with_procname(self):
        enabled_plugins = set(('process_id', 'procname'))
        fields = self._default_format_and_split(RecordBuilder().fill().create(),
                                                plugin_predicate=enabled_plugins.__contains__)
        self.assertEquals(fields[0], 'pid=00042:myproc')

    def _default_format_and_split(self, record, plugin_predicate=lambda p: True):
        return self._format_record_and_split(create_default_formatter(plugin_predicate), record)

    def _format_record_and_split(self, formatter, record):
        formatted = formatter(record, None)
        return re.split(r'\s+', formatted)


class CreateFormatterTestCase(TestCase):
    def test_pid(self):
        formatter = create_formatter(['process_id'])
        record = RecordBuilder().fill().create()
        self.assertEquals(formatter(record, None), "process_id=00042")

    def test_pid_pname(self):
        formatter = create_formatter(['process_id', 'procname'])
        record = RecordBuilder().fill().create()
        self.assertEquals(formatter(record, None).strip(), "process_id=00042 procname=myproc")


class CreateFormatterByFormatStringTestCase(TestCase):
    def test_pid(self):
        formatter = create_formatter_by_format_string("myprocess={}", ['process_id'])
        record = RecordBuilder().fill().create()
        self.assertEquals(formatter(record, None), "myprocess=42")
