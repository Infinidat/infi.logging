import re
from munch import Munch
from unittest import TestCase
from infi.logging.formatters import create_syslog_formatter


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


class CreateSyslogFormatterTestCase(TestCase):
    def test_default(self):
        f = create_syslog_formatter()
        record = RecordBuilder().fill().create()
        formatted = f(record, None)
        fields = re.split(r'\s+', formatted)
        self.assertEquals(fields, ['pid=00042:myproc', 'tid=00001:00001', 'tag=0000ffff', 'module=mychannel', 'level=DEBUG', 'msg=mymessage'])

    def test__no_procname(self):
        f = create_syslog_formatter(procname=False)
        record = RecordBuilder().fill().create()
        formatted = f(record, None)
        fields = re.split(r'\s+', formatted)
        self.assertEquals(fields, ['pid=00042', 'tid=00001:00001', 'tag=0000ffff', 'module=mychannel', 'level=DEBUG', 'msg=mymessage'])

    def test__no_greenlet_id(self):
        f = create_syslog_formatter(greenlet_id=False)
        record = RecordBuilder().fill().create()
        formatted = f(record, None)
        fields = re.split(r'\s+', formatted)
        self.assertEquals(fields, ['pid=00042:myproc', 'tid=00001', 'tag=0000ffff', 'module=mychannel', 'level=DEBUG', 'msg=mymessage'])

    def test__no_request_id(self):
        f = create_syslog_formatter(request_id_tag=False)
        record = RecordBuilder().fill().create()
        formatted = f(record, None)
        fields = re.split(r'\s+', formatted)
        self.assertEquals(fields, ['pid=00042:myproc', 'tid=00001:00001', 'module=mychannel', 'level=DEBUG', 'msg=mymessage'])
