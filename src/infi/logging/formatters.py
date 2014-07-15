from socket import gethostname
from .request_id_tag import TAG_NAME

MODULU = 32768


def file_formatter(record, handler):
    hostname = gethostname()
    result = "{:%Y-%m-%d %H:%M:%S} {} ".format(record.time, hostname) + syslog_formatter(record, handler)
    return result


def syslog_formatter(record, handler):
    strformat = "pid={:0>5}:{: <28} tid={:0>5}:{:0>5} tag={:0>8} module={: <40} level={: <7} msg={}"
    procname = record.extra.get('procname', '[izbox]')
    greenlet_id = record.extra.get('greenlet_id', -1)
    thread_id = record.extra.get('thread_id', record.thread)
    tag = record.extra.get(TAG_NAME, 0)
    trace = record.extra.get("trace", False)
    formatted_exception = record.formatted_exception
    exc_msg = '' if formatted_exception is None else '\n' + formatted_exception
    formatted = strformat.format(record.process, procname,
                                 thread_id % MODULU, greenlet_id % MODULU,
                                 tag, record.channel, "TRACE" if trace else record.level_name, record.message + exc_msg)
    return formatted
