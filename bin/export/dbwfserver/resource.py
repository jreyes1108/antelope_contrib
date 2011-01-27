from __main__ import *

def isNumber(test):
#{{{
    """
    Test if the string is a valid number 
    and return the converted number. 
    """
    if config.debug: log.msg("isNunber(%s)" % test)

    try:
        test = str(test)
        if re.search('\.',test):
            try:
                return float(test)
            except:
                return None

        else:
            try:
                return int(test)
            except:
                return None
    except:
        return None

#}}}

class QueryParser(resource.Resource):
#{{{
    """
    Serve HTTP queries.
    """
    isLeaf = False
    if config.debug: print "Set isLeaf = %s" % isLeaf

    allowedMethods = ("GET")
    if config.debug: print "Set allowedMethods = %s" % allowedMethods

    def __init__(self,db):
    #{{{
        self.dbname = db

        """
        Initialize Classes
        """
        if config.verbose: print 'Load class resorce.Resource.__init__(self)'
        resource.Resource.__init__(self)

        """
        Open db using dbcentral CLASS
        """
        if config.debug: print "Create dbcentral object with database(%s)." % self.dbname
        self.db = dbcentral.dbcentral(self.dbname,config.nickname,config.debug)

        if config.verbose: self.db.info()

        if not self.db.list(): sys.exit('\nERROR: No databases to use! (%s)\n\n'% self.dbname)

        """
        We might need to remove 
        databases without wfdisc table
        """
        remove = []

        for dbname in sorted(self.db.list()):

            """ Test database access. """
            try:
                db_pntr = datascope.dbopen( dbname , "r" )

            except Exception, e:

                """ Remove database from dbcentral object. """
                print '\nERROR: dbopen(%s) =>(%s)\n' % (dbname,e)
                remove.append(dbname)
                continue

            if config.verbose: print "Databse %s" % db
            if config.debug: print "[%s,%s,%s,%s]" % (db_pntr['database'],db_pntr['table'],db_pntr['field'],db_pntr['record'])

            """ Test database tables. """
            if config.debug:
                """ List files in db directory. """
                head, tail = os.path.split(dbname)
                print "Files in directory:(%s)" % head
                print "%s" % [ x for x in os.listdir(head)]

            for tbl in ['wfdisc','instrument','sensor','origin','arrival']:

                if config.debug: print "Check table  [%s]." % tbl

                try:
                    db_pntr.lookup( table=tbl )

                except Exception, e:
                    print '\nERROR: %s.%s not present (%s)\n' % (dbname,tbl,e)
                    if tbl == 'wfdisc': remove.append(dbname)
                    continue

                try:
                    records = db_pntr.query(datascope.dbRECORD_COUNT)

                except Exception, e:

                    print '\nERROR: %s.%s( dbRECORD_COUNT )=>(%s)' % (db,tbl,e)
                    if tbl == 'wfdisc': remove.append(db)

                if not records and tbl == 'wfdisc':
                    print '\nERROR: %s.%s( dbRECORD_COUNT )=>(%s) Empty table!!!!' % (db,tbl,e)
                    remove.append(db)
                    continue

                if config.debug: print "%s.%s records=>[%s]" % (db,tbl,records)

            db_pntr.free()
            db_pntr.close()

        for db in remove:
            print "Removing %s from dbcentral object" % db
            try:
                self.db.purge(db)
            except:
                pass

        if len(remove): print "New list: dbcentral.list() => %s" % self.db.list()

        if not self.db.list(): sys.exit('\n\nNo good databases to work with! QUIT NOW! (run with -v or -V for more info)\n\n')

        """
        At this point we can start the reactor.
        Load the rest after the reactor is running.
        I want to run the rest in a separate thread 
        and all functions synchronously. 
        Each function on a different PID to avoid db access problems.
        """
        reactor.callWhenRunning(reactor.callInThread,self._init)

    #}}}

    def _init(self):
    #{{{

        """
        Initialize Classes
        """
        if config.debug: print 'Load class evdata.Stations(%s)' % self.dbname
        self.stations = evdata.Stations(self.db)

        if config.debug: print 'Load class evdata.Events(%s)' % self.dbname
        self.events = evdata.Events(self.db)

        """
        Default configuration for template.html
        """
        self.tvals = {
            "filters":           '<option value="None">None</option>',
            "dbname":            self.dbname,
            "application_title": config.application_title,
            "jquery_includes":   self._jquery_includes()
        }

        for filter in config.filters:
            self.tvals['filters'] += '<option value="'+config.filters[filter].replace(' ','_')+'">'
            self.tvals['filters'] += filter
            self.tvals['filters'] += '"</option>'

        if config.display_arrivals:
            self.tvals['display_arrivals'] = 'checked="checked"'
        else:
            self.tvals['display_arrivals'] = ''

        if config.display_points:
            self.tvals['display_points'] = 'checked="checked"'
        else:
            self.tvals['display_points'] = ''

        self.tvals['event_controls'] = ' \
            <p>Get time from event list:</p> \
            <input type="submit" id="load_events" value="Show Events"/> '

        if config.debug: print 'Done loading clases for reactor.'
        config.loading = False

        """
        Update Thread Pool
        """
        self.tp = reactor.getThreadPool()

        if config.debug: 
            print 'Actual Thread Pool.'
            self.tp.dumpStats()

        #reactor.suggestThreadPoolSize(30)
        self.tp.adjustPoolsize(20,20)


        if config.debug: 
            print 'New Thread Pool.'
            self.tp.dumpStats()


        #self.thread_pool = ThreadPool(20,20)
        #self.thread_pool.start()
        #reactor.addSystemEventTrigger('after', 'shutdown', self.thread_pool.stop)

        #if config.debug: reactor.callLater(.1, self.running_test)

        self.clean = reactor.callLater(10, self.dbclean)

#}}}

    def _jquery_includes(self):
        # {{{
        jquery_includes = ''

        for jqf in config.jquery_files:

            if(re.match(r'^IE\s+', jqf)):

                re.sub(r'^IE\s+', '', jqf)
                jquery_includes += '\n\t<!--[if IE]>\n'
                jquery_includes += '\t\t<script language="javascript" type="text/javascript" src="'
                jquery_includes += jqf + '"></script>\n\t<![endif]-->\n'

            else:

                jquery_includes += '\n\t<script type="text/javascript" src="' + jqf + '"></script>\n'

        return jquery_includes
        # }}}

    def _parse_request(self,args):
        # {{{

        """
        Strict format for uri:
            localhost/

            localhost/sta

            localhost/sta/time
            localhost/sta/chan

            localhost/sta/time/time
            localhost/sta/chan/time

            localhost/sta/chan/time/time

            localhost/sta/chan/time/time/filter

            localhost/wf/sta/chan/time/time/filter

            Data-only calls:
            localhost/data/wf
            localhost/data/meta
            localhost/data/times
            localhost/data/events
            localhost/data/filters
            localhost/data/stations
            localhost/data/coverage
            localhost/data/channels
            localhost/data/wf/sta/chan/time/time/filter
            localhost/data/meta/sta/chan/time/time/filter


        """
        if config.debug: log.msg("_parse_request(): Original URI: %s" % str(args) ) 

        uri  = defaultdict()
        temp = defaultdict(lambda: defaultdict(defaultdict))

        uri.update( { 
            "sta":[],
            "chan":[],
            "end":False,
            "data":False,
            "start":False,
            "filter":None,
            "time_window":False
        } )

        if len(args) > 0:
            #
            # Check for special flags
            #
            if 'day' in args:
                uri['time_window'] = 'day'
                args.remove('day')
            elif 'week' in args:
                uri['time_window'] = 'week'
                args.remove('week')
            elif 'month' in args:
                uri['time_window'] = 'month'
                args.remove('month')

            if args[0] == 'data':
                uri['data'] = True
                args.remove('data')
                if config.verbose: log.msg("_parse_request(): data query.") 
                return uri


        # localhost/sta
        if len(args) == 2:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))

        # localhost/sta/time
        # localhost/sta/chan
        elif len(args) == 3:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            if isNumber( args[2] ):
                uri['start'] = args[2]
            else:
                uri['chan'] = self.stations.convert_chan(uri['sta'],args[2].split('-'))

        # localhost/sta/time/time
        # localhost/sta/chan/time
        elif len(args) == 4:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            if isNumber( args[2] ):
                uri['start'] = args[2]
                uri['end'] = args[3]
            else:
                uri['chan'] = self.stations.convert_chan(uri['sta'],args[2].split('-'))
                uri['start'] = args[3]

        # localhost/sta/chan/time/time
        elif len(args) == 5:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['chan'] = self.stations.convert_chan(uri['sta'],args[2].split('-'))
            uri['start'] = args[3]
            uri['end'] = args[4]

        # localhost/sta/chan/time/time/filter
        elif len(args) == 6:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['chan'] = self.stations.convert_chan(uri['sta'],args[2].split('-'))
            uri['start'] = args[3]
            uri['end'] = args[4]
            uri['filter'] = args[5]

        #
        #Setting the filter
        #
        if uri['filter']:
            if uri['filter'] == 'None' or uri['filter'] == 'null' or uri['filter'] == '-':
                uri['filter'] = None
            else:
                uri['filter'] = uri['filter'].replace('_',' ')
        #
        # Fix stations
        #
        if uri['sta']:
            args[1] = '-'.join(uri['sta'])


        #
        # Fix times
        #
        if uri['start']: uri['start'] = isNumber(uri['start'])

        if uri['end']: uri['end'] = isNumber(uri['end'])

        if uri['end'] and uri['start']:
            if config.verbose: log.msg("_parse_request(): Converted URI: %s" % str(uri) ) 
            return uri

        if uri['time_window']:
            if uri['time_window'] == 'day': 
                time_window = 86400
            elif uri['time_window'] == 'week':
                time_window = 604800
            elif uri['time_window'] == 'month':
                time_window = 2629743
            else:
                time_window = config.default_time_window
        else:
            time_window = config.default_time_window

        if not uri['start']:
            uri['start'] = self.stations.max_time(uri['sta']) - time_window

        if not uri['end']:
            uri['end'] = uri['start'] + time_window

        if config.verbose: log.msg("_parse_request(): Converted URI: %s" % str(uri) ) 

        return uri
        # }}}

    def getChild(self, name, uri): 
    #{{{
        if config.debug: log.msg("getChild()")
        return self
    #}}}

#    def coverage(self, params=None, stations=None):
#    #{{{
#
#        #
#        #Get list of segments of data for the respective station and channel
#        #
#        sta_str  = ''
#        chan_str = ''
#        res_data = defaultdict(lambda: defaultdict(defaultdict))
#
#        res_data.update( {'type':'coverage'} )
#        res_data.update( {'format':'cov-bars'} )
#
#
#        #
#        # Build dictionary to store data
#        #
#        #   We need to build this to be clear to the application
#        #   that some stations may have no data.
#        for sta in res_data['sta']:
#
#            for chan in params['chan']:
#
#                if chan in stations.channels(sta):
#
#                    res_data[sta][chan] = {}
#
#
#        dbs = self.db()
#
#        for dbptr in dbs:
#
#            #if config.debug:
#            #    log.msg("Testing %s" % db)
#            #    log.msg("\ttimes for db")
#            #    log.msg("\tdbs[db]['start'] = %s" % dbs[db]['start'])
#            #    log.msg("\tdbs[db]['end'] = %s" % dbs[db]['end'])
#            #    log.msg("\ttimes for request")
#            #    log.msg("\tparams['time_start'] = %s" % params['time_start'])
#            #    log.msg("\tparams['time_end'] = %s" % params['time_end'])
#
#            #if 'time_start' in params:
#
#            #    if _isNumber(dbs[db]['end']) < _isNumber(params['time_start']): continue
#
#            #if 'time_end' in params:
#
#            #    if _isNumber(dbs[db]['start']) > _isNumber(params['time_end']): continue
#
#            #if config.debug: log.msg("Database matched query times...")
#
#            #
#            # Start wfdisc query
#            #
#            #dbptr = dbs[db]['pointer']
#
#            dbptr.lookup( table='wfdisc' )
#
#            # Subset wfdisc for stations
#            if 'sta' in params:
#
#                sta_str  = "|".join(str(x) for x in params['sta'])
#                dbptr.subset("sta =~/%s/" % sta_str)
#                if config.debug: log.msg("\n\nCoverage subset on sta =~/%s/ " % sta_str)
#
#            # Subset wfdisc for channels
#            if 'chan' in params:
#
#                chan_str  = "|".join(str(x) for x in params['chan'])
#                dbptr.subset("chan =~/%s/" % chan_str)
#                if config.debug: log.msg("\n\nCoverage subset on chan =~/%s/ " % chan_str)
#
#            # Subset wfdisc for start_time
#            if 'time_start' in params:
#
#                res_data.update( {'time_start':params['time_start']} )
#                dbptr.subset("endtime >= %s" % params['time_start'])
#                if config.debug: log.msg("\n\nCoverage subset on time >= %s " % params['time_start'])
#
#            # Subset wfdisc for end_time
#            if 'time_end' in params:
#
#                res_data.update( {'time_end':params['time_end']} )
#                dbptr.subset("time <= %s" % params['time_end'])
#                if config.debug: log.msg("\n\nCoverage subset on time_end <= %s " % params['time_end'])
#
#            if not dbptr.query(datascope.dbRECORD_COUNT):
#
#                _error('No records for: %s' %  params, res_data)
#                continue
#
#            # If no start time on request... use min in subset
#            if not 'time_start' in res_data:
#
#                min = dbptr.ex_eval('min(time)')
#
#                if not res_data['time_start']:
#
#                    res_data['time_start'] = min
#
#                elif min < res_data['time_start']:
#
#                    res_data['time_start'] = min
#
#            # If no end time on request... use max in subset
#            if not 'time_end' in res_data:
#
#                max = dbptr.ex_eval('max(endtime)')
#
#                if not res_data['time_end']:
#
#                    res_data['time_end'] = max
#
#                elif max > res_data['time_end']:
#
#                    res_data['time_end'] = max
#
#
#            for i in range(dbptr.query(datascope.dbRECORD_COUNT)):
#
#                dbptr.record = i
#
#                try:
#
#                    (this_sta,this_chan,time,endtime) = dbptr.getv('sta','chan','time','endtime')
#
#                except Exception,e:
#
#                    _error("Eventdata: Problem in getv(): %s" % e)
#
#                if not this_sta in res_data['sta']:
#
#                    res_data['sta'].append(this_sta)
#
#                if not this_chan in res_data['chan']:
#
#                    res_data['chan'].append(this_chan)
#
#                if config.debug: log.msg("Now with: (%s,%s,%s,%s)" % (this_sta,this_chan,time,endtime) )
#
#                if this_sta not in res_data:
#
#                    res_data[this_sta] = {}
#
#                if this_chan not in res_data[this_sta]:
#
#                    res_data[this_sta][this_chan] = {}
#
#                if 'data' not in res_data[this_sta][this_chan]:
#
#                    res_data[this_sta][this_chan]['data'] = []
#
#                try:
#                    res_data[this_sta][this_chan]['data'].append([time,endtime])
#                except:
#                    _error("Eventdata: Problem adding data to dictionary: [%s,%s] %s" % (time,endtime,e))
#
#        return res_data
#    #}}}
#
    def get_data(self,station,channel,start,end,filter=None):
        # {{{
        """
        Return points or bins of data for query
        """

        if config.debug: log.msg("get_data(): %s.%s [%s,%s]" % (station,channel,start,end))

        if type(station)==type(list()):
            station = station[0]
        if type(channel)==type(list()):
            channel = channel[0]


        response_data = defaultdict(dict)
        temp_dic = self.stations(station)

        if not temp_dic:
            log.msg("%s.%s not valid station-channel set" % (station,channel))
            response_data['error'] = "%s.%s not valid station-channel set" % (station,channel)
            return response_data

        if not channel in temp_dic:
            log.msg("%s not valid channel for station %s" % (channel,station))
            response_data['error'] = "%s not valid channel for station %s" % (channel,station)
            return response_data

        if config.debug: log.msg("get_data(): prepare vars for %s.%s " % (station,channel))
        response_data[station][channel] = defaultdict(dict)
        response_data[station][channel]['end']      = end
        response_data[station][channel]['start']    = start
        response_data[station][channel]['metadata'] = temp_dic[channel]


        points = 0
        if temp_dic[channel]['samprate']: points = int( (end-start) * temp_dic[channel]['samprate'] )

        if config.debug: log.msg("get_data(): points:%s canvas:%s threshold:%s" % (points,config.canvas_size_default,config.binning_threshold))               

        if points >  (config.binning_threshold * config.canvas_size_default):
            binsize = points/config.canvas_size_default
        else:
            binsize = 0


        dbname = self.db(start)
        if config.debug: log.msg("get_data(): db:%s" % dbname)

        #if config.debug: log.msg('From get_data(): os.getpid() => [%s]' % os.getpid() )

        try:
            db = datascope.dbopen( dbname, 'r' )
            db.lookup( table='wfdisc' )
            records = db.query(datascope.dbRECORD_COUNT)
        except Exception, e:
            del db
            log.msg('Loading: %s.wfdisc => [%s]' % (dbname,e) )
            response_data['error'] = 'Loading: %s.wfdisc => [%s]' % (dbname,e)
        else:

            #
            # Track pointers in array
            #
            config.dbpointers.append(db)

            if True: log.msg('get_data(): pid:[%s] pntr:[%s,%s,%s,%s]' % (os.getpid(),db.database,db.table,db.field,db.record))
            log.msg('Data: get_samples(%s,%s,%s,%s,%s,%s)' % (station,channel,start,end,binsize,filter) )

            try:
                if binsize:
                    response_data[station][channel]['data']   = db.samplebins(start,end,station,channel,binsize,False,filter)
                    response_data[station][channel]['format'] = 'bins'
                else:
                    response_data[station][channel]['data']   = db.sample(start,end,station,channel,False,filter)
                    response_data[station][channel]['format'] = 'lines'

            except Exception,e:
                log.msg("First exception [%s] on db.sample/samplebins: %s" % (Exception,e))
                sleep(1)
                try:
                    db = datascope.dbopen( dbname, 'r' )
                    db.lookup( table='wfdisc' )
                    records = db.query(datascope.dbRECORD_COUNT)
                except Exception, e:
                    del db
                    log.msg('Loading: %s.wfdisc => [%s]' % (dbname,e) )
                    response_data['error'] = 'Loading: %s.wfdisc => [%s]' % (dbname,e)
                    return "Exception [%s] on get_data: [%s]" % (Exception,e)
                else:
                    try:
                        if binsize:
                            response_data[station][channel]['data']   = db.samplebins(start,end,station,channel,binsize,False,filter)
                            response_data[station][channel]['format'] = 'bins'
                        else:
                            response_data[station][channel]['data']   = db.sample(start,end,station,channel,False,filter)
                            response_data[station][channel]['format'] = 'lines'

                    except Exception,e:
                        log.msg("Second exception [%s] on db.sample/samplebins: %s" % (Exception,e))
                        return "Exception [%s] on get_data: [%s]" % (Exception,e)

        return response_data

        # }}}

    def render_GET(self, uri):
    #{{{
        if config.debug: log.msg("render_GET()")

        #if config.debug: log.msg('QUERY: %s ' % uri)

        #if config.verbose: (host,port) = uri.getHeader('host').split(':', 1)
        #if config.verbose: log.msg('Hostname => [%s:%s]'% (host,port))
        #log.msg('Host=> [%s]'% uri.host)
        #log.msg('socket.gethostname() => [%s]'% socket.gethostname())
        #log.msg('socket.getsockname() => [%s]'% uri.host.getsockname())
        #uri.setHost(host,config.port)


        if self.stations.loading or self.events.loading:
            uri.setHeader("content-type", "text/html")
            uri.setHeader("response-code", 500)
            return "<html><head><title>%s</title></head><body><b>Server Loading!</b></body></html>" % config.application_name

        #
        # Delay the call to clean the database pointers
        #
        try:
            self.clean.reset(10)
        except:
            self.clean = reactor.callLater(10, self.dbclean)


        #
        #Build Deferred and throw in our thread. Not the reactor's threadpool 
        #
        #print "############################"
        #print "Thread_pool.dumpStats()"
        #self.tp.dumpStats()
        #print "############################"
        d = defer.Deferred()
        d.addCallback( self.render_uri )
        d.addCallback( uri.write )
        d.addCallback( lambda x: uri.finish() )
        d.addErrback( lambda x: self.defer_error(uri,x) )
        d.addErrback( lambda x: uri.finish() )
        reactor.callInThread(d.callback, uri)

        if config.debug: log.msg("Done with defer call. now return server.NOT_DONE_YET")

        return server.NOT_DONE_YET
    #}}}

    def render_uri(self, uri):
    #{{{

        if config.debug: log.msg('QUERY: %s ' % uri)
        #
        # Clean and prep vars
        #
        response_data = {}
        response_meta = {}
        query         = {}
        response_data = defaultdict(dict)
        response_meta = defaultdict(dict)
        query         = defaultdict(dict)

        response_meta.update( { 
            "type":              'meta-query',
            "dir":               '&mdash;',
            "key":               '&mdash;',
            "error":             'false',
            "setupUI":           'false',
            "meta_query":        'false'
        } )

        if config.debug:
            log.msg('New query:')
            log.msg('\turi:%s' % uri )
            log.msg('\turi.uri:%s' % uri.uri)
            log.msg('\turi.args:%s' % (uri.args) )
            log.msg('\turi.prepath:%s' % (uri.prepath) )
            log.msg('\turi.postpath:%s' % (uri.postpath) )
            log.msg('\turi.path:%s' % (uri.path) )
            log.msg('')

        path = uri.prepath

        #
        # remove all empty  elements
        # This (localhost:8008/stations/) is the same as # (localhost:8008/stations) 
        #
        while True:
            try: 
                path.remove('')
            except: 
                break

        query = self._parse_request(path)

        if path:
            log.msg('')
            log.msg('Query uri.prepath=>path:(size %s)%s' % (len(path),path) )
            log.msg('')

        if uri.args:
            log.msg('')
            log.msg('Query uri.args:(size %s)%s' % (len(uri.args),uri.args) )
            log.msg('')

        if len(path) == 0:
            pass

        elif query['data']:
        #{{{

                uri.setHeader("content-type", "application/json")

                if len(path) == 0:
                #{{{ ERROR: we need one option
                    uri.setHeader("content-type", "text/html")
                    uri.setHeader("response-code", 500)
                    return json.dumps( "Empty data query (%s)" % uri.uri )
                #}}}

                elif path[0] == 'events':
                #{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument.
                    """

                    if len(path) == 2:
                        return json.dumps(self.events(path[1]))

                    elif len(path) == 3:
                        return json.dumps(self.events.phases(path[1],path[2]))
                        #return json.dumps(risp.risp_s(102400,self.events.phases,path[1],path[2]))

                    else:
                        return json.dumps(self.events.table())
                #}}}

                elif path[0] == 'dates':
                #{{{
                    """
                    Return list of yearday values for time in db
                    for all stations in the cluster of dbs.
                    """
                    if len(path) == 2:
                        return json.dumps(self.stations.dates([path[1]]))

                    else:
                        return json.dumps(self.stations.dates())
                #}}}

                elif path[0] == 'stations':
                #{{{
                    """
                    Return station list as JSON objects. For client ajax calls.
                    Called with argument return dictionary
                    """

                    if len(path) == 2:

                        query['sta'] = self.stations.convert_sta(path[1].split('-'))

                        for sta in query['sta']:
                            response_data[sta] = self.stations(sta)

                        return json.dumps(response_data)

                    else:
                        return json.dumps(self.stations.list())
                #}}}

                elif path[0] == 'channels':
                #{{{
                    """
                    Return channels list as JSON objects. For client ajax calls.
                    """
                    return json.dumps(self.stations.channels())
                #}}}

                elif path[0] == 'filters':
                #{{{
                    """
                    Return list of filters as JSON objects. For client ajax calls.
                    """
                    return json.dumps(config.filters, sort_keys=True)
                #}}}

                elif path[0] == 'wf':
                #{{{
                    """
                    Return JSON object of data. For client ajax calls.
                    Use risp to run func on different PID.
                    """
                    #log.msg('Start sleep(5)')
                    #sleep(5)
                    #log.msg('End sleep(5)')
                    #return 'Done sleep'

                    query = self._parse_request(path)

                    #return json.dumps( risp.risp_s(102400,self.get_data,query['sta'],query['chan'],query['start'],query['end'],query['filter']) )
                    return json.dumps( self.get_data(query['sta'],query['chan'],query['start'],query['end'],query['filter']) )

                #}}}

                elif path[0] == 'coverage':
                #{{{
                    """
                    Return coverage tuples as JSON objects. For client ajax calls.
                    """

                    query = self._parse_request(path)

                    return json.dumps(self.data.coverage(query,self.stations))

                #}}}

                elif path[0] == 'meta':
                #{{{
                    """
                    *** DEBUGGING TOOL ***
                    TEST metaquery parsing response. 
                    Return json with meta-query data for further ajax uri.
                    """

                    query = self._parse_request(path)

                    if 'start' in query: 

                        response_meta['phases'] = self.events.time(query['start'],20)


                    for station in query['sta']:

                        temp_dic = self.stations(str(station))

                        if not temp_dic: continue

                        for channel in query['chan']:

                            if not channel in  temp_dic: continue

                            response_meta[station][channel]['metadata']  = temp_dic[channel]

                            response_meta['traces'][station][channel] = 'True'

                    return json.dumps(response_meta)

                #}}}

                else:
                #{{{ ERROR: Unknown query type.
                    uri.setHeader("content-type", "text/html")
                    uri.setHeader("response-code", 500)
                    return json.dumps( "Unknown query type:(%s)" % path )
                #}}}

        #}}}

        elif path[0] == 'wf':
            #{{{
                """
                Parse query for data uri. Return html with meta-query data for further ajax uri.
                """

                response_meta['meta_query'] = defaultdict(lambda: defaultdict(defaultdict))

                for sta in query['sta']:
                    temp_dic = self.stations(sta)
                    if not temp_dic: continue

                    for chan in query['chan']:
                        if not chan in temp_dic: continue
                        #response_meta['meta_query'][sta][chan] = temp_dic[chan]
                        response_meta['meta_query']['traces'][sta][chan] = 'True'


                response_meta['meta_query']['time_start'] = query['start']
                response_meta['meta_query']['time_end'] = query['end']
                response_meta['meta_query'] = json.dumps( response_meta['meta_query'] )

                response_meta['dir'] = 'wf'

                path.remove('wf')

                response_meta['key']  = " / ".join(str(x) for x in path)

            #}}}

        elif path[0] == 'plot':
            #{{{
                """
                Parse query for data uri. Return html with meta-query data for further ajax uri.
                """

                uri.setHeader("content-type", "text/html")

                #query = self._parse_request(path)
                response_meta['meta_query'] = defaultdict(lambda: defaultdict(defaultdict))

                for sta in query['sta']:
                    temp_dic = self.stations(sta)
                    if not temp_dic: continue

                    for chan in query['chan']:
                        if not chan in temp_dic: continue
                        response_meta['meta_query']['traces'][sta][chan] = 'True'


                response_meta['meta_query']['time_start'] = query['start']
                response_meta['meta_query']['time_end'] = query['end']
                response_meta['meta_query'] = json.dumps( response_meta['meta_query'] )

                response_meta.update(self.tvals)
                
                return  Template(open(config.plot_template).read()).safe_substitute(response_meta)

            #}}}

        else:
            uri.setHeader("content-type", "text/html")
            uri.setHeader("response-code", 500)
            log.msg("Unknown type of query: %s" % path)
            return json.dumps( "Unknown query type:(%s)" % path )


        if 'mode' in uri.args:

            response_meta['setupUI'] = json.dumps(uri.args)


        response_meta.update(self.tvals)
        
        return  Template(open(config.template).read()).safe_substitute(response_meta)

    #}}}

#    def running_test(self):
#    #{{{
#        #
#        # Prints a few dots on stdout while the reactor is running.
#        #
#        print '.'
#        reactor.callLater(.1, self.running_test)
#    #}}}
#
    def defer_error(self, uri, text):
    #{{{
        #
        # Prints Error back to the browser.
        #
        log.msg('\n\n%s\n\n' % text)
        uri.setHeader("content-type", "text/html")
        uri.setHeader("response-code", 400)
        uri.write('ERROR in query: \n %s' % text)
    #}}}

    def dbclean(self):
    #{{{
        #
        # Stop processing requests and clean the db pointers
        #
        if config.verbose: log.msg('Start cleaning.')
        config.locked = True

        for db in config.dbpointers:
            if config.verbose: log.msg('cleaning pntr:[%s,%s,%s,%s]' % (db.database,db.table,db.field,db.record))
            try:
                db.free()
                db.close()
            except:
                pass

        config.dbpointers = []
            
        config.locked = False
        if config.verbose: log.msg('End cleaning.')
        
        #self.clean = reactor.callLater(10, self.dbclean)
    #}}}

#}}}
