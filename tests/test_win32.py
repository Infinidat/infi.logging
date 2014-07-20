try:
    from ctypes import WinError
except:
    from unittest import SkipTest
    raise SkipTest("test module for win32 only")


from contextlib import contextmanager

from infi.unittest import TestCase
from infi.logging.win32 import *
from logbook import *

class Win32TestCase(TestCase):
    def test_register_app(self):
        with self._register_application():
            pass

    def test_register_event_source(self):
        with self._register_application():
            handle = register_event_source("test_app")
            self.assertNotEqual(handle, 0)
            deregister_event_source(handle)

    def test_report_event(self):
        with self._register_application_and_event_source() as handle:
            report_event(handle, EVENTLOG_SUCCESS, 0, 0, [ "testing 123" ], None)

    def test_report_event__two_strings(self):
        with self._register_application_and_event_source() as handle:
            report_event(handle, EVENTLOG_SUCCESS, 0, 0, [ "testing 123", "testing 321" ], None)

    def test_report_event__raw_data(self):
        with self._register_application_and_event_source() as handle:
            report_event(handle, EVENTLOG_SUCCESS, 0, 0, [ "testing 123" ], "this is a raw data")

    def test_win32_handler(self):
        with self._register_application():
            with Win32EventLogHandler("test_app").applicationbound():
                info("This is test_win32_handler")

    def test_win32_handler__eventid(self):
        with self._register_application():
            with Win32EventLogHandler("test_app").applicationbound():
                info("This is test_win32_handler__eventid id should be 1", eventid=1)

    def test_win32_handler__eventcategory(self):
        with self._register_application():
            with Win32EventLogHandler("test_app").applicationbound():
                info("This is test_win32_handler__eventcategory category should be 1", eventcategory=1)

    def test_win32_handler__raw_data(self):
        with self._register_application():
            with Win32EventLogHandler("test_app").applicationbound():
                info("This is test_win32_handler__raw_data should have raw data", raw_data="this is raw data")

    @contextmanager
    def _register_application_and_event_source(self):
        with self._register_application():
            handle = None
            try:
                handle = register_event_source("test_app")
                yield handle
            finally:
                if handle is not None:
                    deregister_event_source(handle)

    @contextmanager
    def _register_application(self):
        try:
            register_application("test_app", self._message_file_path())
            yield
        finally:
            unregister_application("test_app")

    def _message_file_path(self):
        import sys
        from pkg_resources import resource_filename
        fname = "eventlog_amd64.dll" if sys.maxsize > (1 << 31) else "eventlog_x86.dll"
        return resource_filename("infi.logging", fname)
