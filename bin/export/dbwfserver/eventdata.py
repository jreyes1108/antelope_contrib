import sys
import os
import re

from twisted.python import log 
from twisted.internet import reactor

from collections import defaultdict 

from antelope.datascope import *
from antelope.stock import *

import dbwfserver.config as config
    
def _error(text,dictionary=None,quiet=False):
#{{{
    """
    Test if the 'error' is defined in the dictionary and append text.
    Return updated dictionary.
    """

    log.msg("\n\n\tERROR:\n\t\t%s\n" % text)

    if dictionary and not quiet:
        if 'error' in dictionary:
            dictionary['error'] = str(dictionary['error']) + '\n'+ text 
        else:
            dictionary['error'] = '\n' + text

        return dictionary
#}}}

def _isNumber(test):
#{{{
    """
    Test if the string is a valid number 
    and return the converted number. 
    """
    try:
        test = str(test)
        if re.search('.',test):
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

class db_nulls():
#{{{
    """
    db_nulls tools.
    """

    def __init__(self):
#{{{
        self.dbname = config.dbname
        self.db = dbopen(self.dbname)
        self._get_nulls()
#}}}

    def __str__(self):
#{{{
        """
        end-user/application display of content using print() or log.msg()
        """
        text = 'Null values for (%s):' % config.dbname

        for value in self.null_vals.keys():
            text += "\t%s: %s" % (value,self.null_vals[value])

        return text
#}}}

    def __call__(self, element):
#{{{
        """
        method to intercepts data requests.
        """
        if element in self.null_vals:
            if config.debug:
                log.msg("\tNULLS(%s): %s" % (element,self.null_vals[element]))
            return self.null_vals[element]

        else:
            _error("Class db_nulls(): No value for (%s)" % element)
            return ''
#}}}

    def _get_nulls(self):
#{{{
        """
        Go through the tables on the database and return
        dictionary with NULL values for each field.
        """

        self.null_vals = defaultdict(dict)

        for table in self.db.query(dbSCHEMA_TABLES):
            self.db.lookup( '',table,'','')
            for field in self.db.query(dbTABLE_FIELDS):
                self.db.lookup( '',table,field,'dbNULL')
                self.null_vals[field] = _isNumber(self.db.get(''))
                if config.debug: log.msg("Class Db_Nulls: set(%s):%s" % (field,self.null_vals[field]))
#}}}

#}}}
#
# Initiate db_nulls here to be accessible to Stations and Events classes simultaneously
# This will turn 'nulls' into a global object inside eventdata.py
# We can do this on resources.py but that will prevent direct access from Stations or Events classes
#   and from other servers using this library. This will change in the next version of the server. 
nulls = db_nulls()



class Stations():
#{{{
    """
    Data structure and functions to query for stations
    """

    def __init__(self, dbname):
#{{{
        self.dbname = dbname
        self.db = dbopen(self.dbname)
        self.stachan_cache = defaultdict(dict)
        self.index = []
        self._get_stachan_cache()
#}}}

    def __iter__(self):
#{{{
        self.index = self.stachan_cache.keys()
        return self
#}}}

    def next(self):
#{{{
        if len(self.index) == 0:
            raise StopIteration
        else:
            return self.index.pop()
#}}}

    def __repr__(self):
#{{{
        """
        low-level display for programmers o use during development.
        call: repr(var)
        """
        log.msg("\tClass Stations(): Cache of stations. (%s) stations." %  self.stachan_cache.keys())

        for st in self.stachan_cache.keys():
            log.msg("\t\t%s:" % st )
            for ch in self.stachan_cache[st].keys():
                log.msg("\t\t\t%s: %s" % (ch,self.stachan_cache[st][ch]) )
#}}}

    def __str__(self):
#{{{
        """
        end-user/application display of content using print() or log.msg()
        """
        for st in self.stachan_cache.keys():
            chans = self.stachan_cache[st].keys()
            log.msg("\t%s: %s" % (st,chans) )
#}}}

    def __call__(self, station):
#{{{
        """
        method to intercepts data requests.
        """
        if station in self.stachan_cache:
            return self.stachan_cache[station]

        else:
            log.msg("Class Stations(): No value for (%s)" % station)
            return False
#}}}

    def _get_stachan_cache(self):
#{{{
        self.stachan_cache = defaultdict(dict)

        db = Dbptr(self.db)
        if config.simple:
            db.process([
                'dbopen wfdisc',
                'dbsort -u sta chan'
                ])
        else:
            db.process([
                'dbopen sensor',
                'dbjoin instrument',
                'dbsort sta chan'
                ])

        for i in range(db.query(dbRECORD_COUNT)):

            db.record = i

            if config.simple:

                sta, chan, srate = db.getv('sta', 'chan', 'samprate')

                if config.debug:
                    log.msg("\tStation(%s): %s " % (sta,chan))

                self.stachan_cache[sta][chan] = defaultdict(dict)
                if srate > 0:
                    self.stachan_cache[sta][chan]['samprate'] = srate
                else :
                    self.stachan_cache[sta][chan]['samprate'] = 0

            else:
                sta, chan, insname, srate, ncalib, rsptype, time, endtime = db.getv('sta', 'chan', 'insname', 'samprate', 'ncalib','rsptype','time','endtime')

                if _isNumber(endtime) == nulls('endtime'):
                    endtime = '-'

                if _isNumber(ncalib) == nulls('ncalib'):
                    ncalib = '-'

                if _isNumber(srate) == nulls('samprate'):
                    srate = '-'

                if rsptype == nulls('rsptype'):
                    rsptype = '-'

                if insname == nulls('insname'):
                    insname = '-'

                if config.debug:
                    log.msg("\tStation(%s): %s %s %s %s %s %s %s" % (sta,chan,time,endtime,insname,srate,ncalib,rsptype))

                self.stachan_cache[sta][chan] = defaultdict(dict)
                self.stachan_cache[sta][chan][time]['insname'] = insname
                self.stachan_cache[sta][chan][time]['samprate'] = srate
                self.stachan_cache[sta][chan][time]['ncalib'] = ncalib
                self.stachan_cache[sta][chan][time]['rsptype'] = rsptype
                self.stachan_cache[sta][chan][time]['endtime'] = endtime

        if config.verbose:
            log.msg("\tClass Stations(): Updating cache of stations. (%s) stations." % len(self.list()) )

        if config.debug: self.__str__()


        self.call = reactor.callLater(60, self._get_stachan_cache)
#}}}

    def channels(self,station=False):
#{{{
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

    def list(self):
            return self.stachan_cache.keys()
#}}}

class Events():
#{{{
    """
    Data structure and functions to query for events
    """

    def __init__(self, dbname):
#{{{
        self.dbname = dbname
        self.db = dbopen(self.dbname)
        self.event_cache = defaultdict(list)
        self.index = []
        self._get_event_cache()
#}}}

    def __iter__(self):
#{{{
        self.index = self.event_cache.keys()
        return self
#}}}

    def next(self):
#{{{
        if len(self.index) == 0:
            raise StopIteration
        else:
            return self.index.pop()
#}}}

    def __repr__(self):
#{{{
        """
        low-level display for programmers o use during development.
        call: repr(var)
        """
        log.msg("\tClass Events(): Cache of events. (%s) events.", len(self.event_cache) )
        log.msg("\t\t%s", (self.event_cache.keys()) )
        for event in self.event_cache.keys():
            log.msg("\t\t%s: %s" % (event,self.event_cache[event]) )
#}}}

    def __str__(self):
#{{{
        """
        end-user/application display of content using print() or log.msg()
        """
        log.msg("\t\tEvents: %s" % (self.event_cache.keys()) )
#}}}

    def __call__(self, value):
#{{{
        """
        method to intercepts data requests.
        """

        value = _isNumber(value)

        if self.event_cache[value]:
            return self.event_cache[value]
        else:
            log.msg("Class Events(): No value (%s)" % value)
            return False
#}}}

    def list(self):
        return self.event_cache.keys()

    def table(self):
        return self.event_cache

    def time(self,orid_time,window=5):
#{{{
        """
        Look for event id close to a value of epoch time + or - window time in seconds. 
        If no widow time is provided the default is 5 secods.
        """

        if config.simple: 
            return {}

        results = {}
        
        start = float(orid_time)-float(window)
        end   = float(orid_time)+float(window)

        db = Dbptr(self.db)

        db.lookup( table='origin')

        db.process([ 'dbopen origin' ]) 
        db.process([ 'dbsubset time >= %f' % start ])
        db.process([ 'dbsubset time <= %f' % end ])

        if db.query(dbRECORD_COUNT):

            for i in range(db.query(dbRECORD_COUNT)):

                db.record = i

                (orid,time) = db.getv('orid','time')

                orid = _isNumber(orid)
                time = _isNumber(time)
                results[orid] = time

            return results

        else:
            return {}
#}}}

    def _get_event_cache(self):
#{{{
        if config.simple:
            return {}
        self.event_cache = defaultdict(list)

        db = Dbptr(self.db)

        db.lookup( table='event')

        if db.query(dbTABLE_PRESENT): 
            db.process([ 'dbopen event' ])
            db.process([ 'dbjoin origin' ])
            db.process([ 'dbsubset orid == prefor' ])
        else:
            if config.verbose: log.msg("\n\tevent table NOT present!!!\n")
            db.lookup( table='assoc')

            if db.query(dbTABLE_PRESENT): 
                db.process([ 'dbopen origin' ])
                db.process([ 'dbjoin assoc' ])
                db.process([ 'dbsort -u sta orid' ])
            else:
                if config.verbose: log.msg("\n\tassoc table NOT present!!!\n")
                db.process([ 'dbopen origin' ])

        db.process([ 'dbsort -u orid' ])

        for i in range(db.query(dbRECORD_COUNT)):

            db.record = i

            (orid,time,lat,lon,depth,auth,mb,ml,ms,nass) = db.getv('orid','time','lat','lon','depth','auth','mb','ml','ms','nass')


            if auth == nulls('auth'):
                auth = '-'

            if _isNumber(orid) == nulls('orid'):
                orid = '-'

            if _isNumber(time) == nulls('time'):
                time = '-'

            if _isNumber(lat) == nulls('lat'):
                lat = '-'

            if _isNumber(lon) == nulls('lon'):
                lon = '-'

            if _isNumber(depth) == nulls('depth'):
                depth = '-'

            if _isNumber(mb) == nulls('mb'):
                mb = '-'

            if _isNumber(ms) == nulls('ms'):
                ms = '-'

            if _isNumber(ml) == nulls('ml'):
                ml = '-'

            if _isNumber(nass) == nulls('nass'):
                nass = '-'


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


            if config.debug:
                log.msg("\tEvent(%s): [time:%s lat:%s lon:%s depth:%s auth:%s mb:%s ml:%s ms:%s nass:%s]" % (orid,time,lat,lon,depth,auth,mb,ml,ms,nass) )

        if config.verbose:
            log.msg("\tClass Events(): Updating cache of events. (%s) events." % len(self.event_cache) )

        if config.debug:
            self.__str__()

        self.call = reactor.callLater(60, self._get_event_cache)
#}}}

    def phases(self, mintime, maxtime):
#{{{
        """
        Go through station channels to retrieve all
        arrival phases
        """

        if config.simple:
            return {}

        if config.debug: log.msg("Getting phases.")

        phases = defaultdict(dict)

        assoc_present = False

        db = Dbptr(self.db)

        db.lookup( table='assoc')

        if db.query(dbTABLE_PRESENT): 
            db.process([ 'dbopen arrival' ])
            db.process([ 'dbjoin assoc' ])
            assoc_present = True
        else:
            if config.verbose: log.msg("\n\tassoc table NOT present!!!\n")
            db.process([ 'dbopen arrival' ])


        if db.query(dbTABLE_PRESENT):

            try:
                phase_sub = dbsubset(db,'time >= %s && time <= %s' % (float(mintime),float(maxtime)) )
            except Exception,e:
                _error("Exception on phases: %s" % e,phases)
                return phases

            for p in range(phase_sub.query(dbRECORD_COUNT)):

                phase_sub.record = p

                if assoc_present:
                    try:
                        Sta, Chan, ArrTime, Phase = phase_sub.getv('sta','chan','time','phase')
                    except Exception,e:
                        _error("Exception on phases: %s" % e,phases)
                        return phases

                    StaChan = Sta + '_' + Chan

                    phases[StaChan][ArrTime] = Phase

                else:
                    try:
                        Sta, Chan, ArrTime, Phase = phase_sub.getv('sta','chan','time','iphase')
                    except Exception,e:
                        _error("Exception on phases: %s" % e,phases)
                        return phases

                    StaChan = Sta + '_' + Chan

                    phases[StaChan][ArrTime] = '_' + Phase


                if config.debug:
                    log.msg("Phases(%s):%s" % (StaChan,Phase) )

            if not phases:
                _error("No arrivals in this time segment for time segment: t1=%s t2=%s" % (mintime,maxtime),phases)

            return phases
#}}}
#}}}

class EventData():
#{{{
    """
    Provide interaction with Datascope database
    """

    def __init__(self, dbname):
#{{{
        self.dbname = dbname
        self.db = dbopen(self.dbname)
#}}}

    def _get_matched_stations(self, sta=None):
#{{{
        stations = []

        db = Dbptr(self.db)

        if config.simple:
            db.process([ 'dbopen wfdisc' ])
        else:
            db.process([
                'dbopen sensor',
                'dbjoin instrument'
                ])

        if not sta:
            sta = ['.*']

        # Handle wildcards on station value
        sta_str  = "|".join(str(x) for x in sta)

        db.subset("sta =~/%s/" % sta_str)

        db.process([ 'dbsort -u sta' ])

        if db.query(dbRECORD_COUNT) == 0:
            _error('%s not a valid station regex' % sta_str)
            return []

        for i in range(db.query(dbRECORD_COUNT)):
            db.record = i
            stations.append(db.getv('sta')[0])

        return stations
#}}}

    def _get_matched_channels(self, chan=None):
#{{{
        channels = []

        db = Dbptr(self.db)

        if config.simple:
            db.process([ 'dbopen wfdisc' ])
        else:
            db.process([
                'dbopen sensor',
                'dbjoin instrument'
                ])

        if not chan:
            chan = ['.*']

        # Handle wildcards on station value
        chan_str  = "|".join(str(x) for x in chan)

        db.subset("chan =~/%s/" % chan_str)

        db.process([ 'dbsort -u chan' ])

        if db.query(dbRECORD_COUNT) == 0:
            _error('%s not a valid channel regex' % chan_str)
            return []

        for i in range(db.query(dbRECORD_COUNT)):
            db.record = i
            channels.append(db.getv('chan')[0])

        return channels
#}}}

    def _extract_values(self, url):
#{{{
        data = defaultdict(dict)

        """
        Setting stations
        """
        # Handle wildcards on station values
        if 'sta' in url:
            data['sta'] = self._get_matched_stations(url['sta'])
        else:
            data['sta'] = self._get_matched_stations()

        """
        Setting channels
        """
        # Handle wildcards on channel values
        if 'chan' in url:
            data['chan'] = self._get_matched_channels(url['chan'])
        else:
            data['chan'] = self._get_matched_channels()

        """
        Setting time window of waveform.
        """
        if 'time_end' in url:
            # Segment provided
            data['time_start'] = _isNumber(url['time_start'])
            data['time_end'] = _isNumber(url['time_end'])

        elif 'time_start' in url:
            # We have start time... calc end time
            data['time_start'] = _isNumber(url['time_start'])
            data['time_end'] = _isNumber( float(url['time_start']) + float(config.default_time_window) )

        else:
            # Get the newest data in the wfdisc
            # and go back 'default_time_window'.

            # Start wfdisc query
            db = Dbptr(self.db)
            db.process([ 'dbopen wfdisc', ])

            # Subset wfdisc for stations
            if 'sta' in url:
                sta_str  = "|".join(str(x) for x in url['sta'])
                db.subset("sta =~/%s/" % sta_str)
                if config.debug: log.msg("\n\nCoverage subset on sta =~/%s/ " % sta_str)

            # Subset wfdisc for channels
            if 'chan' in url:
                chan_str  = "|".join(str(x) for x in url['chan'])
                db.subset("chan =~/%s/" % chan_str)
                if config.debug: log.msg("\n\nCoverage subset on chan =~/%s/ " % chan_str)

            if not db.query(dbRECORD_COUNT):
                _error('No records for: %s' %  url, data)
                return data

            # no end time on request... use max in subset
            data['time_end'] = db.ex_eval('max(endtime)')
            data['time_start'] = data['time_end'] - float(config.default_time_window)

        return data
#}}}

    def parse_query(self, url_data, stations=None, events=None):
#{{{
        """
        Prepare metadata for future ajax extraction
        """
        if config.debug:
            log.msg("Starting functions eventdata.parse_query(): %s" % url_data)

        res_data = self._extract_values(url_data)

        res_data['type'] = 'meta-query'

        if 'sta' in res_data and 'chan' in res_data and 'time_start' in res_data: 

            # Getting phase arrival times.
            #res_data['phases'] = events.phases(res_data['sta'],res_data['time_start'],res_data['time_end'])
            pass


        for station in res_data['sta']:

            temp_dic = stations(str(station))

            if not temp_dic:
                _error('%s not a valid station' % (station),res_data)
                continue

            for channel in res_data['chan']:
                if not channel in  temp_dic:
                    _error("%s not valid channel for station %s" % (channel,station),res_data,True)
                    continue

                if config.debug: log.msg("Now: %s %s" % (station,channel))

                res_data[station][channel] = defaultdict(dict)

                res_data[station][channel]['metadata']  = temp_dic[channel]

        if not res_data:
            _error("No meta-queries results for URL : %s" % url_data ,res_data)

        return res_data
#}}}

    def get_segment(self, url_data, stations, events):
#{{{
        """
        Get a segment of waveform data.
        """

        if config.debug:
            log.msg("\nStarting functions eventdata.get_segment(): %s" % url_data)

        """
        Setting vars
        """
        res_data = self._extract_values(url_data)

        res_data['type'] = 'waveform'

        """
        Verify data extracted.
        """
        if not 'time_start' in res_data or not 'time_end' in res_data:
            _error("Error in time:(%s,%s)" % (res_data['time_start'],res_data['time_end']),res_data)
            return  

        if not 'sta' in res_data: 
            _error('Error. No stations in selection.' % url_data['sta'], res_data)
            return  

        if not 'chan' in res_data: 
            _error('Error. No channels in selection.' % url_data['cahns'], res_data)
            return  

        """
        Setting the filter
        """
        if 'filter' in url_data:
            if url_data['filter'] == 'None':
                filter = None
            else:
                filter = url_data['filter'].replace('_',' ')
        else:
            filter = None

        res_data['filter'] = filter


        for station in res_data['sta']:

            temp_dic = stations(str(station))

            if not temp_dic:
                _error('%s not a valid station' % (station),res_data)
                continue

            for channel in res_data['chan']:
                if config.debug: log.msg("Now: %s %s" % (station,channel))


                if not channel in  temp_dic:
                    _error("%s not valid channel for station %s" % (channel,station),res_data)
                    continue

                res_data[station][channel] = defaultdict(dict)

                res_data[station][channel]['start']     = res_data['time_start']
                res_data[station][channel]['end']       = res_data['time_end']
                res_data[station][channel]['metadata']  = temp_dic[channel]

                if config.debug: log.msg("Get data for (%s %s %s %s)" % (res_data['time_start'],res_data['time_end'],station,channel))

                # Loop over all samplerates and get max
                # A station might swap sensor and change samplerate.
                if config.simple:
                    if temp_dic[channel]['samprate']:
                        points = int( (res_data['time_end']-res_data['time_start']) * temp_dic[channel]['samprate'] )
                    else:
                        points = 1

                else:
                    points = int( (res_data['time_end']-res_data['time_start'])* max([ temp_dic[channel][x]['samprate'] for x in temp_dic[channel]]) )

                if config.debug: log.msg("Total points:%s Canvas Size:%s Binning threshold:%s" % (points,config.canvas_size_default,config.binning_threshold))

                if not points > 0:
                    res_data[station][channel]['data'] = ()

                elif points <  (config.binning_threshold * config.canvas_size_default):

                    try:
                        res_data[station][channel]['data'] = self.db.sample(res_data['time_start'],res_data['time_end'],station,channel,False, filter)
                    except Exception,e:
                        _error("Exception on data: %s" % e,res_data,True)

                    res_data[station][channel]['format'] = 'lines'

                else:

                    binsize = points/config.canvas_size_default
                    try:
                        res_data[station][channel]['data'] = self.db.samplebins(res_data['time_start'], res_data['time_end'], station, channel, binsize, False, filter)
                    except Exception,e:
                        _error("Exception on data: %s" % e,res_data,True)

                    res_data[station][channel]['format'] = 'bins'

        if not res_data:
            _error("No data out of db.sample or db.samplebins",res_data)

        return res_data
#}}}

    def coverage(self, params=None, stations=None):
    #{{{
        """
        Get list of segments of data for the respective station and channel
        """
        sta_str  = ''
        chan_str = ''
        res_data = defaultdict(dict)

        res_data.update( {'type':'coverage'} )
        res_data.update( {'format':'cov-bars'} )

        """
        Setting stations
        """
        # Handle wildcards on station values
        if 'sta' in params:
            res_data['sta'] = self._get_matched_stations(params['sta'])
        else:
            res_data['sta'] = self._get_matched_stations()

        """
        Setting channels
        """
        # Handle wildcards on channel values
        if 'chan' in params:
            res_data['chan'] = self._get_matched_channels(params['chan'])
        else:
            res_data['chan'] = self._get_matched_channels()

        #
        # Build dictionary to store data
        #
        #   We need to build this to tell the application
        #   that some stations may have no data.
        for sta in res_data['sta']:
            for chan in params['chan']:
                if chan in stations.channels(sta):
                    res_data[sta][chan] = {}

        #
        # Start wfdisc query
        #
        db = Dbptr(self.db)
        db.process([ 'dbopen wfdisc', ])

        # Subset wfdisc for stations
        if 'chan' in params:
            sta_str  = "|".join(str(x) for x in params['sta'])
            db.subset("sta =~/%s/" % sta_str)
            if config.debug: log.msg("\n\nCoverage subset on sta =~/%s/ " % sta_str)

        # Subset wfdisc for channels
        if 'chan' in params:
            chan_str  = "|".join(str(x) for x in params['chan'])
            db.subset("chan =~/%s/" % chan_str)
            if config.debug: log.msg("\n\nCoverage subset on chan =~/%s/ " % chan_str)

        # Subset wfdisc for start_time
        if 'time_start' in params:
            res_data.update( {'time_start':params['time_start']} )
            db.subset("endtime >= %s" % params['time_start'])
            if config.debug: log.msg("\n\nCoverage subset on time >= %s " % params['time_start'])

        # Subset wfdisc for end_time
        if 'time_end' in params:
            res_data.update( {'time_end':params['time_end']} )
            db.subset("time <= %s" % params['time_end'])
            if config.debug: log.msg("\n\nCoverage subset on time_end <= %s " % params['time_end'])

        if not db.query(dbRECORD_COUNT):
            _error('No records for: %s' %  params, res_data)
            return res_data

        # If no start time on request... use min in subset
        if not 'time_start' in res_data:
            res_data.update( {'time_start': db.ex_eval('min(time)') })

        # If no end time on request... use max in subset
        if not 'time_end' in res_data:
            res_data.update( {'time_end': db.ex_eval('max(endtime)') })


        for i in range(db.query(dbRECORD_COUNT)):

            db.record = i

            try:
                (this_sta,this_chan,time,endtime) = db.getv('sta','chan','time','endtime')
            except Exception,e:
                _error("Exception on data: %s" % e,res_data)

            if not this_sta in res_data['sta']:
                res_data['sta'].append(this_sta)
            if not this_chan in res_data['chan']:
                res_data['chan'].append(this_chan)

            # Build the dictionary
            #if not this_sta in res_data:
            #    res_data[this_sta] = {}
            #if not this_chan in res_data[this_sta]:
            #    res_data[this_sta][this_chan] = {}
            #if not 'data' in res_data[this_sta][this_chan]:
            #    res_data[this_sta][this_chan] = { 'data':[] }
            try:
                res_data[this_sta][this_chan]['data'].append([time,endtime])
            except:
                res_data[this_sta][this_chan]['data'] = [[time,endtime]]

        return res_data
    #}}}
#}}}
