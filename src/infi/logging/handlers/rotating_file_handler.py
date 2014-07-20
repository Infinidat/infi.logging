import logbook
from logbook.handlers import rename, sys, errno


class RotatingFileHandler(logbook.RotatingFileHandler):
    """Similar to logbook's `RotatingFileHandler`, but the backup files use leading zeros in the suffix so it'll be
    easier to sort when listing files (e.g. x.01, x.02 and not x.1, x.2)."""
    def perform_rollover(self):
        # Code here is almost the same as the base class's perform_rollover except for the src and dst formatting.
        self.stream.close()
        for x in xrange(self.backup_count - 1, 0, -1):
            src = '{}.{:02}'.format(self._filename, x)
            dst = '{}.{:02}'.format(self._filename, x + 1)
            try:
                rename(src, dst)
            except OSError:
                e = sys.exc_info()[1]
                if e.errno != errno.ENOENT:
                    raise
        rename(self._filename, self._filename + '.01')
        self._open('w')
