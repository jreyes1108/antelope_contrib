import sys
from twisted.python import log
from twisted.web import server, static, rewrite
from twisted.application import service, internet

import dbwfserver.config as config
import dbwfserver.resource as resource


log.startLogging(sys.stdout)


application = service.Application(config.application_name)

sc = service.IServiceCollection(application)

for port,db  in config.run_servers.items():

    log.msg('Now with db:'+str(db)+' and port:'+ str(port) )

    root = resource.QueryParser(db)

    root.putChild('static',   static.File(config.static_dir))

    rewrite_root = rewrite.RewriterResource(root)

    site = server.Site(rewrite_root)

    site.displayTracebacks = config.display_tracebacks

    sc.addService(internet.TCPServer(int(port), site))
