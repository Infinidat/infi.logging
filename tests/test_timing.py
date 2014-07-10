from logging_test_case import LoggingTestCase
from infi.logging.timing import set_time_func, log_timing_context, log_timing


class TimingTestCase(LoggingTestCase):
    def test_log_timing_context(self):
        t = [1, 2]
        def time_f():
            return t.pop(0)
        set_time_func(time_f)
        with log_timing_context('my context'):
            pass
        self.assert_all_log_record(lambda r: 'my context' in r.msg)
        self.assert_any_log_record(lambda r: 'time taken: 1.0000 seconds' in r.msg)

    def test_log_timing(self):
        t = [1, 2]
        def time_f():
            return t.pop(0)
        @log_timing
        def foo():
            pass
        set_time_func(time_f)
        foo()
        self.assert_all_log_record(lambda r: 'foo' in r.msg)
        self.assert_any_log_record(lambda r: 'time taken: 1.0000 seconds' in r.msg)
