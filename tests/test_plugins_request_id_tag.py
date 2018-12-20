try:
    import gevent
except:
    from unittest import SkipTest
    raise SkipTest("gevent not installed")

from logging_test_case import LoggingTestCase
from infi.logging.plugins.request_id_tag import get_tag, set_tag, request_id_tag, get_request_id_tag_from_record


@request_id_tag
def return_tag_func():
    return get_tag()


@request_id_tag
def return_tag_func_2():
    return return_tag_func()


class RequestIDTagTestCase(LoggingTestCase):
    def tearDown(self):
        super(RequestIDTagTestCase, self).tearDown()
        set_tag(None)

    def test_tag_accessors(self):
        set_tag('hello')
        self.assertEqual('hello', get_tag())

        set_tag(None)
        self.assertEqual(None, get_tag())

        # Make sure the tag is greenlet-local:
        set_tag("hello")

        def new_greenlet():
            self.assertEqual(None, get_tag())
        g = gevent.spawn(new_greenlet)
        g.join()
        self.assertEqual("hello", get_tag())

    def test_random_tag(self):
        from infi.logging.plugins.request_id_tag import new_random_tag
        t1, t2 = new_random_tag(), new_random_tag()
        self.assertNotEqual(t1, t2)
        self.assertTrue(len(t1) > 0 and len(t2) > 0)

    def test_request_id_tag__new_processor(self):
        self.assertEqual(get_tag(), None)

        tag = return_tag_func()
        self.assertIsNotNone(tag)

        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: get_request_id_tag_from_record(r) == tag)

    def test_request_id_tag__log_only_first_tag_ctx(self):
        tag = return_tag_func_2()

        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: get_request_id_tag_from_record(r) == tag and 'return_tag_func_2' in r.msg)

    def test_request_id_tag__context_switch_new_tag(self):
        set_tag('boo')
        g = gevent.spawn(return_tag_func_2)
        g.join()
        tag = g.value
        self.assertNotEqual(tag, 'boo')

        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: get_request_id_tag_from_record(r) == tag and 'return_tag_func_2' in r.msg)

    def test_request_id_tag__context_switch_set_tag(self):
        set_tag('boo')

        def foo():
            return return_tag_func()
        g = gevent.spawn(request_id_tag(foo, tag='boo2'))
        g.join()
        self.assertEqual(g.value, 'boo2')
        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: get_request_id_tag_from_record(r) == 'boo2' and 'foo' in r.msg)

    def test_decorate_tag_with_default(self):
        @request_id_tag(tag='boo')
        def foo():
            return get_tag()

        self.assertEqual(foo(), 'boo')
