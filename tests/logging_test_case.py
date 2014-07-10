from infi.unittest import TestCase


class LoggingTestCase(TestCase):
    def setUp(self):
        super(LoggingTestCase, self).setUp()
        from logbook import TestHandler
        self.log_handler = TestHandler()
        self.log_handler.push_application()

    def tearDown(self):
        super(LoggingTestCase, self).tearDown()
        self.log_handler.pop_application()

    def assert_log_records_len(self, n):
        self.assertEquals(len(self.log_handler.records), n)

    def assert_any_log_record(self, pred):
        self.assertTrue(any(pred(o) for o in self.log_handler.records),
                        "any_log_record({!r}) is False, log records: {!r}".format(pred, self.dump_log_records()))

    def assert_all_log_record(self, pred):
        self.assertTrue(all(pred(o) for o in self.log_handler.records),
                        "all_log_record({!r}) is False, log records: {!r}".format(pred, self.dump_log_records()))

    def dump_log_records(self):
        return [r.to_dict() for r in self.log_handler.records]