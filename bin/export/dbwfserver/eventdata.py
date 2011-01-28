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

class db_nulls():
#{{{ Class to store null values for every field in the schema

    def __init__(self,db,tables=[]):
    #{{{ Load class and test databases

        """
        This should be a dbcentral object
        """
        self.dbcentral = db
        self.tables    = tables

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

        else:
            config.dbpointers.append(db)



        if config.debug: log.msg("Class Db_Nulls: db: %s" % db)
        if config.debug: log.msg("Class Db_Nulls: Looking for tables:%s" % self.tables)

        """
        Loop over all tables
        """
        for table in db.query(datascope.dbSCHEMA_TABLES):

            if len(self.tables) > 0 and table not in self.tables: continue

            if config.debug: log.msg("Class Db_Nulls: Now with table:[%s]" % table)

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

                    if config.debug: log.msg("\tClass Db_Nulls: table:[%s] field(%s):[%s]" % (table,field,self.null_vals[field]))

    #}}}

#}}}

class Stations():
#{{{ Class to load information about stations
    """
    Data structure and functions to query for stations
    """

    def __init__(self, db):
    #{{{ Load class and get the data

        self.first = True
        self.dbcentral = db
        self.stachan_cache = defaultdict(lambda: defaultdict(defaultdict))
        self.offset = -1
        self.loading = True

        #
        # Load null class
        #
        self.nulls = db_nulls(db,['wfdisc','sensor','instrument']) 

        #
        # Run update in loop call
        #
        self._running_loop = False
        #stachan_loop = LoopingCall(reactor.callInThread,self._inThread)
        stachan_loop = LoopingCall(deferToThread,self._inThread)
        stachan_loop.start(120,now=True)

    #}}}

    def _inThread(self):
    #{{{
        if self._running_loop:
            log.msg("Class Stations: Update taking longer than loop restart time...")
            return 

        #
        # Wait if we are cleaning dbpointers
        #
        while config.locked: pass

        if config.debug: log.msg("Class Stations: Update class object...")
        self._running_loop = True
        config.locked = True

        try:
            #self.stachan_cache = risp.risp_s(10485760,self._get_stachan_cache)
            self.stachan_cache = self._get_stachan_cache()
        except Exception, e:
                print '\nERROR: Events._inThread() => (%s)' % e

        if config.debug: log.msg("Class Stations: Done updating class object...")
        self._running_loop = False
        config.locked = False
        self.loading = False

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

        if config.verbose: log.msg("class Stations():")

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
            if config.debug: log.msg("Stations(%s) => %s" % (station,self.stachan_cache[station]))
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

        if config.debug: 
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

            else:
                config.dbpointers.append(db)


            if not records: sys.exit('Stations(): ERROR: No records to work on any  table\n\n')

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

                if config.debug: log.msg("Station(): (simple loop) %s.%s[%s,%s,%s]" % (sta,chan,calib,segtype,srate))


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

                            if config.debug: log.msg("Station(): %s.%s[%s,%s]" % (sta,chan,start_day,end_day))

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

                            if config.debug: log.msg("Station(): %s.%s[%s,%s]" % (sta,chan,start_day,end_day))

                            stachan_cache[sta][chan]['dates'] = [start_day,end_day]

        if config.verbose:
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

        if config.debug: log.msg('Stations(): max_time(%s)=>%s' % (test,cache) )
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

                if config.debug: log.msg("Stations(): dates(%s,%s)=>%s" % (sta,chan,self.stachan_cache[sta][chan]['dates']) )

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

        if config.debug: log.msg("Stations(): dates(%s)=>%s" % (test,cache) )

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

        while True:
            try:
                list.remove('')
            except:
                break

        for test in list:
            for sta in self.stachan_cache:
                if re.search(test, sta): 
                    stations.append(sta)

        for s in stations: 
            keys[s] = 1 

        stations = keys.keys()
        
        # Limit stations to 4
        #if len(stations) > 3: 
        #    stations = stations[:4]

        if config.verbose:
            log.msg("Stations(): convert_sta(%s) => %s" % (list,stations))

        return stations

    #}}}

    def convert_chan(self, stations=['.*'], list=['.*']):
    #{{{ get list of stations for the query

        channels = []
        keys = {} 

        while True:
            try:
                stations.remove('')
            except:
                break

        while True:
            try:
                list.remove('')
            except:
                break

        for test in list:
            for sta in self.convert_sta(stations):
                for chan in self.stachan_cache[sta]:
                    if re.search(test, chan): 
                        channels.append(chan)

        for s in channels: 
            keys[s] = 1 

        if config.verbose:
            log.msg("Stations(): convert_chan(%s,%s) => %s" % (stations,list,keys.keys()))

        return keys.keys()

    #}}}

    def list(self):
            return self.stachan_cache.keys()
#}}}

class Events():
#{{{ Class to load information about events
    """
    Data structure and functions to query for events
    """

    def __init__(self, db):
    #{{{ Load class and get the data

        self.first = True
        self.dbcentral = db
        self.event_cache = defaultdict(list)
        self.offset = -1 
        self.loading = True

        #
        # Load null class
        #
        self.nulls = db_nulls(db,['events','event','origin','assoc','arrival']) 

        #
        # Get data from tables
        #
        self._running_loop = False
        #ev_loop = LoopingCall(reactor.callInThread,self._inThread)
        ev_loop = LoopingCall(deferToThread,self._inThread)
        ev_loop.start(120,now=True)

    #}}}

    def _inThread(self):
    #{{{
        if self._running_loop:
            log.msg("Class Events: Update taking longer than loop restart time...")
            return

        #
        # Wait if we are cleaning dbpointers
        #
        while config.locked: pass

        if config.verbose: log.msg("Class Events: Update class object...")
        self._running_loop = True
        config.locked = True

        try:
            #self.event_cache = risp.risp_s(10485760,self._get_event_cache)
            self.event_cache = self._get_event_cache()
        except Exception, e:
                print '\nERROR: Events._inThread() => (%s)' % e

        if config.verbose: log.msg("Class Events: Done updating class object...")
        self._running_loop = False
        config.locked = False
        self.loading = False

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

        if config.debug:

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

            else:
                config.dbpointers.append(db)



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
        if config.simple:
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
        else:
            config.dbpointers.append(db)


        db.subset( 'time >= %f' % start )
        db.subset( 'time <= %f' % end )

        try:
            db = datascope.dbopen( dbname , 'r' )
            db.lookup( table='wfdisc' )
            records = db.query(datascope.dbRECORD_COUNT)

        except:
            records = 0

        else:
            config.dbpointers.append(db)

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

        if config.debug: 
            log.msg("Events(): update cache.")

        times = self._times()

        for dbname in self.dbcentral.list():

            event_cache = defaultdict(dict)

            if config.debug: 
                log.msg("Events(): _get_event_cache  db[%s]" % (dbname) )

            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='event')
                records = db.query(datascope.dbRECORD_COUNT)

            except:
                records = 0

            else:
                config.dbpointers.append(db)

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

            if config.debug: 
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


        if config.verbose:
            log.msg("Events(): Updating cache. (%s)" % len(event_cache))

        return event_cache
#}}}

    def phases(self, min, max):
    #{{{ function to return dictionary of arrivals
        """
        Go through station channels to retrieve all
        arrival phases
        """
        if config.verbose: log.msg("Events():phases(%s,%s) "%(min,max))
        phases = defaultdict(dict)

        assoc   = False
        arrival = False

        dbname = self.dbcentral(min)

        if config.verbose: log.msg("Events():phases(%s,%s) db:(%s)"%(min,max,dbname))
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

            else:
                config.dbpointers.append(db)

        else:
            config.dbpointers.append(db)


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


            if config.debug: log.msg("Phases(%s):%s" % (StaChan,Phase))

        if config.debug:  log.msg("Events: phases(): t1=%s t2=%s [%s]" % (min,max,phases))

        return phases
    #}}}

#}}}
