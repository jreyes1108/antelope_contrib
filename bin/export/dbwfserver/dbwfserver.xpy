import re
import os
import sys
import getopt
from string import Template
from time import gmtime, strftime
from collections import defaultdict 

try:
    import antelope.stock as stock
    import antelope.datascope as datascope
except Exception,e:
    print "Problem loading Antelope's Python libraries. (%s)" % e
    sys.exit()

try:
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.scripts.twistd import run      #The Twisted Daemon: platform-independent interface.
    from twisted.application import service, internet
    from twisted.web import resource, server, static, rewrite
except Exception,e:
    print "Problem loading Twisted-Python libraries. (%s)" % e
    sys.exit()



if(float(sys.version_info[0])+float(sys.version_info[1])/10 >= 2.6):

    try:
        import json
    except Exception,e:
        print "Problem loading Python's json library. (%s)" % e
        sys.exit()

else:

    try:
        import simplejson as json
    except Exception,e:
        print "Problem loading Python's simplejson library. (%s)" % e
        sys.exit()


# 
# Init logging
#
#log.startLogging(sys.stdout)
#log.msg('Starting dbwfserver...')

try:
    import dbwfserver.config as config
except Exception,e:
    print "Problem loading dbwfserver's CONFIG module from contrib code. (%s)" % e
    sys.exit()


sys.argv = config.configure(sys.argv)

try:
    import dbwfserver.dbcentral as dbcentral 
except Exception,e:
    print "Problem loading dbwfserver's DBCENTRAL module from contrib code. (%s)" % e
    sys.exit()

try:
    import dbwfserver.eventdata as evdata 
except Exception,e:
    print "Problem loading dbwfserver's EVDATA module from contrib code. (%s)" % e
    sys.exit()

try:
    import dbwfserver.resource as resource
except Exception,e:
    print "Problem loading dbwfserver's RESOURCE module from contrib code. (%s)" % e
    sys.exit()

run()
