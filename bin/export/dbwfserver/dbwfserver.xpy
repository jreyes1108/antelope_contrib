import re
import os
import sys
import getopt
import socket
import platform
import pprint
from string import Template
from collections import defaultdict 
from time import gmtime, strftime, sleep


def system_print():
#{{{
    #
    #Print system info in case of errors
    #
    print
    print 'uname:', platform.uname()
    print
    print 'Version      :', sys.version_info
    print 'Version      :', platform.python_version()
    print 'Compiler     :', platform.python_compiler()
    print 'Build        :', platform.python_build()
    print
    print 'system   :', platform.system()
    print 'node     :', platform.node()
    print 'release  :', platform.release()
    print 'version  :', platform.version()
    print 'machine  :', platform.machine()
    print 'processor:', platform.processor()
#}}}

def missing_twisted():
#{{{
    #
    #Print instructions to install Twisted.
    #
    v       = platform.python_version()
    v_major = sys.version_info[0]
    v_minor = sys.version_info[1]
    print 
    print 'Faile resolving dependence on module "Twuisted" Ver:10.1.0 or newer.'
    print 'Try:'
    print '*******************************************'
    print '\tsudo easy_install -U Twisted'
    print '*******************************************'
    print '\tIf you get this message after successfully'
    print '\trunning easy_install, then try a version '
    print '\tspecific easy_install command.'
    print '\tFor this installation [%s]...' % v
    print '\t"sudo easy_install-%s.%s -U Twisted".'% (v_major,v_minor)
    print '\tThis version should match the version'
    print '\tused to configure the Python Interface to Antelope.'
    print  
#}}}

def runApp(config):
    UnixApplicationRunner(config).run()

def run_reactor():

    id = os.getpid()

    if os.path.isdir('./state'):
        path = './state'
    else:
        path = '/tmp'

    ServerOptions.optParameters[1] = ['pidfile','',path+'/dbwfserver_'+str(id)+'.pid','Name of the pidfile']
    app.run(runApp, ServerOptions)


#
#Try to import Antelope's Python Interface.
#
try:
    import antelope.stock as stock
    import antelope.datascope as datascope
except Exception,e:
    print "Problem loading Antelope's Python libraries. (%s)" % e
    sys.exit()

try:
    from twisted.python import log
    from twisted.scripts.twistd import run
    from twisted.internet import reactor, defer, threads
    from twisted.internet.task import LoopingCall
    from twisted.application import app, service, internet
    from twisted.internet.threads import deferToThread
    from twisted.web import resource, server, static, rewrite
except Exception,e:
    system_print()
    print "Problem loading Twisted-Python libraries. (%s)" % e
    print "Force update with 'sudo easy_install -U Twisted'"
    missing_twisted()
    sys.exit()

#
#Import Python module JSON or SimpleJSON to 
#parse returned results from queries
#bsed on Python version test
#
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

try:
    import dbwfserver.risp as risp 
except Exception,e:
    print "Problem loading dbwfserver's RISP module from contrib code. (%s)" % e
    sys.exit()

try:
    import dbwfserver.config as config
except Exception,e:
    print "Problem loading dbwfserver's CONFIG module from contrib code. (%s)" % e
    sys.exit()

#
#Configure system with command-line flags and pf file values.
#
sys.argv = config.configure()

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

#
# Run the reactor now
#
try:
    from twisted.scripts._twistd_unix import ServerOptions, UnixApplicationRunner 
except:
    run()
else:
    run_reactor()
