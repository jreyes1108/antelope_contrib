from twisted.web import server, static, rewrite
from twisted.application import service, internet

import dbwfserver.config as config
import dbwfserver.resource as resource


for port,db  in config.run_servers.items():

    print 'Now with db:'+str(db)+' and port:'+ str(port)

    root = resource.QueryParser(db)

    root.putChild('static',   static.File(config.static_dir))

    rewrite_root = rewrite.RewriterResource(root)

    site = server.Site(rewrite_root)

    site.displayTracebacks = config.display_tracebacks

    application = service.Application(config.application_name+' '+str(port))

    internet.TCPServer(int(port), site).setServiceParent(application)
