#!/usr/bin/env python

SEVERITY_NAMES = """
SeverityNames=(Success=0x0:STATUS_SEVERITY_SUCCESS
               Informational=0x1:STATUS_SEVERITY_INFORMATIONAL
               Warning=0x2:STATUS_SEVERITY_WARNING
               Error=0x3:STATUS_SEVERITY_ERROR
              )
"""

print(SEVERITY_NAMES)
print("MessageIdTypedef=WORD")

message_id = 1
for severity in ('Success', 'Informational', 'Warning', 'Error'):
    for i in xrange(0, 256):
        print("MessageId=0x%x" % message_id)
        print("Language=English")
        print("Severity=%s" % severity)
        message_id += 1
        print("%1")
        print(".")
        print("")
