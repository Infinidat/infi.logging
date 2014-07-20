import gevent
from logging_test_case import LoggingTestCase
from infi.logging.dependencies import set_time_func
from infi.logging.timing import (log_timing_context, log_timing, enable_slow_greenlet_log_warning,
                                 disable_slow_greenlet_log_warning)


class TimingTestCase(LoggingTestCase):
    def tearDown(self):
        import time
        set_time_func(time.time)
        disable_slow_greenlet_log_warning()

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

    def test_slow_greenlet_log_warning(self):
        enable_slow_greenlet_log_warning(0.1)

        def slow_greenlet():
            import time
            time.sleep(0.5)
        g = gevent.spawn(slow_greenlet)
        g.join()
        self.assert_any_log_record(lambda r: 'was running for at least' in r.msg)

    def test_slow_greenlet_log_warning__dont_warn_about_gevent_hub_blocking(self):
        enable_slow_greenlet_log_warning(0.1)
        gevent.sleep(0.5)
        self.assert_no_log_record(lambda r: 'was running for at least' in r.msg)
