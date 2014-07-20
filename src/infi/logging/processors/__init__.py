from infi.logging.dependencies import has_gevent, USE_DEFAULT, should_use_procname, should_use_gevent

from .procname import get_procname_from_record, get_procname, set_procname, refresh_procname_if_none, inject_procname
from .thread_id import get_thread_id_from_record, inject_thread_id

__all__ = ['inject_procname', 'get_procname_from_record', 'get_procname', 'set_procname', 'refresh_procname_if_none'
           'inject_thread_id', 'get_thread_id_from_record']

if has_gevent:
    from .greenlet_id import inject_greenlet_id, get_greenlet_id_from_record
    __all__.extend(['inject_greenlet_id', 'get_greenlet_id_from_record'])


def create_inject_extra_data(procname=USE_DEFAULT, thread_id=True, greenlet_id=USE_DEFAULT):
    """
    Composes a set of inject data methods into a single one based on the flags passed.
    :param procname: if True, injects procname to the record
    :param thread_id: if True, injects thread ID to the record
    :param greenlet_id: if True, injects greenlet ID to the record
    :returns: function(record: logbook record)
    """
    injectors = []
    if should_use_procname(procname):
        injectors.append(inject_procname)
    if thread_id:
        injectors.append(inject_thread_id)
    if should_use_gevent(greenlet_id):
        injectors.append(inject_greenlet_id)

    def inject_extra_data(record):
        """Wrapper that injects procname, thread ID and greenlet ID (if gevent installed)"""
        for inject in injectors:
            inject(record)
    return inject_extra_data
