from __main__ import *

#
# Global Functions
# 

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
        self.null_vals = defaultdict(lambda: defaultdict(dict))

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

            print  "\nERROR: db_nulls(): No element named (%s) in object.\n\n" % element
            return 

        if element in self.null_vals:

            return self.null_vals[element]

        else:

            print "\nERROR: db_nulls(): No value for (%s)\n\n" % element
            return
    #}}}

    def _get_nulls(self):
    #{{{ Private function to load values from dbs
        """
        Go through the tables on the database and return
        dictionary with NULL values for each field.
        """

        #try:
        #    import antelope.datascope as datascope
        #except Exception,e:
        #    print "Problem loading Antelope's Python libraries. (%s)" % e
        #    reactor.stop()


        """
        We will assume all databases have the same schema. 
        Get the first only.
        """
        dbname = self.dbcentral.list()[0]

        try:
            db = datascope.dbopen( dbname , "r" )

        except Exception, e:
            print '\n\nERROR: dbopen(%s)=>(%s)\n\n' % (dbname,e)
            sys.exit(reactor.stop()) 


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

        self.config = config
        self.first = True
        self.dbcentral = db
        self.stachan_cache = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.offset = -1
        self.wfdates = defaultdict(lambda: defaultdict(dict))
        self.maxtime = -1
        self.mintime = 0

        if self.config.debug: print "Stations(): init() class"

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

        if self.config.verbose: print "Stations():"

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
            if self.config.debug: print "Stations(): %s => %s" % (station,self.stachan_cache[station])
            return self.stachan_cache[station]

        else:
            print "Stations(): No value for station:%s" % station
            if self.config.debug:
                for sta in self.stachan_cache:
                    for chan in self.stachan_cache[sta]:
                        print '\t%s.%s => %s' % (sta,chan,self.stachan_cache[sta][chan])

        return False
    #}}}

    def _get_stachan_cache(self):
    #{{{ private function to load data
        records = 0

        if self.config.verbose: print "Stations(): update cache"

        for dbname in self.dbcentral.list():

            if self.config.debug: print "Station(): dbname: %s" % dbname
            dates = {}

            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='wfdisc',field='time')
                records = db.query(datascope.dbRECORD_COUNT)
                self.mintime = db.ex_eval('min(time)')
                self.maxtime   = db.ex_eval('max(endtime)')
            except Exception,e:
                print "Stations(): ERROR: Problem with wfdisc table. %s: %s" % (Exception,e)
                sys.exit(reactor.stop()) 

            if self.maxtime > stock.now() or self.maxtime > (stock.now()-3600):
                self.maxtime = -1


            #
            # Method 1
            #   python tools
            #
            for j in range(records):
                db.record = j
                try:
                    self.wfdates[stock.yearday(db.getv('time')[0])] = 1
                except Exception, e:
                    print 'Station(): ERROR (%s=>%s)' % (Exception,e)

            if self.config.debug: 
                print 'Stations(): maxtime: %s' % self.maxtime
                print 'Stations(): mintime: %s' % self.mintime
                print 'Stations(): dates: %s' % dates.keys()

            try:
                db.close()
            except:
                pass

            #
            # Method 2
            #   system tools
            #
            #run = "%s/bin/dbselect %s.wfdisc 'yearday(time)'" % (os.environ['ANTELOPE'],dbname)

            #print "*********"
            #print "Dates: "
            #print "*********"
            #for file in os.popen(run).readlines():
            #    dates[file.strip()] = 1
            #l = dates.keys()
            #print l
            #print "*********"
            #sys.exit(reactor.stop()) 

            #start_day = stock.str2epoch(stock.epoch2str(start,'%D'))
            #end_day = stock.str2epoch(stock.epoch2str(end,'%D'))
            #if self.wfdate:
            #    if self.wfdate[0] > start_day: self.wfdate[0] = start_day
            #    if self.wfdate[1] < start_day: self.wfdate[0] = start_day
            #self.wfdates = [start_day,end_day]

            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='sitechan')
                db.sort(['sta', 'chan'])
                records = db.query(datascope.dbRECORD_COUNT)

            except Exception,e:
                print 'Stations(): ERROR: Porblems with sitechan table %s: %s\n\n' % (Exception,e)
                sys.exit(reactor.stop()) 


            if not records: 
                print "Stations(): ERROR: No records after sitechan sort. "
                sys.exit(reactor.stop()) 


            for j in range(records):

                db.record = j
                try:
                    sta, chan, ondate, offdate = db.getv('sta','chan','ondate','offdate')
                except Exception, e:
                    print 'Station(): ERROR (%s=>%s)' % (Exception,e)

                ondate = stock.str2epoch(str(ondate))
                if offdate != -1: offdate = stock.str2epoch(str(offdate))

                self.stachan_cache[sta][chan]['dates'].extend([[ondate,offdate]])

                if self.config.debug: print "Station(): %s.%s dates: %s" % (sta,chan,self.stachan_cache[sta][chan]['dates'])

            try:
                db.close()
            except:
                pass


        print "Stations(): Done updating cache (%s) stations." % len(self.stachan_cache)

    #}}}

    def min_time(self):
    #{{{ function to return time of first sample 
        """
        Get time of first wfdisc sample
        """

        return self.mintime

    #}}}

    def max_time(self):
    #{{{ function to return time of last sample 
        """
        Get time of last wfdisc sample
        """

        if self.maxtime == -1:
            return stock.now()

        return self.maxtime

    #}}}

    def stadates(self,start=False,end=False):
    #{{{ function to return start and end times for a station
        """
        Get list of valid dates
        """

        if not start: return self.stachan_cache.keys()


        cache = {}

        if not end: end = stock.now()
        if start > end: end = stock.now()
        start = float(start)
        end = float(end)

        for sta in self.stachan_cache:
            for chan in self.stachan_cache[sta]:
                for date in self.stachan_cache[sta][chan]['dates']:

                    if date[1] == -1:

                        if date[0] <= start: cache[sta] = 1
                        if date[0] <= end: cache[sta] = 1

                    else:

                        if date[0] <= start and start <= date[1]: cache[sta] = 1
                        if date[0] <= end and end <= date[1]: cache[sta] = 1
                        if start <= date[0] and date[1] <= end: cache[sta] = 1

        print cache.keys()
        return cache.keys()

    #}}}

    def dates(self):
    #{{{ function to return start and end times for a station
        """
        Get list of valid dates
        """
        return self.wfdates.keys()

    #}}}

    def channels(self,station=[]):
    #{{{ function to return list of valid channels
        """
        Get unique list of channels.
        """
        chans = {}

        if station:

            for sta in station:
                if sta in self.stachan_cache:

                    for ch in self.stachan_cache[sta]:

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

        if self.config.debug: print "Stations(): convert_sta(%s) => %s" % (list,stations)

        return stations

    #}}}

    def list(self):
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
        self.event_cache = defaultdict(lambda: defaultdict(dict))
        self.offset = -1 
        self.start = 0
        self.end = 0

        if self.config.debug: print "Events(): init() class"

        #
        # Load null class
        #
        if self.config.debug: print "Events(): self.nulls"
        self.nulls = db_nulls(db,self.config.debug,['events','event','origin','assoc','arrival']) 

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

        value = isNumber(value)

        if not value:
            return "Not a valid number in function call: %s" % value

        if value in self.event_cache:

            return self.event_cache[value]

        else:

            print "Events(): %s not in database." % value
            return self.list
    #}}}

    def list(self):
        return self.event_cache.keys()

    def table(self):
        return dict(self.event_cache)

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
            print  "Not a valid number in function call: %s" % orid_time
            return
        
        start = float(orid_time)-float(window)
        end   = float(orid_time)+float(window)

        dbname = self.dbcentral(orid_time)

        if not db:
            print  "No match for orid_time in dbcentral object: (%s,%s)" % (orid_time,self.dbcentral(orid_time))
            return

        try: 
            db = datascope.dbopen( dbname , 'r' )
            db.lookup( table='origin')
            db.query(datascope.dbTABLE_PRESENT) 
        except Exception,e:
            print "Exception on Events() time(%s): Error on db pointer %s [%s]" % (orid_time,db,e)
            return

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

        if self.config.verbose: print "Events(): update cache"

        for dbname in self.dbcentral.list():

            if self.config.debug: print "Events(): dbname: %s" % dbname

            # Get min max for wfdisc table first
            try:
                db = datascope.dbopen( dbname , 'r' )
                db.lookup( table='wfdisc')
                start = db.ex_eval('min(time)')
                end = db.ex_eval('max(endtime)')
                if end > stock.now():
                    end = stock.now()
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


                self.event_cache[orid] = {'time':time, 'lat':lat, 'lon':lon, 'depth':depth, 'auth':auth, 'mb':mb, 'ms':ms, 'ml':ml, 'nass':nass}

                if mb > 0:
                    self.event_cache[orid]['magnitude'] = mb
                    self.event_cache[orid]['mtype'] = 'Mb'
                elif ms > 0:
                    self.event_cache[orid]['magnitude'] = ms
                    self.event_cache[orid]['mtype'] = 'Ms'
                elif ml > 0:
                    self.event_cache[orid]['magnitude'] = ml
                    self.event_cache[orid]['mtype'] = 'Ml'
                else:
                    self.event_cache[orid]['magnitude'] = '-'
                    self.event_cache[orid]['mtype'] = '-'

            try:
                db.close()
            except:
                pass

        print "Events(): Done updating cache. (%s)" % len(self.event_cache)

        if self.config.debug:
            print "Events(): %s" % self.event_cache.keys()

#}}}

    def phases(self, min, max):
    #{{{ function to return dictionary of arrivals
        """
        Go through station channels to retrieve all
        arrival phases
        """
        if self.config.debug: print "Events():phases(%s,%s) "%(min,max)

        phases = defaultdict(lambda: defaultdict(dict))

        assoc   = False
        arrival = False

        dbname = self.dbcentral(min)

        if self.config.debug: print "Events():phases(%s,%s) db:(%s)"%(min,max,dbname)

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

        if not nrecs:
            try:
                db.close()
            except:
                pass
            return dict(phases)

        try:
            db.subset("%s <= time && time <= %s" % (float(min),float(max)) )
            nrecs = db.query(datascope.dbRECORD_COUNT)
        except:
            nrecs = 0

        if not nrecs:
            try:
                db.close()
            except:
                pass
            return dict(phases)

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
        try:
            db.close()
        except:
            pass

        if self.config.debug:  print "Events: phases(): t1=%s t2=%s [%s]" % (min,max,phases)

        return dict(phases)
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

        print '########################'
        print '\tLoading!'
        print '########################'

        self.config = config
        self.dbname = db
        self.realtime = 'false'
        self.loading_stations = True
        self.loading_events = True

        #
        # Initialize Classes
        #
        if self.config.debug: print 'QueryParser(): Init DB: Load class resorce.Resource.__init__(self)'
        resource.Resource.__init__(self)


        #
        # Open db using dbcentral CLASS
        #
        if self.config.debug: print "QueryParser(): Init DB: Create dbcentral object with database(%s)." % self.dbname
        self.db = dbcentral.dbcentral(self.dbname,self.config.nickname,self.config.debug)

        if self.config.debug: self.db.info()

        if not self.db.list(): 
            print '\nQueryParser(): Init DB: ERROR: No databases to use! (%s)\n\n'% self.dbname
            sys.exit(reactor.stop()) 


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

            table_list =  ['wfdisc','sitechan']

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

        deferToThread(self._init_in_thread)

    #}}}

    def _init_in_thread(self):
    #{{{
        print '\nLoading Stations()\n'
        self.stations = Stations(self.db,self.config)
        self.loading_stations = False
        print '\nDone loading Stations()\n'

        if self.config.event:
            print '\nLoading Events()\n'
            self.events = Events(self.db,self.config)
            self.loading_events = False
            print '\nDone loading Events()\n'
        else:
            self.loading_events = False

        if self.stations.max_time() > (stock.now() - 3600 ):
            self.realtime = 'true'

        print '\nREADY!\n'
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


        if self.loading_stations or self.loading_events:
            uri.setHeader("content-type", "text/html")
            uri.setHeader("response-code", 500)
            html =  "<html><head><title>%s</title></head><body><h1>DBWFSERVER:</h1></br><h3>Server Loading!</h3></br>" % self.config.application_name
            
            html +=  "<p>Waiting for Stations: %s</p></br>" % self.loading_stations

            html +=  "<p>Waiting for Events: %s</p></br>" % self.loading_events

            html +=  "</body></html>"
            return html

        d = defer.Deferred()
        d.addCallback( self.render_uri )
        reactor.callInThread(d.callback, uri)

        if self.config.debug: log.msg("QueryParser(): render_GET() - return server.NOT_DONE_YET")

        return server.NOT_DONE_YET

    #}}}

    def render_uri(self,uri):
    #{{{

        #
        # Clean and prep vars
        #
        response_data = {}
        response_meta = {}

        response_meta.update( { 
            "type":       'meta-query',
            "error":      'false',
            "setupUI":    'false',
            "realtime":   self.realtime,
            "proxy":      "''",
            "proxy_url":  self.config.proxy_url,
            "style":      self.config.style,
            "meta_query": "false"
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

                if len(path) == 0:
                #{{{ ERROR: we need one option
                    log.msg('QueryParser(): render_uri() ERROR: Empty "data" query!')
                    return self.uri_results(uri,'Invalid data query.')
                #}}}

                elif path[0] == 'events':
                #{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => events')
                    if not self.config.event: 
                        return self.uri_results(uri,{})

                    elif len(path) == 2:
                        return self.uri_results( uri, self.events(path[1]) )

                    elif len(path) == 3:
                        return self.uri_results( uri, self.events.phases(path[1],path[2]) )

                    else:
                        return self.uri_results(uri,self.events.table() )
                #}}}

                elif path[0] == 'dates':
                #{{{
                    """
                    Return list of yearday values for time in db
                    for all wfs in the cluster of dbs.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => dates')

                    return self.uri_results( uri, self.stations.dates() )

                #}}}

                elif path[0] == 'stadates':
                #{{{
                    """
                    Return list of yearday values for time in db
                    for all stations in the cluster of dbs.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => dates')

                    if len(path) == 2: 
                        return self.uri_results( uri, self.stations.stadates(path[1]) )

                    if len(path) == 3: 
                        return self.uri_results( uri, self.stations.stadates(path[1],path[2]) )

                    return self.uri_results( uri, self.stations.stadates() )

                #}}}

                elif path[0] == 'stations':
                #{{{
                    """
                    Return station list as JSON objects. For client ajax calls.
                    Called with argument return dictionary
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => stations')

                    if len(path) == 2: 
                        return self.uri_results( uri, self.stations(path[1]) )

                    return self.uri_results( uri, self.stations.list() )
                #}}}

                elif path[0] == 'channels':
                #{{{
                    """
                    Return channels list as JSON objects. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => channels')

                    if len(path) == 2:
                        stas = self.stations.convert_sta(path[1].split('|')) 
                        return self.uri_results( uri, self.stations.channels( stas ) )

                    return self.uri_results( uri, self.stations.channels() )
                #}}}

                elif path[0] == 'now':
                #{{{
                    """
                    Return JSON object for epoch(now).
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => now')

                    return self.uri_results( uri, [stock.now()] )
                #}}}

                elif path[0] == 'filters':
                #{{{
                    """
                    Return list of filters as JSON objects. For client ajax calls.
                    """

                    if self.config.debug: log.msg('QueryParser(): render_uri() query => data => filters')

                    return self.uri_results( uri, self.config.filters )
                #}}}

                elif path[0] == 'wf':
                #{{{
                    """
                    Return JSON object of data. For client ajax calls.
                    """

                    if self.config.debug: print "QueryParser(): render_uri(): get_data(%s))" % query

                    return self.uri_results( uri, self.get_data(query) )

                #}}}

                elif path[0] == 'coverage':
                #{{{
                    """
                    Return coverage tuples as JSON objects. For client ajax calls.
                    """
                    if self.config.debug: print "QueryParser(): render_uri(): Get coverage" 

                    query.update( { "coverage": 1 } )

                    return self.uri_results( uri, self.get_data(query) )

                #}}}

                else:
                #{{{ ERROR: Unknown query type.
                    return self.uri_results( uri, "Unknown query type:(%s)" % path )
                #}}}

        #}}}

        response_meta.update(self.tvals)

        if not path: 
            return  self.uri_results( uri, Template(open(self.config.template).read()).safe_substitute(response_meta) )

        response_meta['meta_query'] = {}
        response_meta['meta_query']['sta'] = query['sta']
        response_meta['meta_query']['chan'] = query['chan']
        response_meta['meta_query']['time_start'] = query['start']
        response_meta['meta_query']['time_end'] = query['end']
        response_meta['meta_query']['calib'] = query['calib']
        response_meta['meta_query']['filter'] = query['filter']
        response_meta['meta_query']['page'] = query['page']
        if uri.args:
            response_meta['setupUI'] = json.dumps(uri.args)

        response_meta['meta_query'] = json.dumps( response_meta['meta_query'] )

        if path[0] == 'wf':
                return  self.uri_results( uri, Template(open(self.config.template).read()).safe_substitute(response_meta) )

        elif path[0] == 'plot':
                return  self.uri_results( uri, Template(open(self.config.plot_template).read()).safe_substitute(response_meta) )

        return self.uri_results( uri, "Invalid query."  )

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
            localhost/data/meta/sta/chan/time/time/filter/page


        """
        if self.config.debug: log.msg("QueryParser(): _parse_request(): URI: %s" % str(args) ) 

        uri = {}
        time_window = self.config.default_time_window

        uri.update( { 
            "sta":[],
            "chan":[],
            "end":0,
            "data":False,
            "start":0,
            "filter":'None',
            "calib":False,
            "page":1,
            "coverage":0,
            "time_window":False
        } )

        if 'data' in args:
            if self.config.verbose: log.msg("QueryParser() _parse_request(): data query!") 
            uri['data'] = True
            args.remove('data')

        # localhost/sta
        if len(args) > 1:
            uri['sta'] = args[1]

        # localhost/sta/chan
        if len(args) > 2:
            uri['chan'] = args[2]

        # localhost/sta/chan/time
        if len(args) > 3:
            uri['start'] = args[3]

        # localhost/sta/chan/time/time
        if len(args) > 4:
            uri['end'] = args[4]

        # localhost/sta/chan/time/time/filter
        if len(args) > 5:
            uri['filter'] = args[5]

        # localhost/sta/chan/time/time/filter/calib
        if len(args) > 6:
            uri['calib'] = args[6]

        # localhost/sta/chan/time/time/filter/calib/page
        if len(args) > 7:
            uri['page'] = args[7]


        #
        #Setting the filter
        #
        if uri['filter']:
            if uri['filter'] == 'None' or uri['filter'] == 'null' or uri['filter'] == '-':
                uri['filter'] = 'None'
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
            if not uri['start'] :
                uri['end'] = self.stations.max_time()
                uri['start'] = uri['end'] - time_window

                uri['end']   = isNumber(uri['end'])
                uri['start'] = isNumber(uri['start'])

            if not uri['end']:
                uri['end'] = uri['start'] + time_window

        if self.config.verbose: 
            log.msg("QueryParser(): _parse_request(): [sta:%s chan:%s start:%s end:%s]" % (uri['sta'], uri['chan'], uri['start'], uri['end']) ) 

        return uri
        # }}}

    def uri_results(self, uri=None, results=None):
    #{{{
        print 'QueryParser(): uri_results(%s,%s)' % (uri,type(results))

        try:
            if uri: 
                #print '\n\nTYPE: %s \n\n' % type(results)
                if type(results).__name__ == 'list' or type(results).__name__ == 'dict':
                    uri.setHeader("content-type", "application/json")
                    uri.write(json.dumps(results))
                else:
                    uri.setHeader("content-type", "text/html")
                    uri.write(results)

                    uri.finish()
        except:
            pass

        print 'QueryParser(): uri_results() DONE!'
    #}}}

    def get_data(self,query):
        # {{{
        #
        # Return points or bins of data for query
        #

        response_data = ""

        if self.config.debug: 
            print "QueryParser(): get_data(): Build COMMAND"

        if self.config.debug: 
            print "QueryParser(): get_data(): Get data for uri:%s.%s" % (query['sta'],query['chan'])

        if not query['sta']:
            response_data = "Not valid station value" 
            print response_data
            return { "ERROR": response_data }

        if not query['chan']:
            response_data = "Not valid channel value "
            print response_data
            return { "ERROR": response_data }

        start = isNumber(query['start'])
        end   = isNumber(query['end'])

        if not start: 
            temp_dic = self.stations(query['sta'][0])
            if temp_dic: start = temp_dic[query['chan'][0]]['end'] - self.config.default_time_window

        #if not start: start = stock.now()

        if not end: end = start + self.config.default_time_window

        tempdb = self.db(start)
        if not tempdb:
            response_data = "Not valid database for this time [%s]" % start
            print response_data
            return { "ERROR": response_data }

        regex = "-s 'sta=~/%s/ && chan=~/%s/' " % (query['sta'],query['chan'])

        if query['filter'] != 'None':
            filter = "-f '%s'" % query['filter']
        else:
            filter = ""

        if query['coverage']:
            coverage = "-b "
        else:
            coverage = ""

        if query['calib']:
            calib = "-c "
        else:
            calib = ""

        if query['page']:
            page = "-p %s" % query['page']
        else:
            page = ""

        run = "dbwfserver_extract %s %s %s %s %s -n %s -m %s %s %s %s 2>&1" % ( regex, coverage, filter, page, calib, self.config.max_traces, self.config.max_points, tempdb, start, end)

        print "*********"
        print "QueryParser(): get_data(): Extraction command: [%s]" % run
        print "*********"

        # Method 1
        #master, slave = pty.openpty()
        #pipe = Popen(run, stdin=PIPE, stdout=slave, stderr=slave, close_fds=True, shell=True)
        #stdout = os.fdopen(master)
        #return stdout.readline()

        # Method 2
        return os.popen(run).read().replace('\n', '')

        # }}}

#}}}

