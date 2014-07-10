try:
    import gevent
except:
    from unittest import SkipTest
    raise SkipTest("gevent not installed")

from infi.unittest import TestCase
from infi.logging.request_id_tag import get_tag, set_tag, request_id_tag, TAG_NAME


@request_id_tag
def return_tag_func():
    return get_tag()


@request_id_tag
def return_tag_func_2():
    return return_tag_func()


class RequestIDTagTestCase(TestCase):
    def setUp(self):
        from logbook import TestHandler
        self.log_handler = TestHandler()
        self.log_handler.push_application()

    def tearDown(self):
        self.log_handler.pop_application()
        set_tag(None)

    def test_tag_accessors(self):
        set_tag('hello')
        self.assertEquals('hello', get_tag())

        set_tag(None)
        self.assertEquals(None, get_tag())

        # Make sure the tag is greenlet-local:
        set_tag("hello")
        def new_greenlet():
            self.assertEquals(None, get_tag())
        g = gevent.spawn(new_greenlet)
        g.join()
        self.assertEquals("hello", get_tag())

    def test_random_tag(self):
        from infi.logging.request_id_tag import new_random_tag
        t1, t2 = new_random_tag(), new_random_tag()
        self.assertNotEquals(t1, t2)
        self.assertTrue(len(t1) > 0 and len(t2) > 0)

    def test_request_id_tag__new_processor(self):
        self.assertEquals(get_tag(), None)

        tag = return_tag_func()
        self.assertIsNotNone(tag)

        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: r.extra.get(TAG_NAME, None) == tag)

    def test_request_id_tag__log_only_first_tag_ctx(self):
        tag = return_tag_func_2()

        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: r.extra.get(TAG_NAME, None) == tag and 'return_tag_func_2' in r.msg)

    def test_request_id_tag__context_switch_new_tag(self):
        set_tag('boo')
        g = gevent.spawn(return_tag_func_2)
        g.join()
        tag = g.value
        self.assertNotEquals(tag, 'boo')

        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: r.extra.get(TAG_NAME, None) == tag and 'return_tag_func_2' in r.msg)

    def test_request_id_tag__context_switch_set_tag(self):
        set_tag('boo')
        def foo():
            return return_tag_func()
        g = gevent.spawn(request_id_tag(foo, tag='boo2'))
        g.join()
        self.assertEquals(g.value, 'boo2')
        self.assert_log_records_len(1)
        self.assert_any_log_record(lambda r: r.extra.get(TAG_NAME, None) == 'boo2' and 'foo' in r.msg)

    def test_decorate_tag_with_default(self):
        @request_id_tag(tag='boo')
        def foo():
            return get_tag()

        self.assertEquals(foo(), 'boo')

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