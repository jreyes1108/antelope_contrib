from __main__ import sys
from __main__ import os

import getopt
import antelope.stock as stock

global sys

def usage():

    print "Usage: dbwfserver [-dvV] [-p pfname] [-P port] [dbname]\n"

def configure(args):

    global pfname
    global application_name
    global application_title
    global static_dir
    global jquery_dir
    global html_template
    global simple_html_template
    global dbname
    global port
    global dbs
    global binning_threshold
    global canvas_size_default
    global apply_calib
    global display_tracebacks
    global display_arrivals
    global verbose
    global debug
    global simple
    global daemonize
    global import_paths
    global jquery_files
    global default_chans
    global default_time_window
    global filters
    global run_servers

    pfname = 'dbwfserver'

    application_name    = ''
    application_title   = ''
    static_dir          = ''
    jquery_dir          = ''
    html_template       = ''
    simple_html_template= ''
    dbname              = ''
    port                = -1
    binning_threshold   = -1
    canvas_size_default = -1
    apply_calib         = False
    display_tracebacks  = False
    display_arrivals    = True
    verbose             = False
    debug               = False
    simple              = False
    daemonize           = False
    import_paths        = ()
    jquery_files        = ()
    default_chans       = ()
    default_time_window = -1
    filters             = {}
    dbs                 = {}
    run_servers         = {}

    try:

        opts, pargs = getopt.getopt(sys.argv[1:], 'dp:P:vVs')

    except getopt.GetoptError:

        usage()
        sys.exit(-1)
    
    if( len(pargs) == 1):

        dbname = pargs[0]


    for option, value in opts:

        if '-p' in option:
            pfname = value

        if '-d' in option:
            daemonize = True

        if '-V' in option:
            debug = True
            verbose = True

        if '-v' in option:
            verbose = True

        if '-s' in option:
            simple = True

        if '-P' in option:
            port = int(value)

    #
    # Get values from pf file
    #
    port                = stock.pfget_int( pfname, "port" )
    binning_threshold   = stock.pfget_int( pfname, "binning_threshold" )
    canvas_size_default = stock.pfget_int( pfname, "canvas_size_default" )
    jquery_dir          = stock.pfget_string( pfname, "jquery_dir" )
    static_dir          = stock.pfget_string( pfname, "static_dir" )
    html_template       = stock.pfget_string( pfname, "html_template" )
    simple_html_template= stock.pfget_string( pfname, "simple_html_template" )
    application_name    = stock.pfget_string( pfname, "application_name" )
    application_title   = stock.pfget_string( pfname, "application_title" )
    apply_calib         = stock.pfget_boolean( pfname, "apply_calib" )
    display_tracebacks  = stock.pfget_boolean( pfname, "display_tracebacks" )
    display_arrivals    = stock.pfget_boolean( pfname, "display_arrivals" )
    jquery_files        = stock.pfget_tbl( pfname, "jquery_files" )
    default_chans       = stock.pfget_tbl( pfname, "default_chans" )
    default_time_window = stock.pfget_tbl( pfname, "default_time_window" )
    filters             = stock.pfget_arr( pfname, "filters" )
    dbs                 = stock.pfget_arr( pfname, "dbs" )
    import_paths        = stock.pfget_tbl( pfname, "import_paths" )

    # Build dictionary of servers we want to run 
    if dbname:
        run_servers = { int(port):str(dbname) }

    else:
        for db in dbs:
            dbname = db
            run_servers[int(db)] = str(dbs[db])

    for p in import_paths:
        sys.path.insert(0, p)

    argv_remap = list()
    argv_remap.append(sys.argv[0])

    if(not daemonize):
        argv_remap.append("-n")

    argv_remap.append("-y")
    argv_remap.append(os.path.join(os.environ['ANTELOPE'], 'data/python/dbwfserver/server.py'))

    return argv_remap
