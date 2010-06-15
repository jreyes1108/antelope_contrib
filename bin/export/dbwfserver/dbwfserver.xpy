import os

import sys

from twisted.python import log 

from twisted.scripts.twistd import run

import dbwfserver.config as config



#log.startLogging(stdout)
log.msg('Starting dbwfserver...')

sys.argv = config.configure(sys.argv)

run()
