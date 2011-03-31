from __main__ import *

#
# Global Functions
# 
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

#
# Global Classes
# 
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

        try:
            import antelope.datascope as datascope
        except Exception,e:
            print "Problem loading Antelope's Python libraries. (%s)" % e
            sys.exit()


        self.null_vals = {}

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

        try:
            db.close()
        except:
            pass

    #}}}

#}}}

class Stations():
#{{{ Class to load information about stations
    """
    Data structure and functions to query for stations
    """

    def __init__(self, db, config):
    #{{{ Load class and get the data

        print "Stations: init() class"

        self.config = config
        self.first = True
        self.dbcentral = db
        self.stachan_cache = {}
        self.offset = -1

        #
        # Load null class
        #
        print "Stations: self.nulls"
        self.nulls = db_nulls(db,self.config.debug,['wfdisc']) 

        print "Stations: call _get_stachan_cache"
        self._get_stachan_cache()

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

        if self.config.verbose: print "class Stations():"

        for st in self.stachan_cache.keys():
            chans = self.stachan_cache[st].keys()
            print "\t%s: %s" % (st,chans)

    #}}}

    def __call__(self, station):
    #{{{ Function calls to the class.
        """
        method to intercepts data requests.
        """


        if station in self.stachan_cache:
            if self.config.debug: print "Stations(%s) => %s" % (station,self.stachan_cache[station])
            return self.stachan_cache[station]

        else:
            print "Stations(): No value for station:%s" % station
            for sta in self.stachan_cache:
                for chan in self.stachan_cache[sta]:
                    print '%s.%s => %s' % (sta,chan,self.stachan_cache[sta][chan])

        return False
    #}}}

    def _get_stachan_cache(self):
    #{{{ private function to load data

        if self.config.debug: print "Stations: _get_stachan_cache(): starting"

        try:
            if self.config.debug: print "Stations: _get_stachan_cache(): try import datascope"
            import antelope.datascope as datascope
            import antelope.stock as stock

        except Exception,e:
            print "Problem loading Antelope's Python libraries. (%s)" % e
            sys.exit()

        if self.config.debug: print "Stations: _get_stachan_cache(): done importing datascope"

        stachan_cache = {}
        records = 0

        if self.config.verbose: print "Stations: _get_stachan_cache(): update cache"

        for dbname in self.dbcentral.list():

            if self.config.debug: print "Station(): _get_stachan_cache(): in dbname: %s" % dbname

            #
            # On the first part just get the names and pass them down to the object
            #
            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='wfdisc')
                start = db.ex_eval('min(time)')
                end   = db.ex_eval('max(endtime)')
                start_day = stock.str2epoch(stock.epoch2str(start,'%D'))
                end_day = stock.str2epoch(stock.epoch2str(end,'%D'))
                db.sort(['sta', 'chan'], unique=True)
                records = db.query(datascope.dbRECORD_COUNT)

            except Exception,e:
                print 'Stations(): ERROR: Porblems on dbopen. ex_eval or dbquery %s: %s\n\n' % (Exception,e)
                records = 0


            if not records: 
                print 'Stations(): ERROR: No records to work on any  table\n\n'
                continue


            for j in range(records):

                db.record = j
                try:
                    sta, chan,  srate, calib, segtype = db.getv('sta','chan','samprate','calib','segtype')
                except Exception, e:
                    print 'Station(): ERROR extracting data db.getv(sta,chan,samprate,calib,segtype). (%s=>%s)' % (Exception,e)


                if srate == self.nulls('samprate'):
                    srate = '-'

                if calib == self.nulls('calib'):
                    calib = '-'

                if segtype == self.nulls('segtype'):
                    segtype = '-'

                if not sta in stachan_cache: stachan_cache[sta] = {}
                if not chan in stachan_cache[sta]: stachan_cache[sta][chan] = {}
                stachan_cache[sta][chan]['calib']    = calib
                stachan_cache[sta][chan]['segtype']  = segtype
                stachan_cache[sta][chan]['samprate'] = srate
                stachan_cache[sta][chan]['dates'] = [start_day,end_day]
                stachan_cache[sta][chan]['start'] = start
                stachan_cache[sta][chan]['end'] = end

                if self.config.debug: print "Station(): %s.%s[%s,%s,%s]" % (sta,chan,calib,segtype,srate)


        if self.config.verbose:
            print "Stations(): Updating cache (%s) stations." % len(stachan_cache.keys())

        self.stachan_cache = stachan_cache

        if self.config.verbose: print "Stations: _get_stachan_cache(): Done! updating cache"


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

        if self.config.debug: print 'Stations(): max_time(%s)=>%s' % (test,cache)
        return cache

    #}}}

    def dates(self,test=False):
    #{{{ function to return start and end times for a station
        """
        Get list of valid dates
        """

        cache = {}

        if not test: test = self.stachan_cache.keys()

        for sta in test:

            if not sta in self.stachan_cache: continue 

            for chan in self.stachan_cache[sta].keys():

                if not 'dates' in self.stachan_cache[sta][chan]: continue

                if self.config.debug: print "Stations(): dates(%s,%s)=>%s" % (sta,chan,self.stachan_cache[sta][chan]['dates'])

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

        if self.config.debug: print "Stations(): dates(%s)=>%s" % (test,cache)

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

        if self.config.debug: print "Stations(): convert_sta(%s)" % list

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

        if self.config.verbose: print "Stations(): convert_sta(%s) => %s" % (list,stations)

        return stations

    #}}}

    def convert_chan(self, list=['.*'], stations=['.*']):
    #{{{ get list of stations for the query

        if not list: list = ['.*'] 
        if not stations: stations = ['.*'] 

        if self.config.debug: print "Stations(): convert_chan(%s,%s)" % (list,stations)

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
            print "Stations(): convert_chan(%s,%s) => %s" % (stations,list,channels)

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
        self.event_cache = {}
        self.offset = -1 
        self.start = 0
        self.end = 0

        #
        # Load null class
        #
        print "Events(): self.nulls"
        self.nulls = db_nulls(db,self.config.debug,['events','event','origin','assoc','arrival']) 

        print "Events(): call _get_event_cache"
        self._get_event_cache()

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
                print "\nEvents(): %s(%s)" % (orid,self.event_cache[orid])

        else: 

            print "Events(): %s" % (self.event_cache.keys())

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

            print "Events(): %s not in database." % value
            return False
    #}}}

    def list(self):
        return self.event_cache.keys()

    def table(self):
        return self.event_cache

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

        if self.config.debug: print "Events: _get_evnet_cache(): starting"

        try:
            if self.config.debug: print "Events: _get_evnet_cache(): try import datascope"
            import antelope.datascope as datascope
            import antelope.stock as stock
        except Exception,e:
            print "Problem loading Antelope's Python libraries. (%s)" % e
            sys.exit()

        if self.config.debug: print "Events: _get_event_cache(): done importing datascope"



        if self.config.debug: print "Events(): update cache."

        for dbname in self.dbcentral.list():


            if self.config.debug: 
                print "Events(): _get_event_cache  db[%s]" % dbname

            event_cache = {}

            # Get min max for wfdisc table first
            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='wfdisc')
                start = db.ex_eval('min(time)')
                end = db.ex_eval('max(endtime)')
                records = db.query(datascope.dbRECORD_COUNT)

            except:
                records = 0


            if records:

                if not self.start:
                    self.start = start

                elif self.start > start:
                    self.start = start

                if not self.end:
                    self.end = end

                elif self.end < end:
                    self.end = end

            try:
                db.close()
            except:
                pass

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
                continue

            if self.config.debug: 
                print "Events(): origin db_pointer: [%s,%s,%s,%s]" % (db['database'],db['table'],db['field'],db['record'])

            try:
                db.subset("time > %f" % self.start)
                db.subset("time < %f" % self.end)
            except:
                pass

            try:
                records = db.query(datascope.dbRECORD_COUNT)
            except:
                records = 0

            if not records: 
                print 'Events(): ERROR: No records after time subset\n\n'
                continue

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


        self.event_cache = event_cache

        if self.config.verbose:
            print "Events(): Updating cache. (%s)" % len(event_cache)

#}}}

    def phases(self, min, max):
    #{{{ function to return dictionary of arrivals
        """
        Go through station channels to retrieve all
        arrival phases
        """
        if self.config.verbose: print "Events():phases(%s,%s) "%(min,max)
        phases = {}

        assoc   = False
        arrival = False

        dbname = self.dbcentral(min)

        if self.config.verbose: print "Events():phases(%s,%s) db:(%s)"%(min,max,dbname)

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
                print "Events: Exception on phases(): %s" % e,phases
                return phases


        try: 
            nrecs = db.query(datascope.dbRECORD_COUNT)
        except Exception,e:
            print "Events: Exception on phases(): %s" % e,phases
            return phases

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


            if self.config.debug: print "Phases(%s):%s" % (StaChan,Phase)

        if self.config.debug:  print "Events: phases(): t1=%s t2=%s [%s]" % (min,max,phases)

        return phases
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
        if self.config.verbose: print 'QueryParser(): Init DB: Load class resorce.Resource.__init__(self)'
        resource.Resource.__init__(self)


        #
        # Open db using dbcentral CLASS
        #
        if self.config.debug: print "QueryParser(): Init DB: Create dbcentral object with database(%s)." % self.dbname
        self.db = dbcentral.dbcentral(self.dbname,self.config.nickname,self.config.debug)

        if self.config.debug: self.db.info()

        if not self.db.list(): sys.exit('\nQueryParser(): Init DB: ERROR: No databases to use! (%s)\n\n'% self.dbname)


        self.tvals = {
                "filters": '<option value="None">None</option>',
                "dbname": self.dbname,
                "event_controls": '',
                "application_title": self.config.application_title,
            }

        if self.config.event:
                self.tvals['event_controls'] = ' \
                    <p>Get time from event list:</p> \
                    <input type="submit" id="load_events" value="Show Events"/> '


        for filter in self.config.filters:
            self.tvals['filters'] += '<option value="'+self.config.filters[filter].replace(' ','_')+'">'
            self.tvals['filters'] += filter
            self.tvals['filters'] += '"</option>'

        if self.config.event and self.config.display_arrivals:
            self.tvals['display_arrivals'] = 'checked="checked"'
        else:
            self.tvals['display_arrivals'] = ''

        if self.config.display_points:
            self.tvals['display_points'] = 'checked="checked"'
        else:
            self.tvals['display_points'] = ''

        reac = pool.apply_async(self._init_Reactor,(None,),callback=self._cb_init)

    #}}}

    def _init_Reactor(self,none):
        #{{{

        try:
            import antelope.datascope as datascope
            import antelope.stock as stock
        except Exception,e:
            print '\n\n Problem loading Antelope Python libraries. (%s)' % e
            return False

        #
        # We might need to remove 
        # databases without wfdisc table
        #
        remove = []

        for dbname in sorted(self.db.list()):

            #
            # Test database access. 
            #
            if self.config.debug: print "QueryParser(): Init(): try dbopen [%s]" % dbname

            try:
                db_temp = datascope.dbopen( dbname , "r" )
            except Exception, e:
                print '\nERROR: dbopen(%s) =>(%s)\n' % (dbname,e)
                remove.append(dbname)
                continue

            if self.config.debug: 
                print "QueryParser(): Init(): Dbptr: [%s,%s,%s,%s]" % (db_temp['database'],db_temp['table'],db_temp['field'],db_temp['record'])

            #table_list =  ['wfdisc','instrument','sensor','origin','arrival']
            table_list =  ['wfdisc']

            for tbl in table_list:
                if self.config.debug: print "QueryParser(): Init(): Check table  %s[%s]." % (dbname,tbl)

                try:
                    db_temp.lookup( table=tbl )
                except Exception, e:
                    print '\nERROR: %s.%s not present (%s)\n' % (dbname,tbl,e)
                    remove.append(dbname)
                    continue

                try:
                    db_temp.query(datascope.dbTABLE_PRESENT)
                except Exception,e:
                    print '\nERROR: %s.%s not present (%s)\n' % (dbname,tbl,e)
                    remove.append(dbname)
                    continue

                try:
                    records = db_temp.query(datascope.dbRECORD_COUNT)
                except Exception, e:
                    print '\nERROR: %s.%s( dbRECORD_COUNT )=>(%s)' % (dbname,tbl,e)
                    if tbl == 'wfdisc': remove.append(dbname)
                    continue


                if not records and tbl == 'wfdisc':
                    print '\nERROR: %s.%s( dbRECORD_COUNT )=>(%s) Empty table!!!!' % (dbname,tbl,records)
                    remove.append(dbname)
                    continue

                if self.config.debug: print "QueryParser(): Init():\t%s records=>[%s]" % (tbl,records)

            try:
                db_temp.close()
            except:
                print '\nERROR: dbclose(%s) =>(%s)\n' % (dbname,e)
                remove.append(dbname)
                continue


        for db_temp in remove:
            print "QueryParser(): Init(): Removing %s from dbcentral object" % db_temp
            self.db.purge(db_temp)

        if len(remove): print "QueryParser(): Init(): New list: dbcentral.list() => %s" % self.db.list()

        if not self.db.list(): 
            print '\n\nNo good databases to work! -v or -V for more info\n\n'
            return False

        return True

    #}}}

    def _cb_init(self,results=False):
    #{{{


        if not results: 
            print 'Problems in QueryParser() init() '
            reactor.stop()
            sys.exit()

        if self.config.debug: log.msg("QueryParser(): Init Done!") 

        self.loading = False


        #
        # Run update in loop calls
        #
        if self.config.debug: log.msg("QueryParser(): run init for Stations()") 
        stachan_loop = LoopingCall(pool.apply_async,Stations,(self.db,self.config),callback=self._cb_init_Station)
        stachan_loop.start(600,now=True)

        if self.config.event:
            if self.config.debug: log.msg("QueryParser(): run init for Events()") 
            event_loop = LoopingCall(pool.apply_async,Events,(self.db,self.config),callback=self._cb_init_Event)
            event_loop.start(600,now=True)
        else:
            if self.config.debug: log.msg("QueryParser(): Avoid init for Events()") 
            self.loading_events = False

    #}}} 
    def _cb_init_Station(self,result=False):
    #{{{

        if not result: 
            print 'Problems in QueryParser() Station() '
            reactor.stop()
            sys.exit()

        self.stations = result

        if self.config.debug: log.msg("QueryParser(): Station() update Done!" )

        self.loading_stations = False

    #}}}

    def _cb_init_Event(self,result=False):
    #{{{

        if not result: 
            print 'Problems in QueryParser() Events() '
            reactor.stop()
            sys.exit()

        self.events = result

        if self.config.debug: log.msg("QueryParser(): Events() update Done!" )

        self.loading_events = False

    #}}}

    def getChild(self, name, uri): 
    #{{{
        #if self.config.debug: log.msg("getChild(): name:%s uri:%s" % (name,uri))
        return self
    #}}}

    def render_GET(self, uri):
    #{{{
        if self.config.debug: log.msg("QueryParser(): render_GET(): uri: %s" % uri)

        if self.config.debug: 
            log.msg('')
            log.msg('QueryParser(): render_GET(%s)' % uri)
            log.msg('QueryParser(): render_GET() uri.uri:%s' % uri.uri)
            log.msg('QueryParser(): render_GET() uri.args:%s' % (uri.args) )
            log.msg('QueryParser(): render_GET() uri.prepath:%s' % (uri.prepath) )
            log.msg('QueryParser(): render_GET() uri.postpath:%s' % (uri.postpath) )
            log.msg('QueryParser(): render_GET() uri.path:%s' % (uri.path) )

            (host,port) = uri.getHeader('host').split(':', 1)
            log.msg('QueryParser():\tQUERY: %s ' % uri)
            log.msg('QueryParser():\tHostname => [%s:%s]'% (host,port))
            log.msg('QueryParser():\tHost=> [%s]'% uri.host)
            log.msg('QueryParser():\tsocket.gethostname() => [%s]'% socket.gethostname())
            log.msg('')
            #log.msg('QueryParser():\tsocket.getsockname() => [%s]'% uri.host.getsockname())
            #uri.setHost(host,config.port)


        if self.loading or self.loading_stations or self.loading_events:
            uri.setHeader("content-type", "text/html")
            uri.setHeader("response-code", 500)
            return "<html><head><title>%s</title></head><body><h1>DBWFSERVER:</h1></br><h3>Server Loading!</h3></body></html>" % self.config.application_name


        #d = defer.Deferred()
        #d.addCallback( lambda x: self.render_uri(v,x) )
        #d.addCallback( lambda x: self.uri_results(v,x,False,False) )
        #d.addErrback( lambda x: self.uri_results(v,x,False,True) )
        #reactor.callInThread(d.callback, uri)

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

        pool.apply_async(self.render_uri,(query,path),callback=lambda x: self.uri_results(uri,x) )

        if self.config.debug: log.msg("QueryParser(): render_GET() - return server.NOT_DONE_YET")

        return server.NOT_DONE_YET

    #}}}

    def render_uri(self,query,path):
    #{{{

        #
        # Clean and prep vars
        #
        response_data = {}
        response_meta = {}
        response_data = {}
        response_meta = {}

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



        if query['data']:
        #{{{

                if self.config.debug: log.msg('QueryParser(): render_uri() "data" query')

                if len(path) == 0:
                #{{{ ERROR: we need one option
                    log.msg('QueryParser(): render_uri() ERROR: Empty "data" query!')
                    return "Invalid data query."
                #}}}

                elif path[0] == 'events':
                #{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => events')
                    if not self.config.event: return {}

                    elif len(path) == 3:
                        return self.events.phases(path[1],path[2])

                    else:
                        return self.events.table()
                #}}}

                elif path[0] == 'dates':
                #{{{
                    """
                    Return list of yearday values for time in db
                    for all stations in the cluster of dbs.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => dates')

                    if len(path) == 2:
                        return self.stations.dates([path[1]])

                    else:
                        return self.stations.dates()
                #}}}

                elif path[0] == 'stations':
                #{{{
                    """
                    Return station list as JSON objects. For client ajax calls.
                    Called with argument return dictionary
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => stations')

                    if len(path) == 2: 
                        return self.stations.convert_sta(path[1].split('-'))

                    if len(path) == 3: 
                        for sta in self.stations.convert_sta(path[1].split('-')):
                            for chan in self.stations.convert_chan(path[2].split('-')):
                                if sta not in response_data: response_data[sta] = []
                                response_data[sta].extend(self.stations.convert_chan([chan],[sta]))

                        return response_data


                    return self.stations.convert_sta()
                #}}}

                elif path[0] == 'channels':
                #{{{
                    """
                    Return channels list as JSON objects. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => channels')

                    if len(path) == 2:
                        return self.stations.convert_chan(path[1].split('-'))

                    return self.stations.convert_chan()
                #}}}

                elif path[0] == 'filters':
                #{{{
                    """
                    Return list of filters as JSON objects. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => filters')

                    return self.config.filters
                #}}}

                elif path[0] == 'wf':
                #{{{
                    """
                    Return JSON object of data. For client ajax calls.
                    """

                    if self.config.debug: print "QueryParser(): render_uri(): get_data(%s))" % query

                    return self.get_data(query)

                #}}}

                elif path[0] == 'coverage':
                #{{{
                    """
                    Return coverage tuples as JSON objects. For client ajax calls.
                    """
                    if self.config.debug: print "QueryParser(): render_uri(): Get coverage" 


                    return self.coverage(query['sta'],query['chan'],query['start'],query['end'])

                #}}}

                elif path[0] == 'meta':
                #{{{
                    """
                    *** DEBUGGING TOOL ***
                    TEST metaquery parsing response. 
                    Return json with meta-query data for further ajax uri.
                    """

                    #query = self._parse_request(path)

                    if 'start' in query and self.config.event: 

                        response_meta['phases'] = self.events.time(query['start'],20)


                    for station in query['sta']:

                        temp_dic = self.stations(str(station))

                        if not temp_dic: continue

                        for channel in query['chan']:

                            if not channel in  temp_dic: continue

                            response_meta[station][channel]['metadata']  = temp_dic[channel]

                            response_meta['traces'][station][channel] = 'True'

                    return response_meta

                #}}}

                else:
                #{{{ ERROR: Unknown query type.
                    return "Unknown query type:(%s)" % path
                #}}}

        #}}}

        elif not path: 
            pass

        elif path[0] == 'wf':
            #{{{
                """
                Parse query for data uri. Return html with meta-query data for further ajax uri.
                """

                response_meta['meta_query'] = {}

                response_meta['meta_query']['traces'] = {};

                for sta in query['sta']:
                    temp_dic = self.stations(sta)

                    for chan in query['chan']:
                        if not chan in temp_dic: continue

                        if sta not in response_meta['meta_query']['traces']: response_meta['meta_query']['traces'][sta] = []
                        response_meta['meta_query']['traces'][sta].extend([chan])


                response_meta['meta_query']['sta'] = query['sta']
                response_meta['meta_query']['chan'] = query['chan']
                response_meta['meta_query']['o_sta'] = query['o_sta']
                response_meta['meta_query']['o_chan'] = query['o_chan']
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

                #query = self._parse_request(path)
                response_meta['meta_query'] = {}

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
            return "Invalid query." 
        #}}}

        #if 'mode' in uri.args: response_meta['setupUI'] = json.dumps(uri.args)

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

        uri = {}
        time_window = self.config.default_time_window

        uri.update( { 
            "sta":[],
            "chan":[],
            "o_sta":'null',
            "o_chan":'null',
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

        # localhost/sta
        if len(args) > 1:
            uri['sta'] = self.stations.convert_sta(args[1].split('-'))
            uri['o_sta'] = args[1]

        # localhost/sta/chan
        if len(args) > 2:
            uri['chan'] = self.stations.convert_chan(args[2].split('-'),args[1].split('-'))
            uri['o_chan'] = args[2]

        # localhost/sta/chan/time
        if len(args) > 3:
            uri['start'] = args[3]

        # localhost/sta/chan/time/time
        if len(args) > 4:
            uri['end'] = args[4]

        # localhost/sta/chan/time/time/filter
        if len(args) > 5:
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

    def uri_results(self, uri=None, results=None):
    #{{{
        print 'QueryParser(): uri_results(%s,%s)' % (uri,type(results))

        if uri: 
            #print '\n\nTYPE: %s \n\n' % type(results)
            if type(results).__name__ == 'list' or type(results).__name__ == 'dict':
                uri.setHeader("content-type", "application/json")
                uri.write(json.dumps(results))
            else:
                uri.setHeader("content-type", "text/html")
                uri.write(results)

            uri.finish()

        print 'QueryParser(): uri_results() DONE!'
    #}}}

    def get_data(self,query):
        # {{{
        #
        # Return points or bins of data for query
        #


        try:
            if self.config.debug: print "get_data(): try import datascope"
            import antelope.datascope as datascope
            import antelope.stock as stock
        except Exception,e:
            print "Problem loading Antelope's Python libraries. (%s)" % e
            sys.exit()

        if self.config.debug: print "get_data(): done importing datascope"

        response_data = {}

        if self.config.debug: print "QueryParser(): get_data(): Get data for uri:%s.%s" % (query['sta'],query['chan'])

        if self.config.debug: print "QueryParser(): get_data(): stations => %s" % query['sta']
        if self.config.debug: print "QueryParser(): get_data(): channels => %s" % query['chan']

        if not query['sta']:
            response_data['error'] = "Not valid station value" 
            print response_data['error']
            return response_data

        if not query['chan']:
            response_data['error'] = "Not valid channel value "
            print response_data['error']
            return response_data

        start = isNumber(query['start'])
        end   = isNumber(query['end'])

        if not start: 
            temp_dic = self.stations(query['sta'][0])
            if temp_dic: start = temp_dic[query['chan'][0]]['end'] - self.config.default_time_window

        if not start: start = stock.now()

        if not end: end = start + self.config.default_time_window

        #
        # Opend db pointer
        #
        if self.config.debug: print "\tQueryParser(): get_data(): get dbname for db(%s) " % start
        try:
            dbname = self.db(start)
        except Exception,e:
            response_data['error'] = '\n\nQueryParser(): get_data(): ERROR: Cannot get db for this time %s [%s][%s]\n\n' % (start,Exception,e)
            print response_data['error']
            return resopnse_data



        if not dbname:
            response_data['error'] = '\n\nQueryParser(): get_data(): ERROR: Cannot get db for this time %s [%s][%s]\n\n' % (start,Exception,e)
            print response_data['error']
            return resopnse_data
        else:
            if self.config.debug: print "\tQueryParser(): get_data(): dbname for db(%s) => %s " % (start,dbname)

        try:
            db = datascope.dbopen( dbname, 'r' )
            db.lookup( table='wfdisc' )
            records = db.query(datascope.dbRECORD_COUNT)

        except Exception, e:
            records = 0
            response_data['error'] = 'QueryParser(): get_data(): ERROR: Loading: %s.wfdisc => [%s]' % (dbname,e)
            print response_data['error']
            db.close()
            return resopnse_data

        if self.config.debug: print 'QueryParser(): get_data(): dbRECORD_COUNT => [%s]' % records

        if not records:
            response_data['error'] = 'QueryParser(): get_data(): ERROR: Empty set after rtload! '
            print response_data['error']
            db.close()
            return response_data

        for sta in query['sta']:
            if self.config.debug: print "\tQueryParser(): render_uri(): extract [%s] " % sta
            temp_dic = self.stations(sta)
            for chan in query['chan']:
                if self.config.debug: print "\tQueryParser(): render_uri(): extract [%s] " % chan

                if self.config.debug: print "\tQueryParser(): render_uri(): trload [%s][%s][%s][%s] " % (sta,chan,start,end)

                try:
                    print 'pntr:[%s]' % (db)
                    tr = datascope.trloadchan( db, start, end, sta, chan )
                except :
                    sleep(1)
                    try:
                        db = datascope.dbopen( dbname, 'r' )
                        db.lookup( table='wfdisc' )
                        print 'pntr:[%s]' % (db)
                        tr = datascope.trloadchan( db, start, end, sta, chan )
                    except Exception, e:
                        response_data['error'] = "QueryParser(): ERROR: render_uri(): trload [%s.%s.%s.%s] => %s" % (sta,chan,start,end,e)
                        print response_data['error']
                        continue

                if not sta in response_data: response_data[sta] = {}
                if not chan in response_data[sta]: response_data[sta][chan] = {}
                response_data[sta][chan] = {}
                response_data[sta][chan]['metadata'] = temp_dic[chan]
                points = 0

                if self.config.debug: print 'QueryParser(): get_data(): get dbRECORD_COUNT'
                try:
                    records = tr.query(datascope.dbRECORD_COUNT)
                except Exception, e:
                    records = 0
                    response_data['error'] = 'QueryParser(): get_data(): ERROR: Cannot get dbRECORD_COUNT'
                    print response_data['error']
                    continue

                if self.config.debug: print 'QueryParser(): get_data(): dbRECORD_COUNT => [%s]' % records

                if not records:
                    response_data['error'] = 'QueryParser(): get_data(): ERROR: Empty set after rtload! '
                    print response_data['error']
                    continue

                if records > 1:
                    response_data['error'] = 'Gap in segment! Display first part. [%s,%s]' (sta,chan)
                    print response_data['error']

                tr[3] = 0

                try:
                    sr = datascope.dbgetv( tr, 'samprate' )
                except Exception, e:
                    response_data['error'] = 'QueryParser(): get_data(): ERROR: Cannot get samplerate. [%s]' % e
                    print response_data['error']
                    continue

                try:
                    temp_start = datascope.dbgetv(tr,'time')[0] 
                    temp_end   = datascope.dbgetv(tr,'endtime')[0] 
                except Exception, e:
                    response_data['error'] = 'QueryParser(): get_data(): ERROR: Cannot get start-end times.'
                    print response_data['error']
                    continue

                response_data[sta][chan]['start']    = temp_start
                response_data[sta][chan]['end']      = temp_end

                points = (temp_end-temp_start) * sr[0]

                if points >  (self.config.binning_threshold * self.config.canvas_size_default):
                    binsize = int(points/self.config.canvas_size_default)
                else:
                    binsize = 0

                if self.config.debug: 
                    print "\tQueryParser(): render_uri(): points:%s " % points
                    print "\tQueryParser(): render_uri(): canvas:%s" % self.config.canvas_size_default
                    print "\tQueryParser(): render_uri(): threshold:%s" % self.config.binning_threshold
                    print "\tQueryParser(): render_uri(): binsize:%s " % binsize

                    print '\t\tget_data(): pid:[%s] pntr:[%s]' % (os.getpid(),tr)

                if query['filter']:
                    try:
                        tr.filter(query['filter'])
                    except Exception, e:
                        response_data['error'] = 'QueryParser(): get_data(): ERROR: Cannot filter data (%s)=>[%s]' (query['filter'],e)
                        print response_data['error']

                try:
                    tr.apply_calib()
                except Exception, e:
                    response_data['error'] = 'QueryParser(): get_data(): ERROR: Cannot apply calib [%s]' % e
                    print response_data['error']


                try:
                    if binsize:
                        response_data[sta][chan]['data']   = tr.databins(binsize)
                        response_data[sta][chan]['format'] = 'bins'
                    else:
                        response_data[sta][chan]['data']   = tr.data()
                        response_data[sta][chan]['format'] = 'lines'

                except Exception, e:
                    response_data['error'] = 'QueryParser(): get_data(): ERROR: Cannot extract data [%s]' % e
                    print response_data['error']
                    response_data[sta][chan]['error'] = "No data in db for this [%s,%s,%s,%s]" % (sta,chan,start,end)
                    response_data[sta][chan]['data']   = []
                    response_data[sta][chan]['format'] = 'lines'

                try:
                    #tr.trdestroy()
                    tr.trfree()
                except:
                    print "get_dat(): ERROR: on closing tr object Exception [%s]: %s" % (Exception,e)

        try:
            pass
            #db.close()
            #db.free()
        except:
            print "get_dat(): ERROR: on closing db pointer Exception [%s]: %s" % (Exception,e)

        return response_data

        # }}}

    def coverage(self,station=None,channel=None,start=0,end=0):
    #{{{

        if self.config.debug: print "coverage(): Get data for %s.%s [%s,%s]" % (station,channel,start,end)

        try:
            if self.config.debug: print "coverage(): try import datascope"
            import antelope.datascope as datascope
            import antelope.stock as stock
        except Exception,e:
            print "Problem loading Antelope's Python libraries. (%s)" % e
            sys.exit()

        if self.config.debug: print "coverage(): done importing datascope"

        #
        #Get list of segments of data for the respective station and channel
        #
        sta_str  = ''
        chan_str = ''
        res_data = {}

        res_data.update( {'type':'coverage'} )
        res_data.update( {'format':'cov-bars'} )
        res_data.update( {'time_start':0} )
        res_data.update( {'time_end':0} )

        res_data['sta'] = self.stations.convert_sta(station)
        res_data['chan'] = self.stations.convert_chan(channel,station)

        #
        # Build dictionary to store data
        #
        #   We need to build this to be clear to the application
        #   that some stations may have no data.
        for sta in res_data['sta']:

            for chan in res_data['chan']:

                    res_data[sta][chan] = {}

        if start: 
            dbname = self.db(start)
        else: 
            dbname = self.db( stock.now() )

        if self.config.debug: print  "coverage(): db:%s" % dbname

        try:
            if self.config.debug: print 'coverage(): Loading %s.wfdisc' % dbname
            db = datascope.dbopen( dbname, 'r' )
            db.lookup( table='wfdisc' )

        except Exception, e:
            response_data['error'] = 'coverage(): ERROR: in loading of %s.wfdisc => [%s]' % (dbname,e)
            return response_data

        if self.config.debug: print 'coverage(): Loading wfdisc => DONE'

        try:
            records = db.query(datascope.dbRECORD_COUNT)
        except:
            records = 0

        if self.config.debug: print  'coverage(): records [%s]' % records 

        # Subset wfdisc for stations
        if station:

            sta_str  = "|".join(str(x) for x in station)
            db.subset("sta =~/%s/" % sta_str)
            if self.config.debug: print "coverage(): subset on sta =~/%s/ " % sta_str

        # Subset wfdisc for channels
        if channel:

            chan_str  = "|".join(str(x) for x in channel)
            db.subset("chan =~/%s/" % chan_str)
            if self.config.debug: print "coverage(): subset on chan =~/%s/ " % chan_str

        # Subset wfdisc for start_time
        if start:

            res_data['time_start'] = start
            db.subset("endtime > %s" % start)
            if self.config.debug: print "coverage(): subset on time >= %s " % start

        else:
            # If no start time on request... use min in subset
            res_data['time_start'] = db.ex_eval('min(time)')

        # Subset wfdisc for end_time
        if end:

            res_data['time_end'] = end
            db.subset("time <= %s" % end)
            if self.config.debug: print "coverage(): subset on time_end <= %s " % end

        else:
            # If no end time on request... use max in subset
            res_data['time_end'] = db.ex_eval('max(endtime)')

        try:
            records = db.query(datascope.dbRECORD_COUNT)
        except:
            records = 0

        if self.config.debug: print  'coverage(): records [%s]' % records 

        if not records:

            print  'coverage(): No records for: [%s,%s,%s,%s]' %  (station,channel,start,end)
            return res_data

        for i in range(records):

            db.record = i

            try:

                (this_sta,this_chan,time,endtime) = db.getv('sta','chan','time','endtime')

            except Exception,e:

                print "coverage(): Problem in getv(): %s" % e

            else:

                if self.config.debug: print "coverage() db.getv: (%s,%s,%s,%s)" % (this_sta,this_chan,time,endtime)

                #if res_data['time_start'] < time:  res_data['time_start'] = time
                #if res_data['time_end'] > endtime: res_data['time_end'] = endtime

                #if not this_sta in res_data['sta']: res_data['sta'].append(this_sta)
                #if not this_chan in res_data['chan']: res_data['chan'].append(this_chan)
                #print 'coverage(): sta:%s chan:%s' % (res_data['sta'],res_data['chan'])

                #if this_sta not in res_data: res_data[this_sta] = defaultdic(dict)
                #if this_chan not in res_data[this_sta]: res_data[this_sta][this_chan] = defaultdic(dict)
                if 'data' not in res_data[this_sta][this_chan]: res_data[this_sta][this_chan]['data'] = []

                try:
                    res_data[this_sta][this_chan]['data'].append([time,endtime])
                except:
                    print "coverage(): Problem adding data to dictionary: [%s,%s] %s" % (time,endtime,e)

        try:
            db.close()
        except:
            print "get_dat(): ERROR: on closing db pointer Exception [%s]: %s" % (Exception,e)

        print "coverage(): %s" % res_data
        return res_data
    #}}}


#}}}

