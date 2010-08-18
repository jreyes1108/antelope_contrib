from __main__ import *

application = service.Application(config.application_name)

sc = service.IServiceCollection(application)

for port,db  in config.run_servers.items():

    root = resource.QueryParser(db)

    root.putChild('static',   static.File(config.static_dir))

    site = server.Site(root)

    site.displayTracebacks = config.display_tracebacks
    # if set, Twisted internal errors are displayed on rendered pages. Default to True.

    sc.addService(internet.TCPServer(int(port), site))
