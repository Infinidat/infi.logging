import logbook
from unittest import TestCase
from infi.logging.handlers import RotatingFileHandler


class RotatingFileHandlerTestCase(TestCase):
    def test_rotation(self):
        from tempfile import mktemp
        from glob import glob
        name = mktemp(prefix='rotating_file_handler_test', suffix='.log')
        h = RotatingFileHandler(name, max_size=16, format_string="{record.message}\n", backup_count=5)

        def glob_log():
            return glob("{}*".format(name))
        with h.applicationbound():
            logbook.info("0132456789012345")
            self.assertEquals(2, len(glob_log()))
            logbook.info("0132456789012345")
            self.assertEquals(3, len(glob_log()))
            logbook.info("0132456789012345")
            self.assertEquals(4, len(glob_log()))
            logbook.info("0132456789012345")
            self.assertEquals(5, len(glob_log()))
            self.assertEquals(set([name] + ["{}.{:02d}".format(name, i) for i in range(1, 5)]), set(glob_log()))
