import os
import sys
from twisted.python import log 


log.startLogging(sys.stdout)

from twisted.scripts.twistd import run

import dbwfserver.config as config


sys.argv = config.configure(sys.argv)

run()
