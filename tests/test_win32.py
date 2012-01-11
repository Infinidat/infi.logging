from infi.unittest import TestCase
from infi.logging.win32 import *

class Win32TestCase(TestCase):
    def test_register_app(self):
        try:
            register_application("test_app", self._message_file_path())
        finally:
            unregister_application("test_app")

    def test_register_event_source(self):
        try:
            register_application("test_app", self._message_file_path())
            handle = register_event_source("test_app")
            self.assertNotEqual(handle, 0)
        finally:
            unregister_application("test_app")

    def test_report_event(self):
        try:
            register_application("test_app", self._message_file_path())
            handle = register_event_source("test_app")
            result = report_event(handle, EVENTLOG_SUCCESS, 0, 0, [ "testing 123" ], None)
            print(result)
        finally:
            deregister_event_source(handle)
            unregister_application("test_app")

    def _message_file_path(self):
        from os import path
        import sys

        assets_dir = path.abspath(path.join(path.dirname(__file__), "..", "assets"))
        arch = "amd64" if sys.maxsize > (1 << 31) else "x86"
        return path.join(assets_dir, arch, "messages.dll")
