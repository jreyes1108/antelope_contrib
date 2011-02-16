from __main__ import *

global sys

def usage():

    print "Usage: dbwfserver [-dvV] [-n nickname] [-p pfname] [-P port] [dbname]\n"

def configure():

    global dbpointers
    global style
    global locked
    global pfname
    global application_name
    global application_title
    global static_dir
    global jquery_dir
    global template
    global plot_template
    global local_data
    global antelope
    global dbname
    global port
    global binning_threshold
    global canvas_size_default
    global apply_calib
    global display_tracebacks
    global display_arrivals
    global display_points
    global verbose
    global debug
    global daemonize
    global import_paths
    global default_chans
    global default_time_window
    global filters
    global run_server
    global nickname

    dbpointers          = []
    locked              = False
    pfname              = 'dbwfserver'
    style               = 'cupertino'
    nickname            = ''
    application_name    = ''
    application_title   = ''
    static_dir          = ''
    jquery_dir          = ''
    template            = ''
    plot_template       = ''
    local_data          = ''
    antelope            = ''
    dbname              = ''
    port                = -1
    binning_threshold   = -1
    canvas_size_default = -1
    apply_calib         = False
    display_tracebacks  = False
    display_arrivals    = True
    display_points      = False
    verbose             = False
    debug               = False
    daemonize           = False
    import_paths        = ()
    default_chans       = ()
    default_time_window = -1
    filters             = {}
    run_server          = {}

    try:

        opts, pargs = getopt.getopt(sys.argv[1:], 'dp:P:vVsn:')

    except getopt.GetoptError:

        usage()
        sys.exit(-1)
    
    if( len(pargs) == 1):

        dbname = pargs[0]


    for option, value in opts:

        if '-p' in option:
            pfname = str(value)

        if '-d' in option:
            daemonize = True

        if '-V' in option:
            debug = True
            verbose = True

        if '-v' in option:
            verbose = True

        if '-P' in option:
            port = int(value)

        if '-n' in option:
            nickname = str(value)

    #
    # Get values from pf file
    #
    if port == -1:
        port = stock.pfget_int( pfname, "port" )

    if not dbname:
        dbname = stock.pfget_arr( pfname, "db" )

    if nickname == '':
        nickname = stock.pfget_arr( pfname, "nickname" )

    binning_threshold   = stock.pfget_int( pfname, "binning_threshold" )
    canvas_size_default = stock.pfget_int( pfname, "canvas_size_default" )
    jquery_dir          = stock.pfget_string( pfname, "jquery_dir" )
    static_dir          = stock.pfget_string( pfname, "static_dir" )
    template            = stock.pfget_string( pfname, "template" )
    plot_template       = stock.pfget_string( pfname, "plot_template" )
    local_data          = stock.pfget_string( pfname, "local_data" )
    style               = stock.pfget_string( pfname, "jquery_ui_style" )
    antelope            = stock.pfget_string( pfname, "antelope" )
    application_name    = stock.pfget_string( pfname, "application_name" )
    application_title   = stock.pfget_string( pfname, "application_title" )
    apply_calib         = stock.pfget_boolean( pfname, "apply_calib" )
    display_tracebacks  = stock.pfget_boolean( pfname, "display_tracebacks" )
    display_arrivals    = stock.pfget_boolean( pfname, "display_arrivals" )
    display_points      = stock.pfget_boolean( pfname, "display_points" )
    default_chans       = stock.pfget_tbl( pfname, "default_chans" )
    default_time_window = stock.pfget_tbl( pfname, "default_time_window" )
    filters             = stock.pfget_arr( pfname, "filters" )
    import_paths        = stock.pfget_tbl( pfname, "import_paths" )

    # 
    # Expand paths
    #
    for p in import_paths:
        log.msg('Expnding path: %s' % p)
        sys.path.insert(0, p)
    # 
    # Fix paths
    #
    template = ("%s/%s/%s" % (antelope,local_data,template))
    plot_template = ("%s/%s/%s" % (antelope,local_data,plot_template))
    jquery_dir = ("%s/%s/%s" % (antelope,local_data,jquery_dir))
    static_dir = ("%s/%s/%s" % (antelope,local_data,static_dir))

    # 
    # Sanity check
    #
    if not os.path.isfile(template):
        sys.exit('\n\nERROR: No template found (%s)\n'% template)


    # Build dictionary of servers we want to run 
    if dbname and port:

        # only one for now
        run_server = { int(port):str(dbname) }

    else:

        usage()
        sys.exit('\n\nERROR: Not a valid db:port setup. (%s,%s)\n' % (dbname,port))


    argv_remap = list()
    argv_remap.append(sys.argv[0])

    if(not daemonize):
        argv_remap.append("-n")

    argv_remap.append("-y")
    argv_remap.append(os.path.join(os.environ['ANTELOPE'], 'local/data/python/dbwfserver/server.py'))

    if os.path.isdir('./state'):
        pid_path = './state'
    else:
        pid_path = '/tmp'
    argv_remap.append("--pidfile")
    argv_remap.append( pid_path+'/dbwfserver_'+str(os.getpid())+'.pid' )

    return argv_remap
