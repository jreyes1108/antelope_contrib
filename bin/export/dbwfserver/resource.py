from __main__ import *

def _error(text,dictionary=None,quiet=False):
#{{{
    """
    Test if the 'error' is defined in the dictionary and append text.
    Return updated dictionary.
    """

    log.msg("\nERROR:\n\t%s\n\n" % text)

    if dictionary and not quiet:
        if 'error' in dictionary:
            dictionary['error'] = str(dictionary['error']) + '\n'+ text 
        else:
            dictionary['error'] = '\n' + text

    if dictionary: return dictionary
#}}}

def isNumber(test):
#{{{
    #
    #Test if the string is a valid number 
    #and return the converted number. 
    #
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

def get_data(dbname,debug,sta,chan,start,end,binsize,filter=None):
    # {{{
    #
    # Return points or bins of data for query
    #

    if debug: print "get_data(): Get data for %s.%s [%s,%s]" % (sta,chan,start,end)

    response_data = defaultdict(dict)

    try:
        temp_db = datascope.dbopen( dbname, 'r' )
        temp_db.lookup( table='wfdisc' )
        records = temp_db.query(datascope.dbRECORD_COUNT)

    except Exception, e:
        print 'get_data(): ERROR: Loading: %s.wfdisc => [%s]' % (dbname,e)
        response_data['error'] = 'Loading: %s.wfdisc => [%s]' % (dbname,e)

    else:

        if debug: print 'get_data(): pid:[%s] pntr:[%s,%s,%s,%s]' % (os.getpid(),temp_db.database,temp_db.table,temp_db.field,temp_db.record)
        if debug: print '\t\tget_data(): get_samples(%s,%s,%s,%s,%s,%s)' % (sta,chan,start,end,binsize,filter)

        try:
            if binsize:
                response_data['data']   = temp_db.samplebins(start,end,sta,chan,binsize,False,filter)
                response_data['format'] = 'bins'
            else:
                response_data['data']   = temp_db.sample(start,end,sta,chan,False,filter)
                response_data['format'] = 'lines'

        except Exception,e:
            print "get_dat(): ERROR: Exception [%s] on temp_db.sample/samplebins: %s" % (Exception,e)
            response_data['error'] = "get_dat(): ERROR: Exception [%s] on temp_db.sample/samplebins: %s" % (Exception,e)
            response_data['data']   = []
            response_data['format'] = 'lines'

    #try:
    #    temp_db.close()
    #except:
    #    pass

    return response_data

    # }}}

def coverage(db,config,station_obj,station=None, channel=None, start=0, end=0):
#{{{

    debug = config['debug']
    verbose = config['verbose']
    canvas_size_default = config['canvas_size_default']
    binning_threshold = config['binning_threshold']
    debug = config['debug']
    verbose = config['verbose']

    if config.debug: log.msg("coverage(): %s.%s [%s,%s]" % (station,channel,start,end))

    #
    #Get list of segments of data for the respective station and channel
    #
    sta_str  = ''
    chan_str = ''
    res_data = defaultdict(lambda: defaultdict(defaultdict))

    res_data.update( {'type':'coverage'} )
    res_data.update( {'format':'cov-bars'} )
    res_data.update( {'sta':[]} )
    res_data.update( {'chan':[]} )

    #
    # Build dictionary to store data
    #
    #   We need to build this to be clear to the application
    #   that some stations may have no data.
    for sta in station:

        for chan in channel: 

            if chan in self.stations(sta):

                res_data[sta][chan] = {}

    if not start: 
        dbname = self.db( stock.now() )
    else: 
        dbname = self.db(start)

    if config.debug: log.msg("coverage(): db:%s" % dbname)

    try:
        db = datascope.dbopen( dbname, 'r' )
        db.lookup( table='wfdisc' )

    except Exception, e:
        del db
        log.msg('Loading: %s.wfdisc => [%s]' % (dbname,e) )
        response_data['error'] = 'Loading: %s.wfdisc => [%s]' % (dbname,e)

    # Subset wfdisc for stations
    if station:

        sta_str  = "|".join(str(x) for x in station)
        db.subset("sta =~/%s/" % sta_str)
        if config.debug: log.msg("\n\nCoverage subset on sta =~/%s/ " % sta_str)

    # Subset wfdisc for channels
    if channel:

        chan_str  = "|".join(str(x) for x in channel)
        db.subset("chan =~/%s/" % chan_str)
        if config.debug: log.msg("\n\nCoverage subset on chan =~/%s/ " % chan_str)

    # Subset wfdisc for start_time
    if start:

        res_data['time_start'] = start
        db.subset("endtime > %s" % start)
        if config.debug: log.msg("\n\nCoverage subset on time >= %s " % start)

    else:
        # If no start time on request... use min in subset
        res_data['time_start'] = db.ex_eval('min(time)')

    # Subset wfdisc for end_time
    if end:

        res_data['time_end'] = end
        db.subset("time <= %s" % end)
        if config.debug: log.msg("\n\nCoverage subset on time_end <= %s " % end)

    else:
        # If no end time on request... use max in subset
        res_data['time_end'] = dbptr.ex_eval('max(endtime)')

    try:
        records = db.query(datascope.dbRECORD_COUNT)
    except:
        records = 0

    if not records:

        log.msg('No records for: [%s,%s,%s,%s]' %  (station,channel,start,end))
        return res_data

    for i in range(records):

        db.record = i

        try:

            (this_sta,this_chan,time,endtime) = db.getv('sta','chan','time','endtime')

        except Exception,e:

            log.msg("coverage(): Problem in getv(): %s" % e)

        else:

            if config.debug: log.msg("coverage() db.getv: (%s,%s,%s,%s)" % (this_sta,this_chan,time,endtime) )

            if time < start: time = start
            if end < endtime: endtime = end

            if not this_sta in res_data['sta']:

                res_data['sta'].append(this_sta)

            if not this_chan in res_data['chan']:

                res_data['chan'].append(this_chan)

            if 'data' not in res_data[this_sta][this_chan]:

                res_data[this_sta][this_chan]['data'] = []

            try:
                res_data[this_sta][this_chan]['data'].append([time,endtime])
            except:
                log.msg("coverage(): Problem adding data to dictionary: [%s,%s] %s" % (time,endtime,e))

    return res_data
#}}}

def Update_Stations(dbcentral,first,debug):
    #{{{ private function to load data

    if debug: print "\n\nUpdate Stations()...\n\n"

    stachan_cache = defaultdict(dict)

    for dbname in dbcentral.list():

        #
        # On the first part just get the names and pass them down to the object
        #
        if debug: print "\n\nUpdate Stations()...try db: %s\n\n" % dbname
        try:
            db = datascope.dbopen( dbname , 'r' )
            db.lookup( table='wfdisc')
            db.sort(['sta', 'chan'], unique=True)
            records = db.query(datascope.dbRECORD_COUNT)

        except:
            records = 0



        if not records: stock.elog_die('Stations(): ERROR: No records to work on any  table\n\n')

        for j in range(records):

            db.record = j
            try:
                sta, chan,  srate, calib, segtype = db.getv('sta','chan','samprate','calib','segtype')
            except Exception, e:
                print 'Station(): ERROR extracting data db.getv(sta,chan,samprate,calib,segtype). (%s=>%s)' % (Exception,e)


            #if srate == nulls('samprate'):
            #    srate = '-'

            #if calib == nulls('calib'):
            #    calib = '-'

            #if segtype == nulls('segtype'):
            #    segtype = '-'

            if not sta in stachan_cache: stachan_cache[sta] = defaultdict(dict)
            stachan_cache[sta][chan]['calib']    = calib
            stachan_cache[sta][chan]['segtype']  = segtype
            stachan_cache[sta][chan]['samprate'] = srate

            if debug: print "Station(): (simple loop) %s.%s[%s,%s,%s]" % (sta,chan,calib,segtype,srate)


        if first:
            #
            #  Simple time selection
            #

            if debug: print "\n\nUpdate Stations()...first loop\n\n"
            try:
                db.lookup( table='wfdisc')
                records = db.query(datascope.dbRECORD_COUNT)

            except:
                pass

            else:
                try:
                    start = db.ex_eval('min(time)')
                    end   = db.ex_eval('max(endtime)')
                except Exception,e:
                    print 'Station(): ERROR extracting max and min times. (%s=>%s)' % (Exception,e)

                for sta in stachan_cache:

                    for chan in stachan_cache[sta]:

                        stachan_cache[sta][chan]['start'] = start

                        stachan_cache[sta][chan]['end'] = end

                        start_day = stock.str2epoch(stock.epoch2str(start,'%D'))
                        end_day = stock.str2epoch(stock.epoch2str(end,'%D'))

                        if debug: print "Station(): %s.%s[%s,%s]" % (sta,chan,start_day,end_day)

                        stachan_cache[sta][chan]['dates'] = [start_day,end_day]

        else:
            #
            #  Now lets get the times. 
            #
            if debug: print "\n\nUpdate Stations()...not first loop\n\n"
            for sta in stachan_cache:

                try:
                    db.lookup( table='wfdisc')
                    db.subset( "sta == '%s'" % sta )
                    records = db.query(datascope.dbRECORD_COUNT)

                except:
                    records = 0

                else:
                    try:
                        start = db.ex_eval('min(time)')
                        end   = db.ex_eval('max(endtime)')
                    except Exception,e:
                        print 'Station(): ERROR extracting max and min times. (%s=>%s)' % (Exception,e)
                        continue

                    for chan in stachan_cache[sta]:

                        stachan_cache[sta][chan]['start'] = start

                        stachan_cache[sta][chan]['end'] = end

                        start_day = stock.str2epoch(stock.epoch2str(start,'%D'))
                        end_day = stock.str2epoch(stock.epoch2str(end,'%D'))

                        if debug: print "Station(): %s.%s[%s,%s]" % (sta,chan,start_day,end_day)

                        stachan_cache[sta][chan]['dates'] = [start_day,end_day]

        try:
            db.close()
        except:
            pass

    if debug:
        print "Stations(): Updating cache (%s) stations." % len(stachan_cache.keys())

    print "\n\nUpdate Stations()...done\n\n"
    return stachan_cache

    #}}}

def Update_Events(dbcentral,first,times,debug):
    #{{{ private function to load the data from the tables

    if debug: print "Events(): update cache."

    for dbname in dbcentral.list():

        event_cache = defaultdict(dict)

        if debug: print "Events(): _get_event_cache  db[%s]" % (dbname)

        try:
            db = datascope.dbopen( dbname , 'r' )
            db.lookup( table='event')
            records = db.query(datascope.dbRECORD_COUNT)

        except:
            records = 0


        if records:

            try:
                db.join( 'origin' )
                db.subset( 'orid == prefor' )
            except:
                pass

        else:

            try:
                db.lookup( table='origin' )
            except:
                pass


        try:
            records = db.query(datascope.dbRECORD_COUNT)
        except:
            records = 0


        if not records: 
            print 'Events(): ERROR: No records to work on any table\n\n'
            return event_cache

        if debug: 
            print "Events(): origin db_pointer: [%s,%s,%s,%s]" % (db['database'],db['table'],db['field'],db['record'])

        if 'start' in times:

            db.subset("time > %f" % float(times['start']))

        if 'end' in times:

            db.subset("time < %f" % float(times['end']))

        try:
            records = db.query(datascope.dbRECORD_COUNT)
        except:
            records = 0

        if not records: 
            print 'Events(): ERROR: No records after time subset\n\n'
            return

        for i in range(records):

            db.record = i

            (orid,time,lat,lon,depth,auth,mb,ml,ms,nass) = db.getv('orid','time','lat','lon','depth','auth','mb','ml','ms','nass')

            #if auth == self.nulls('auth'):
            #    auth = '-'

            #if orid == self.nulls('orid'):
            #    orid = '-'

            #if time == self.nulls('time'):
            #    time = '-'
            #else:
            #    time = "%0.2f" % time

            #if lat == self.nulls('lat'):
            #    lat = '-'
            #else:
            #    lat = "%0.2f" % lat

            #if lon == self.nulls('lon'):
            #    lon = '-'
            #else:
            #    lon = "%0.2f" % lon

            #if depth == self.nulls('depth'):
            #    depth = '-'
            #else:
            #    depth = "%0.2f" % depth

            #if mb == self.nulls('mb'):
            #    mb = '-'
            #else:
            #    mb = "%0.1f" % mb

            #if ms == self.nulls('ms'):
            #    ms = '-'
            #else:
            #    ms = "%0.1f" % ms

            #if ml == self.nulls('ml'):
            #    ml = '-'
            #else:
            #    ml = "%0.1f" % ml

            #if nass == self.nulls('nass'):
            #    nass = '-'
            #else:
            #    nass = "%d" % nass


            event_cache[orid] = {'time':time, 'lat':lat, 'lon':lon, 'depth':depth, 'auth':auth, 'mb':mb, 'ms':ms, 'ml':ml, 'nass':nass}

            if mb > 0:
                event_cache[orid]['magnitude'] = mb
                event_cache[orid]['mtype'] = 'Mb'
            elif ms > 0:
                event_cache[orid]['magnitude'] = ms
                event_cache[orid]['mtype'] = 'Ms'
            elif ml > 0:
                event_cache[orid]['magnitude'] = ml
                event_cache[orid]['mtype'] = 'Ml'
            else:
                event_cache[orid]['magnitude'] = '-'
                event_cache[orid]['mtype'] = '-'

        try:
            db.close()
        except:
           pass

    if debug: print "Events(): Updating cache. (%s)" % len(event_cache)

    return event_cache
#}}}

def init_Reactor(db,simple,debug,tvals):
    #{{{
        #
        # We might need to remove 
        # databases without wfdisc table
        #
        remove = []

        for dbname in sorted(db.list()):

            #
            # Test database access. 
            #
            if debug: print "init() try dbopen [%s]" % dbname
            try:
                db_temp = datascope.dbopen( dbname , "r" )

            except Exception, e:

                """ Remove database from dbcentral object. """
                print '\nERROR: dbopen(%s) =>(%s)\n' % (dbname,e)
                remove.append(dbname)
                continue

            if debug: print "Dbptr: [%s,%s,%s,%s]" % (db_temp['database'],db_temp['table'],db_temp['field'],db_temp['record'])

            #
            #Test database tables.
            #
            if debug:
                """ List files in db directory. """
                head, tail = os.path.split(dbname)
                print "Files in directory:(%s)" % head
                print "\t%s" % [ x for x in os.listdir(head)]

            if simple:
                print '\n\tRunning in SIMPLE mode. Use ONLY wfdisc table.\n'
                table_list =  ['wfdisc']
            else:
                table_list =  ['wfdisc','instrument','sensor','origin','arrival']

            for tbl in table_list:

                if debug: print "Check table  [%s]." % tbl

                try:
                    db_temp.lookup( table=tbl )

                except Exception, e:
                    print '\nERROR: %s.%s not present (%s)\n' % (dbname,tbl,e)
                    if tbl == 'wfdisc': 
                        remove.append(dbname)
                        continue
                    else:
                        print '\nERROR: problems with %s.%s Running simple mode!\n' % (dbname,tbl)
                        simple = True

                try:
                    records = db_temp.query(datascope.dbRECORD_COUNT)

                except Exception, e:

                    print '\nERROR: %s.%s( dbRECORD_COUNT )=>(%s)' % (db_temp,tbl,e)
                    if tbl == 'wfdisc': remove.append(db_temp)

                if records and tbl == 'origin':
                    tvals['event_controls'] = ' \
                        <p>Get time from event list:</p> \
                        <input type="submit" id="load_events" value="Show Events"/> '

                if not records and tbl == 'wfdisc':
                    print '\nERROR: %s.%s( dbRECORD_COUNT )=>(%s) Empty table!!!!' % (db_temp,tbl,records)
                    remove.append(db_temp)
                    continue

                if debug: print "\t%s records=>[%s]" % (tbl,records)

            try:
                db_temp.close()
            except:
                print '\nERROR: dbclose(%s) =>(%s)\n' % (dbname,e)
                remove.append(dbname)
                continue


        for db_temp in remove:
            print "Removing %s from dbcentral object" % db_temp
            try:
                db.purge(db_temp)
            except:
                pass

        if len(remove): print "New list: dbcentral.list() => %s" % db.list()

        if not db.list(): sys.exit('\n\nNo good databases to work with! QUIT NOW! (run with -v or -V for more info)\n\n')

        return [tvals,simple]


#}}}

class Stations():
#{{{ Class to load information about stations
    """
    Data structure and functions to query for stations
    """

    def __init__(self, db, config):
    #{{{ Load class and get the data

        self.config = config
        self.first = True
        self.dbcentral = db
        self.stachan_cache = defaultdict(lambda: defaultdict(defaultdict))
        self.offset = -1

        #
        # Load null class
        #
        self.nulls = db_nulls(db,self.config.debug,['wfdisc','sensor','instrument']) 

        #
        # Run update in loop call
        #
        self._running_loop = False
        stachan_loop = LoopingCall(deferToThread,self._inThread)
        stachan_loop.start(600,now=True)

    #}}}

    def _cb(self,result):
    #{{{

        #log.msg("Class Stations: got result from thread: %s" % result)
        self.stachan_cache = result
        self.first = False

    #}}}

    def _inThread(self):
    #{{{

        result = pool.apply_async(Update_Stations,(self.dbcentral,self.first,self.config.debug),callback=self._cb)
        #return result.get()

    #}}}

    def __getitem__(self,i):
    #{{{ Iteration context

        return self.stachan_cache.keys()[i]

    #}}}

    def next(self):
    #{{{ method to produce items unitl StopIteration is raised

        if len(self.stachan_cache.keys()) == self.offset:

            self.offset = -1
            raise StopIteration

        else:

            return self.stachan_cache.keys()[self.offset]

    #}}}

    def __str__(self):
    #{{{ Nicely print of elements in class.
        """
        end-user/application display of content using log.msg() or log.msg()
        """

        if self.config.verbose: log.msg("class Stations():")

        for st in self.stachan_cache.keys():
            chans = self.stachan_cache[st].keys()
            log.msg("\t%s: %s" % (st,chans))

    #}}}

    def __call__(self, station):
    #{{{ Function calls to the class.
        """
        method to intercepts data requests.
        """


        if station in self.stachan_cache:
            if self.config.debug: log.msg("Stations(%s) => %s" % (station,self.stachan_cache[station]))
            return self.stachan_cache[station]

        else:
            log.msg("Class Stations(): No value for station:%s" % station)
            for sta in self.stachan_cache:
                for chan in self.stachan_cache[sta]:
                    log.msg('%s.%s => %s' % (sta,chan,self.stachan_cache[sta][chan]))

        return False
    #}}}

    def _get_stachan_cache(self):
    #{{{ private function to load data

        stachan_cache = defaultdict(dict)
        records = 0

        if self.config.debug: 
            log.msg("Station(): update cache.")

        for dbname in self.dbcentral.list():

            #
            # On the first part just get the names and pass them down to the object
            #
            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='wfdisc')
                db.sort(['sta', 'chan'], unique=True)
                records = db.query(datascope.dbRECORD_COUNT)

            except:
                records = 0


            if not records: stock.elog_die('Stations(): ERROR: No records to work on any  table\n\n')

            for j in range(records):

                db.record = j
                try:
                    sta, chan,  srate, calib, segtype = db.getv('sta','chan','samprate','calib','segtype')
                except Exception, e:
                    log.msg('Station(): ERROR extracting data db.getv(sta,chan,samprate,calib,segtype). (%s=>%s)' % (Exception,e))


                if srate == self.nulls('samprate'):
                    srate = '-'

                if calib == self.nulls('calib'):
                    calib = '-'

                if segtype == self.nulls('segtype'):
                    segtype = '-'

                if not sta in stachan_cache: stachan_cache[sta] = defaultdict(dict)
                stachan_cache[sta][chan]['calib']    = calib
                stachan_cache[sta][chan]['segtype']  = segtype
                stachan_cache[sta][chan]['samprate'] = srate

                if self.config.debug: log.msg("Station(): (simple loop) %s.%s[%s,%s,%s]" % (sta,chan,calib,segtype,srate))


            if self.first:
                #
                #  Simple time selection
                #

                self.first = False

                try:
                    db.lookup( table='wfdisc')
                    records = db.query(datascope.dbRECORD_COUNT)

                except:
                    pass

                else:
                    try:
                        start = db.ex_eval('min(time)')
                        end   = db.ex_eval('max(endtime)')
                    except Exception,e:
                        log.msg('Station(): ERROR extracting max and min times. (%s=>%s)' % (Exception,e))

                    for sta in stachan_cache:

                        for chan in stachan_cache[sta]:

                            stachan_cache[sta][chan]['start'] = start

                            stachan_cache[sta][chan]['end'] = end

                            start_day = stock.str2epoch(stock.epoch2str(start,'%D'))
                            end_day = stock.str2epoch(stock.epoch2str(end,'%D'))

                            if self.config.debug: log.msg("Station(): %s.%s[%s,%s]" % (sta,chan,start_day,end_day))

                            stachan_cache[sta][chan]['dates'] = [start_day,end_day]

            else:
                #
                #  Now lets get the times. 
                #
                for sta in stachan_cache:

                    try:
                        db.lookup( table='wfdisc')
                        db.subset( "sta == '%s'" % sta )
                        records = db.query(datascope.dbRECORD_COUNT)

                    except:
                        records = 0

                    else:
                        try:
                            start = db.ex_eval('min(time)')
                            end   = db.ex_eval('max(endtime)')
                        except Exception,e:
                            log.msg('Station(): ERROR extracting max and min times. (%s=>%s)' % (Exception,e))
                            continue

                        for chan in stachan_cache[sta]:

                            stachan_cache[sta][chan]['start'] = start

                            stachan_cache[sta][chan]['end'] = end

                            start_day = stock.str2epoch(stock.epoch2str(start,'%D'))
                            end_day = stock.str2epoch(stock.epoch2str(end,'%D'))

                            if self.config.debug: log.msg("Station(): %s.%s[%s,%s]" % (sta,chan,start_day,end_day))

                            stachan_cache[sta][chan]['dates'] = [start_day,end_day]

        if self.config.verbose:
            log.msg("Stations(): Updating cache (%s) stations." % len(stachan_cache.keys()))

        return stachan_cache


    #}}}

    def max_time(self,test=False):
    #{{{ function to return time of last sample for list
        """
        Get time of first sample
        """

        cache = 0

        if not test: test = self.stachan_cache.keys()

        for sta in test:

            for chan in self.stachan_cache[sta].keys():

                try: 
                    if self.stachan_cache[sta][chan]['end'] > cache:
                        cache = self.stachan_cache[sta][chan]['end']
                except:
                    pass

        if self.config.debug: log.msg('Stations(): max_time(%s)=>%s' % (test,cache) )
        return cache

    #}}}

    def dates(self,test=False):
    #{{{ function to return start and end times for a station
        """
        Get list of valid dates
        """

        cache = defaultdict(list)

        if not test: test = self.stachan_cache.keys()

        for sta in test:

            if not sta in self.stachan_cache: continue 

            for chan in self.stachan_cache[sta].keys():

                if not 'dates' in self.stachan_cache[sta][chan]: continue

                if self.config.debug: log.msg("Stations(): dates(%s,%s)=>%s" % (sta,chan,self.stachan_cache[sta][chan]['dates']) )

                (start,end) = self.stachan_cache[sta][chan]['dates']

                if sta not in cache: cache[sta] = (start,end)

                try: 
                    if cache[sta][0] > start:
                        cache[sta][0] = start 
                except:
                    cache[sta][0] = start 

                try:
                    if cache[sta][1] < end:
                        cache[sta][1] = end
                except:
                    cache[sta][chan][1] = end

        if self.config.debug: log.msg("Stations(): dates(%s)=>%s" % (test,cache) )

        return cache

    #}}}

    def channels(self,station=False):
    #{{{ function to return list of valid channels
        """
        Get unique list of channels.
        """
        chans = {}

        if station:

            if station in self.stachan_cache:

                for ch in self.stachan_cache[station]:

                    chans[ch] = 1
            else:

                return False
        else:

            for st in self.stachan_cache.keys():

                for ch in self.stachan_cache[st]:

                    chans[ch] = 1

        return chans.keys()

    #}}}

    def convert_sta(self, list=['.*']):
    #{{{ get list of stations for the query

        stations = []
        keys = {} 

        if not list: list = ['.*'] 

        if self.config.debug: log.msg("Stations(): convert_sta(%s)" % list)

        for test in list:

            if re.search('^\w*$', test): 
                stations.extend([x for x in self.stachan_cache if x == test])

            else:

                if not re.search('^\^', test): test = '^'+test 
                if not re.search('\$$', test): test = test+'$'

                stations.extend([x for x in self.stachan_cache if re.search(test,x)])

        for s in stations: 
            keys[s] = 1 

        stations = keys.keys()

        if self.config.verbose:
            log.msg("Stations(): convert_sta(%s) => %s" % (list,stations))

        return stations

    #}}}

    def convert_chan(self, list=['.*'], stations=['.*']):
    #{{{ get list of stations for the query

        if not list: list = ['.*'] 
        if not stations: stations = ['.*'] 

        if self.config.debug: log.msg("Stations(): convert_chan(%s,%s)" % (list,stations))

        channels = []
        station_list = self.convert_sta(stations)
        keys = {} 

        for test in list:
            for sta in station_list:

                if re.search('^\w*$', test): 

                    channels.extend([x for x in self.stachan_cache[sta] if x == test])

                else:

                    if not re.search('^\^', test): test = '^'+test 
                    if not re.search('\$$', test): test = test+'$'

                    channels.extend([x for x in self.stachan_cache[sta] if re.search(test,x)])


        for s in channels: 
            keys[s] = 1 

        channels = keys.keys()

        if self.config.verbose:
            log.msg("Stations(): convert_chan(%s,%s) => %s" % (stations,list,channels))

        return channels

    #}}}

    def lis(self):
            return self.stachan_cache.keys()
#}}}

class Events():
#{{{ Class to load information about events
    """
    Data structure and functions to query for events
    """

    def __init__(self, db, config):
    #{{{ Load class and get the data

        self.config = config
        self.first = True
        self.dbcentral = db
        self.event_cache = defaultdict(list)
        self.offset = -1 

        #
        # Load null class
        #
        self.nulls = db_nulls(db,self.config.debug,['events','event','origin','assoc','arrival']) 

        #
        # Get data from tables
        #
        self._running_loop = False
        ev_loop = LoopingCall(deferToThread,self._inThread)
        #ev_loop = LoopingCall(reactor.callInThread,self._inThread)
        #ev_loop = LoopingCall(self._inThread)
        ev_loop.start(600,now=True)

    #}}}

    def _cb(self,result):
    #{{{

        #log.msg("Class Events: got result from thread: %s" % result)
        self.event_cache = result
        self.first = False

    #}}}

    def _inThread(self):
    #{{{
        result = pool.apply_async(Update_Events,(self.dbcentral,self.first,self._times(),self.config.debug),callback=self._cb)
        #return result.get()

    #}}}

    def __getitem__(self,i):
    #{{{ Iteration context

        return self.event_cache.keys()[i]

    #}}}

    def next(self):
    #{{{ method to produce items util Stopiteration is reaised

        if len(self.event_cache.keys()) == self.offset:

            self.offset = -1
            raise StopIteration

        else:

            self.offset += 1
            return self.event_cache.keys()[self.offset]

    #}}}

    def __str__(self):
    #{{{ Nicely print of elements in class
        """
        end-user/application display of content using log.msg() or log.msg()
        """

        if self.config.debug:

            for orid in self.event_cache:
                log.msg("\nEvents(): %s(%s)" % (orid,self.event_cache[orid]))

        else: 

            log.msg("Events(): %s" % (self.event_cache.keys()))

    #}}}

    def __call__(self, value):
    #{{{ Function calls to the class
        """
        method to intercepts data requests.
        """

        value = _isNumber(value)

        if not value:
            return _error("Not a valid number in function call: %s" % value)

        if value in self.event_cache:

            return self.event_cache[value]

        else:

            log.msg("Class Events(): %s not in database." % value)
            return False
    #}}}

    def list(self):
        return self.event_cache.keys()

    def table(self):
        return self.event_cache

    def _times(self):
    #{{{ function to return max and min times of wfdisc
        """
        Get min and max times for wfdisc
        """

        data = {}

        #for db_name in self.dbcentral.list_dbs():
        for dbname in self.dbcentral.list():

            end = 0
            start = 0

            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='wfdisc')
                records = db.query(datascope.dbRECORD_COUNT)

            except:
                records = 0


            if records:

                start = db.ex_eval('min(time)')
                end = db.ex_eval('max(endtime)')

                if not 'start' in data:
                    data['start'] = start

                elif data['start'] > start:
                    data['start'] = start

                if not 'end' in data:
                    data['end'] = end

                elif data['end'] < end:
                    data['end'] = end

        return data

    #}}}

    def time(self,orid_time,window=5):
    #{{{ Function to get possible matches of events for some epoch time.
        """
        Look for event id close to a value of epoch time + or - window time in seconds. 
        If no widow time is provided the default is 5 secods.
        """

        results = {}

        #
        # If running in simple mode we don't have access to the tables we need
        #
        if self.config.simple:
            return results

        orid_time = _isNumber(orid_time)

        if not orid_time:
            return _error("Not a valid number in function call: %s" % orid_time)
        
        start = float(orid_time)-float(window)
        end   = float(orid_time)+float(window)

        dbname = self.dbcentral(orid_time)

        if not db:
            return _error("No match for orid_time in dbcentral object: (%s,%s)" % (orid_time,self.dbcentral(orid_time)))

        try: 
            db = datascope.dbopen( dbname , 'r' )
            db.lookup( table='origin')
            db.query(datascope.dbTABLE_PRESENT) 
        except Exception,e:
            return _error("Exception on Events() time(%s): Error on db pointer %s [%s]" % (orid_time,db,e))

        db.subset( 'time >= %f' % start )
        db.subset( 'time <= %f' % end )

        try:
            db = datascope.dbopen( dbname , 'r' )
            db.lookup( table='wfdisc' )
            records = db.query(datascope.dbRECORD_COUNT)

        except:
            records = 0

        if records:

            for i in range(records):

                db.record = i

                (orid,time) = db.getv('orid','time')

                orid = _isNumber(orid)
                time = _isNumber(time)
                results[orid] = time

        return results

    #}}}

    def _get_event_cache(self):
    #{{{ private function to load the data from the tables

        if self.config.debug: 
            log.msg("Events(): update cache.")

        times = self._times()

        for dbname in self.dbcentral.list():

            event_cache = defaultdict(dict)

            if self.config.debug: 
                log.msg("Events(): _get_event_cache  db[%s]" % (dbname) )

            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='event')
                records = db.query(datascope.dbRECORD_COUNT)

            except:
                records = 0

            if records:

                try:
                    db.join( 'origin' )
                    db.subset( 'orid == prefor' )
                except:
                    pass

            else:

                try:
                    db.lookup( table='origin' )
                except:
                    pass


            try:
                records = db.query(datascope.dbRECORD_COUNT)
            except:
                records = 0


            if not records: 
                log.msg('Events(): ERROR: No records to work on any table\n\n')
                return event_cache

            if self.config.debug: 
                log.msg("Events(): origin db_pointer: [%s,%s,%s,%s]" % (db['database'],db['table'],db['field'],db['record']))

            if 'start' in times:

                db.subset("time > %f" % float(times['start']))

            if 'end' in times:

                db.subset("time < %f" % float(times['end']))

            try:
                records = db.query(datascope.dbRECORD_COUNT)
            except:
                records = 0

            if not records: 
                log.msg('Events(): ERROR: No records after time subset\n\n')
                return

            for i in range(records):

                db.record = i

                (orid,time,lat,lon,depth,auth,mb,ml,ms,nass) = db.getv('orid','time','lat','lon','depth','auth','mb','ml','ms','nass')

                if auth == self.nulls('auth'):
                    auth = '-'

                if orid == self.nulls('orid'):
                    orid = '-'

                if time == self.nulls('time'):
                    time = '-'
                else:
                    time = "%0.2f" % time

                if lat == self.nulls('lat'):
                    lat = '-'
                else:
                    lat = "%0.2f" % lat

                if lon == self.nulls('lon'):
                    lon = '-'
                else:
                    lon = "%0.2f" % lon

                if depth == self.nulls('depth'):
                    depth = '-'
                else:
                    depth = "%0.2f" % depth

                if mb == self.nulls('mb'):
                    mb = '-'
                else:
                    mb = "%0.1f" % mb

                if ms == self.nulls('ms'):
                    ms = '-'
                else:
                    ms = "%0.1f" % ms

                if ml == self.nulls('ml'):
                    ml = '-'
                else:
                    ml = "%0.1f" % ml

                if nass == self.nulls('nass'):
                    nass = '-'
                else:
                    nass = "%d" % nass


                event_cache[orid] = {'time':time, 'lat':lat, 'lon':lon, 'depth':depth, 'auth':auth, 'mb':mb, 'ms':ms, 'ml':ml, 'nass':nass}

                if mb > 0:
                    event_cache[orid]['magnitude'] = mb
                    event_cache[orid]['mtype'] = 'Mb'
                elif ms > 0:
                    event_cache[orid]['magnitude'] = ms
                    event_cache[orid]['mtype'] = 'Ms'
                elif ml > 0:
                    event_cache[orid]['magnitude'] = ml
                    event_cache[orid]['mtype'] = 'Ml'
                else:
                    event_cache[orid]['magnitude'] = '-'
                    event_cache[orid]['mtype'] = '-'


        if self.config.verbose:
            log.msg("Events(): Updating cache. (%s)" % len(event_cache))

        return event_cache
#}}}

    def phases(self, min, max):
    #{{{ function to return dictionary of arrivals
        """
        Go through station channels to retrieve all
        arrival phases
        """
        if self.config.verbose: log.msg("Events():phases(%s,%s) "%(min,max))
        phases = defaultdict(dict)

        assoc   = False
        arrival = False

        dbname = self.dbcentral(min)

        if self.config.verbose: log.msg("Events():phases(%s,%s) db:(%s)"%(min,max,dbname))
        if not dbname: return phases

        try: 
            db = datascope.dbopen (dbname , 'r' )
            db.lookup( table='arrival' )
            db.join( 'assoc' )
            nrecs = db.query(datascope.dbRECORD_COUNT)

        except:
            try:
                db = datascope.dbopen (dbname , 'r' )
                db.lookup( table='arrival')
                nrecs = db.query(datascope.dbRECORD_COUNT)

            except Exception,e:
                return _error("Events: Exception on phases(): %s" % e,phases)


        try: 
            nrecs = db.query(datascope.dbRECORD_COUNT)
        except Exception,e:
            return _error("Events: Exception on phases(): %s" % e,phases)

        try:
            db.subset("%s <= time && time <= %s" % (float(min),float(max)) )
            nrecs = db.query(datascope.dbRECORD_COUNT)
        except:
            nrecs = 0

        for p in range(nrecs):

            db.record = p

            if assoc:

                Sta, Chan, ArrTime, Phase = db.getv('sta','chan','time','phase')
                StaChan = Sta + '_' + Chan
                phases[StaChan][ArrTime] = Phase

            else:

                Sta, Chan, ArrTime, Phase = db.getv('sta','chan','time','iphase')
                StaChan = Sta + '_' + Chan
                phases[StaChan][ArrTime] = '_' + Phase


            if self.config.debug: log.msg("Phases(%s):%s" % (StaChan,Phase))

        if self.config.debug:  log.msg("Events: phases(): t1=%s t2=%s [%s]" % (min,max,phases))

        return phases
    #}}}

#}}}

class db_nulls():
#{{{ Class to store null values for every field in the schema

    def __init__(self,db,debug,tables=[]):
    #{{{ Load class and test databases

        """
        This should be a dbcentral object
        """
        self.dbcentral = db
        self.tables    = tables
        self.debug    = debug

        """
        Load values from databases
        """
        self._get_nulls()

    #}}}

    def __str__(self):
    #{{{ Nicely print values
        """
        end-user/application display of content using log.msg() or log.msg()
        """
        text = 'Null values for databases: %s' % self.dbcentral.list()

        for value in self.null_vals.keys():
            text += "\t%s: %s" % (value,self.null_vals[value])

        return text
    #}}}

    def __call__(self, element=None):
    #{{{ Function calls
        """
        method to intercepts requests.
        """
        if element is None:

            return _error("\nERROR: db_nulls(): No element named (%s) in object.\n\n" % element)


        if element in self.null_vals:

            return self.null_vals[element]

        else:

            return _error("\nERROR: db_nulls(): No value for (%s)\n\n" % element)
    #}}}

    def _get_nulls(self):
    #{{{ Private function to load values from dbs
        """
        Go through the tables on the database and return
        dictionary with NULL values for each field.
        """

        self.null_vals = defaultdict(lambda: defaultdict(defaultdict))

        """
        We will assume all databases have the same schema. 
        Get the first only.
        """
        dbname = self.dbcentral.list()[0]

        try:
            db = datascope.dbopen( dbname , "r" )

        except Exception, e:
            sys.exit('\n\nERROR: dbopen(%s)=>(%s)\n\n' % (dbname,e) )


        if self.debug: log.msg("Class Db_Nulls: Looking for tables:%s" % self.tables)

        """
        Loop over all tables
        """
        for table in db.query(datascope.dbSCHEMA_TABLES):

            if len(self.tables) > 0 and table not in self.tables: continue

            if self.debug: log.msg("Class Db_Nulls: Test table:[%s]" % table)

            db.lookup( '',table,'','dbNULL')

            """
            Test every field
            """
            try:
                db.query(datascope.dbTABLE_FIELDS)
            except:
                pass

            else:

                for field in db.query(datascope.dbTABLE_FIELDS):

                    self.null_vals[field] = db.getv(field)[0]

                    if self.debug: log.msg("\t\tClass Db_Nulls: table:[%s] field(%s):[%s]" % (table,field,self.null_vals[field]))

    #}}}

#}}}

class QueryParser(resource.Resource):
#{{{
    #
    # Serve HTTP queries.
    #
    isLeaf = False

    allowedMethods = ("GET")

    def __init__(self,db,config):
    #{{{

        self.config = config
        self.dbname = db
        self.loading = True
        self.loading_events = True
        self.loading_stations = True

        #
        # Initialize Classes
        #
        if self.config.verbose: print 'Load class resorce.Resource.__init__(self)'
        resource.Resource.__init__(self)


        #
        # Open db using dbcentral CLASS
        #
        if self.config.debug: print "Create dbcentral object with database(%s)." % self.dbname
        self.db = dbcentral.dbcentral(self.dbname,self.config.nickname,self.config.debug)

        if self.config.debug: self.db.info()

        if not self.db.list(): sys.exit('\nERROR: No databases to use! (%s)\n\n'% self.dbname)


        self.tvals = {
                "filters": '<option value="None">None</option>',
                "dbname": self.dbname,
                "event_controls": '',
                "application_title": self.config.application_title,
            }

        for filter in self.config.filters:
            self.tvals['filters'] += '<option value="'+self.config.filters[filter].replace(' ','_')+'">'
            self.tvals['filters'] += filter
            self.tvals['filters'] += '"</option>'

        if self.config.display_arrivals:
            self.tvals['display_arrivals'] = 'checked="checked"'
        else:
            self.tvals['display_arrivals'] = ''

        if self.config.display_points:
            self.tvals['display_points'] = 'checked="checked"'
        else:
            self.tvals['display_points'] = ''


        pool.apply_async(init_Reactor,(self.db,self.config.simple,self.config.debug,self.tvals),callback=self._cb_init)

    #}}}

    def _cb_init(self,result):
    #{{{

        self.tvals = result[0]
        self.config.simple = result[1]

        if self.config.debug: log.msg("QueryParser(): Init Done!") 

        self.loading = False

        d = deferToThread(Stations, self.db, self.config)
        d.addCallback(self._cb_init_Station)

        if not self.config.simple:
            d = deferToThread(Events, self.db, self.config)
            d.addCallback(self._cb_init_Event)
        else:
            if self.config.debug: log.msg("QueryParser(): Don't init event class. Running simple mode now!" )
            self.loading_events = False

        #pool.apply_async(Stations,(self.db,self.config),callback=self._cb_init_Station)
        #pool.apply_async(Events,(self.db,self.config),callback=self._cb_init_Event)

    #}}}

    def _cb_init_Station(self,result):
    #{{{

        self.stations = result

        if self.config.debug: log.msg("QueryParser(): Init station class. Done!" )

        self.loading_stations = False

    #}}}

    def _cb_init_Event(self,result):
    #{{{

        self.events = result

        if self.config.debug: log.msg("QueryParser(): Init event class. Done!" )

        self.loading_events = False

    #}}}

    def getChild(self, name, uri): 
    #{{{
        if self.config.debug: log.msg("getChild()")
        return self
    #}}}

    def render_GET(self, uri):
    #{{{
        if self.config.debug: log.msg("QueryParser(): render_GET(): uri: %s" % uri)

        #if config.debug: log.msg('QUERY: %s ' % uri)

        #(host,port) = uri.getHeader('host').split(':', 1)
        #log.msg('QUERY: %s ' % uri)
        #log.msg('Hostname => [%s:%s]'% (host,port))
        #log.msg('Host=> [%s]'% uri.host)
        #log.msg('socket.gethostname() => [%s]'% socket.gethostname())
        #log.msg('socket.getsockname() => [%s]'% uri.host.getsockname())
        #uri.setHost(host,config.port)


        #print self.loading
        #print self.loading_stations
        #print self.loading_events
        if self.loading or self.loading_stations or self.loading_events:
            uri.setHeader("content-type", "text/html")
            uri.setHeader("response-code", 500)
            return "<html><head><title>%s</title></head><body><h1>DBWFSERVER:</h1></br><h3>Server Loading!</h3></body></html>" % self.config.application_name


        #pool.apply_async(render_uri,(self.dbcentral,uri,self.stations,self.events,self.conf),callback=self.uri_callback)
        if self.config.debug: log.msg("QueryParser(): render_GET() - build deferred object.")

        d = defer.Deferred()
        d.addCallback( self.render_uri )
        d.addCallback( uri.write )
        d.addCallback( lambda x: uri.finish() )
        d.addErrback( lambda x: self.defer_error(uri,x) )
        d.addErrback( lambda x: uri.finish() )
        reactor.callInThread(d.callback, uri)

        if self.config.debug: log.msg("QueryParser(): render_GET() - return server.NOT_DONE_YET")

        return server.NOT_DONE_YET

    #}}}

    def render_uri(self, uri):
    #{{{

        if self.config.debug: 
            log.msg('')
            log.msg('QueryParser(): render_uri(%s)' % uri)
            log.msg('QueryParser(): render_uri() uri.uri:%s' % uri.uri)
            log.msg('QueryParser(): render_uri() uri.args:%s' % (uri.args) )
            log.msg('QueryParser(): render_uri() uri.prepath:%s' % (uri.prepath) )
            log.msg('QueryParser(): render_uri() uri.postpath:%s' % (uri.postpath) )
            log.msg('QueryParser(): render_uri() uri.path:%s' % (uri.path) )
            log.msg('')


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
            "proxy":             "''",
            "proxy_url":         self.config.proxy_url,
            "style":             self.config.style,
            "meta_query":        'false'
        } )

        if self.config.proxy_url: response_meta['proxy'] = "'" + self.config.proxy_url + "'"


        #
        # remove all empty  elements
        # This (localhost:8008/stations/) is the same as # (localhost:8008/stations) 
        #
        path = uri.prepath
        while True:
            try: 
                path.remove('')
            except: 
                break


        # Parse all elements on the list
        query = self._parse_request(path)

        log.msg('')
        log.msg('QueryParser(): render_uri() uri.prepath => path(%s)[%s]' % (len(path),path) )
        log.msg('QueryParser(): render_uri() query => [%s]' % query)
        log.msg('')

        if query['data']:
        #{{{

                if self.config.debug: log.msg('QueryParser(): render_uri() "data" query')
                uri.setHeader("content-type", "application/json")

                if len(path) == 0:
                #{{{ ERROR: we need one option
                    log.msg('QueryParser(): render_uri() ERROR: Empty "data" query!')
                    uri.setHeader("content-type", "text/html")
                    uri.setHeader("response-code", 500)
                    return json.dumps( "Invalid data query (%s)" % uri.uri )
                #}}}

                elif path[0] == 'events':
                #{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => events')
                    if self.config.simple: return json.dumps({})

                    elif len(path) == 3:
                        return json.dumps(self.events.phases(path[1],path[2]))

                    else:
                        return json.dumps(self.events.table())
                #}}}

                elif path[0] == 'dates':
                #{{{
                    """
                    Return list of yearday values for time in db
                    for all stations in the cluster of dbs.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => dates')

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

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => stations')

                    if len(path) == 2: 
                        return json.dumps( self.stations.convert_sta(path[1].split('-')) )

                    if len(path) == 3: 
                        for sta in self.stations.convert_sta(path[1].split('-')):
                            for chan in self.stations.convert_chan(path[2].split('-')):
                                if sta not in response_data: response_data[sta] = []
                                response_data[sta].extend(self.stations.convert_chan([chan],[sta]))

                        return json.dumps(response_data)


                    return json.dumps(self.stations.convert_sta())
                #}}}

                elif path[0] == 'channels':
                #{{{
                    """
                    Return channels list as JSON objects. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => channels')

                    if len(path) == 2:
                        return json.dumps( self.stations.convert_chan(path[1].split('-')) )

                    return json.dumps(self.stations.convert_chan())
                #}}}

                elif path[0] == 'filters':
                #{{{
                    """
                    Return list of filters as JSON objects. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => filters')

                    return json.dumps(self.config.filters, sort_keys=True)
                #}}}

                elif path[0] == 'wf':
                #{{{
                    """
                    Return JSON object of data. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => wf')

                    query = self._parse_request(path)

                    #return json.dumps( get_data(self.db,self.config,self.stations,query['sta'],query['chan'],query['start'],query['end'],query['filter']) )

                    stations = self.stations.convert_sta(query['sta'])
                    channels = self.stations.convert_chan(query['chan'],stations)

                    if self.config.debug: print "QueryParser(): render_uri(): path == wf(): Get data for %s.%s" % (query['sta'],query['chan'])

                    if self.config.debug: print "QueryParser(): render_uri(): path == wf(): convert stations => %s" % stations
                    if self.config.debug: print "QueryParser(): render_uri(): path == wf(): convert channels => %s" % channels

                    if not stations:
                        response_data['error'] = "[%s] not valid station value" % query['sta']
                        print response_data['error']
                        return json.dumps( response_data )

                    if not channels:
                        response_data['error'] = "[%s] not valid channel [%s]" % (channel,station)
                        print response_data['error']
                        return json.dumps( response_data )

                    if self.config.debug: print "QueryParser(): render_uri(): path == wf(): prepare vars for [%s].[%s] " % (stations,channels)

                    start = isNumber(query['start'])
                    end   = isNumber(query['end'])

                    for sta in stations:
                        temp_dic = self.stations(sta)
                        for chan in channels:

                            if not start: start = temp_dic[chan]['end'] - self.config.default_time_window

                            if not start: start = stock.now()

                            if not end: end = start + self.config.default_time_window

                            if self.config.debug: print "\tQueryParser(): render_uri(): path == wf(): extract [%s][%s][%s][%s] " % (sta,chan,start,end)
                            response_data[sta][chan] = defaultdict(dict)
                            response_data[sta][chan]['end']      = end
                            response_data[sta][chan]['start']    = start
                            response_data[sta][chan]['metadata'] = temp_dic[chan]
                            points = 0


                            if temp_dic[chan]['samprate']: points = int( (end-start) * temp_dic[chan]['samprate'] )

                            if self.config.debug: print "\tQueryParser(): render_uri(): path == wf(): points:%s canvas:%s threshold:%s" % (points,self.config.canvas_size_default,self.config.binning_threshold)

                            if points >  (self.config.binning_threshold * self.config.canvas_size_default):
                                binsize = points/self.config.canvas_size_default
                            else:
                                binsize = 0

                            if self.config.debug: print "\tQueryParser(): render_uri(): path == wf(): binsize:%s " % binsize

                            if self.config.debug: print "\tQueryParser(): render_uri(): path == wf(): get dbname for db(%s) " % start
                            try:
                                dbname = self.db(start)
                            except Exception,e:
                                print '\n\nget_data(): ERROR: Cannot get db for this time %s [%s][%s]\n\n' % (start,Exception,e)


                            if self.config.debug: print "\tQueryParser(): render_uri(): path == wf(): dbname for db(%s) => %s " % (start,dbname)

                            if not dbname: continue

                            try:
                                res = pool.apply_async( get_data, (dbname,self.config.debug,sta,chan,start,end,binsize,query['filter']) )
                                response_data[sta][chan].update( res.get() )
                            except Exception,e:
                                response_data['error'] = "QueryParser(): render_uri(): ERROR in pool.apply_async(get_data) %s %s " % (Exception,e)
                                print response_data['error']
                                return json.dumps( response_data )


                    return json.dumps( response_data )

                #}}}

                elif path[0] == 'coverage':
                #{{{
                    """
                    Return coverage tuples as JSON objects. For client ajax calls.
                    """

                    query = self._parse_request(path)

                    return json.dumps( self.coverage(query['sta'],query['chan'],query['start'],query['end']) )

                #}}}

                elif path[0] == 'meta':
                #{{{
                    """
                    *** DEBUGGING TOOL ***
                    TEST metaquery parsing response. 
                    Return json with meta-query data for further ajax uri.
                    """

                    query = self._parse_request(path)

                    if 'start' in query and not self.config.simple: 

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

        elif not path: 
            pass

        elif path[0] == 'wf':
            #{{{
                """
                Parse query for data uri. Return html with meta-query data for further ajax uri.
                """

                response_meta['meta_query'] = defaultdict(lambda: defaultdict(defaultdict))

                response_meta['meta_query']['traces'] = {};

                for sta in query['sta']:
                    temp_dic = self.stations(sta)

                    for chan in query['chan']:
                        if not chan in temp_dic: continue

                        if sta not in response_meta['meta_query']['traces']: response_meta['meta_query']['traces'][sta] = []
                        response_meta['meta_query']['traces'][sta].extend([chan])


                response_meta['meta_query']['sta'] = query['sta']
                response_meta['meta_query']['chan'] = query['chan']
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
                
                return  Template(open(self.config.plot_template).read()).safe_substitute(response_meta)

            #}}}

        else: 
        #{{{ ERROR
            uri.setHeader("content-type", "text/html")
            uri.setHeader("response-code", 500)
            return json.dumps( "Invalid query (%s)" % uri.uri )
        #}}}

        if 'mode' in uri.args: response_meta['setupUI'] = json.dumps(uri.args)

        response_meta.update(self.tvals)

        return  Template(open(self.config.template).read()).safe_substitute(response_meta)

    #}}}

    def _parse_request(self,args):
        # {{{

        """
        Strict format for uri:
            localhost/

            localhost/wf/sta

            localhost/wf/sta/chan

            localhost/wf/sta/chan/time

            localhost/wf/sta/chan/time/time

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
        if self.config.debug: log.msg("QueryParser(): _parse_request(): URI: %s" % str(args) ) 

        uri  = defaultdict()
        tendemp = defaultdict(lambda: defaultdict(defaultdict))
        time_window = self.config.default_time_window

        uri.update( { 
            "sta":[],
            "chan":[],
            "end":0,
            "data":False,
            "start":0,
            "filter":None,
            "time_window":False
        } )

        if 'data' in args:
            if self.config.verbose: log.msg("QueryParser() _parse_request(): data query!") 
            uri['data'] = True
            args.remove('data')
            return uri

        # localhost/sta
        if len(args) == 2:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))

        # localhost/sta/chan
        elif len(args) == 3:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['chan'] = self.stations.convert_chan(args[2].split('-'),uri['sta'])

        # localhost/sta/chan/time
        elif len(args) == 4:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['chan'] = self.stations.convert_chan(args[2].split('-'),uri['sta'])
            uri['start'] = args[3]

        # localhost/sta/chan/time/time
        elif len(args) == 5:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['chan'] = self.stations.convert_chan(args[2].split('-'),uri['sta'])
            uri['start'] = args[3]
            uri['end'] = args[4]

        # localhost/sta/chan/time/time/filter
        elif len(args) == 6:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['chan'] = self.stations.convert_chan(args[2].split('-'),uri['sta'])
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
        #if uri['sta']:
        #    args[1] = '-'.join(uri['sta'])

        #
        # Fix start
        #
        if uri['start']:
            if isNumber(uri['start']):
                uri['start'] = isNumber(uri['start'])
            elif uri['start'] == 'hour': 
                uri['start'] = 0
                time_window = 3600
            elif uri['start'] == 'day': 
                uri['start'] = 0
                time_window = 86400
            elif uri['start'] == 'week':
                uri['start'] = 0
                time_window = 604800
            elif uri['start'] == 'month':
                uri['start'] = 0
                time_window = 2629743
            else:
                uri['start'] = 0

        #
        # Fix end
        #
        if uri['end']:
            if isNumber(uri['end']):
                uri['end'] = isNumber(uri['end'])
            elif uri['end'] == 'hour': 
                uri['end'] = 0
                time_window = 3600
            elif uri['end'] == 'day': 
                uri['end'] = 0
                time_window = 86400
            elif uri['end'] == 'week':
                uri['end'] = 0
                time_window = 604800
            elif uri['end'] == 'month':
                uri['end'] = 0
                time_window = 2629743
            else:
                uri['end'] = 0

        #
        # Build missing times if needed
        #
        if uri['sta'] and uri['chan']: 
            if not uri['start'] and not uri['end']:
                uri['end'] = self.stations.max_time(uri['sta'])
                if not uri['end']: uri['end'] = stock.now()
                uri['start'] = uri['end'] - time_window
                uri['end']   = isNumber(uri['end'])
                uri['start'] = isNumber(uri['start'])

            elif not uri['end']:
                uri['end'] = uri['start'] + time_window

            elif not uri['start']:
                uri['start'] = uri['end'] - time_window

        if self.config.verbose: 
            log.msg("QueryParser(): _parse_request(): [sta:%s chan:%s start:%s end:%s]" % (uri['sta'], uri['chan'], uri['start'], uri['end']) ) 

        return uri
        # }}}

    def uri_callback(self, results):
    #{{{

        uri = results[0]
        data = results[1]

        #
        # Prints Error back to the browser.
        #
        #log.msg('\n\n%s\n\n' % text)
        #uri.setHeader("content-type", "text/html")
        #uri.setHeader("response-code", 400)
        #uri.write('ERROR in query: \n %s' % text)

        uri.write(data)
        if self.debug: log.msg('\n\nDATA: %s\n\n' % data)

        uri.finish()

    #}}}


#}}}

