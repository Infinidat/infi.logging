from infi.unittest import TestCase
from infi.logging.win32 import *

class Win32TestCase(TestCase):
    def test_register_app(self):
        try:
            register_application("test_app", r"C:\none")
        finally:
            unregister_application("test_app")
