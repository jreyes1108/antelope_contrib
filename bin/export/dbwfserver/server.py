from __main__ import *

for port,db  in config.run_server.items():

    #reverseProxy = proxy.ReverseProxyResource('localhost',int(port),'/test/path/')
    #root = vhost.NameVirtualHost()
    #root. addHost( 'localhost', reverseProxy)

    root = resource.QueryParser(db,config)

    root.putChild('static', static.File(config.static_dir))

    #
    # favicon.ico
    #
    favicon = static.File(os.path.join(config.static_dir, 'images/favicon.ico'),
                                    defaultType='image/vnd.microsoft.icon')
    root.putChild('favicon.ico', favicon)

    site = server.Site(root)

    site.displayTracebacks = config.display_tracebacks

    application = service.Application(config.application_name)

    sc = service.IServiceCollection(application)

    sc.addService(internet.TCPServer(int(port), site))
