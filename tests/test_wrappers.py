import os
from unittest import TestCase
from logbook import Logger


class WrappersTestCase(TestCase):
    def test_default(self):
        from infi.logging.wrappers import script_logging_context
        with script_logging_context(logfile_path=os.devnull):
            boo = Logger("boo")
            boo.info("baah!")
