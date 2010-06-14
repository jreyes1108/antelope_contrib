import sys
import re
from time import gmtime, strftime

from string import Template
from twisted.web import resource
from twisted.python import log 

import antelope.stock as stock
from antelope.datascope import *

import dbwfserver.eventdata as evdata 
import dbwfserver.config as config

from collections import defaultdict 

"""
Import Python module JSON or SimpleJSON to 
parse returned results from queries
bsed on Python version test
"""

if(float(sys.version_info[0])+float(sys.version_info[1])/10 >= 2.6):

    import json

else:

    import simplejson as json

def isNumber(test):
#{{{
    """
    Test if the string is a valid number 
    and return the converted number. 
    """
    try:
        try:
            return int(test)
        except:
            return float(test)
    except:
        return False
#}}}

class QueryParser(resource.Resource):
    """
    Serve Datascope query requests.
    """
    def __init__(self,db):
#{{{
        resource.Resource.__init__(self)

        self.dbname = db

        try:
            self.db = dbopen(self.dbname)
        except:
            log.msg('\n\nERROR on database %s' % self.dbname)
            sys.exit('Killing Server: No database found (%s)'% self.dbname)


        db = Dbptr(self.db)

        db.lookup( table='wfdisc')

        if db.query(dbTABLE_PRESENT): 
            for check in ['instrument','sensor','origin','arrival']:
                try: db.lookup( table=check )
                except:
                    sys.exit('\n\nKilling Server: Problem on db.lookup on db:%s\n\n'% self.dbname)

                if not db.query(dbTABLE_PRESENT):
                    log.msg('\n\nERROR: %s table not present in %s !!!!\n\n' % (check,self.dbname))
                    config.simple = True

        else:
            log.msg('\n\nERROR on database %s' % self.dbname)
            log.msg('Can not run server without wfdisc table present for database:% \n\n'% self.dbname)
            sys.exit('Killing Server: No wfdisc table in database (%s)'% self.dbname)

        if config.simple:
            log.msg('')
            log.msg('Running %s on SIMPLE mode (-s)'% self.dbname)
            log.msg('')
        else:
            log.msg('')
            log.msg('Running %s on FULL mode'% self.dbname)
            log.msg('')

        self.stations = evdata.Stations(self.dbname)
        self.events = evdata.Events(self.dbname)

        self.eventdata = evdata.EventData(self.dbname)
#}}}

    def _jquery_includes(self):
        # {{{
        jquery_includes = ''

        for jqf in config.jquery_files:

            if(re.match(r'^IE\s+', jqf)):

                re.sub(r'^IE\s+', '', jqf)
                jquery_includes += '<!--[if IE]>\n'
                jquery_includes += '<script language="javascript" '
                jquery_includes += 'type="text/javascript" src="'
                jquery_includes += jqf
                jquery_includes += '"></script>\n'
                jquery_includes += '<![endif]-->\n'

            else:

                jquery_includes += '<script type="text/javascript" '
                jquery_includes += 'src="'
                jquery_includes += jqf
                jquery_includes += '"></script>\n'

        return jquery_includes
        # }}}

    def _parse_url(self,args):
        # {{{

        url_params = defaultdict()

        if config.debug:
            log.msg("Original query list: %s" % str(args) ) 

        if len(args) > 0:
            if args[0] == 'data':
                args.remove('data')

        if len(args) == 2:
            url_params['sta'] = args[1].split('+')

        elif len(args) == 3:
            url_params['sta'] = args[1].split('+')
            if isNumber( args[2] ):
                url_params['time_start'] = args[2]
            else:
                url_params['chan'] = args[2].split('+')

        elif len(args) == 4:
            url_params['sta'] = args[1].split('+')
            if isNumber( args[2] ):
                url_params['time_start'] = args[2]
                url_params['time_end'] = args[3]
            else:
                url_params['chan'] = args[2].split('+')
                url_params['time_start'] = args[3]

        elif len(args) == 5:
            url_params['sta'] = args[1].split('+')
            url_params['chan'] = args[2].split('+')
            url_params['time_start'] = args[3]
            url_params['time_end'] = args[4]

        elif len(args) == 6:
            url_params['sta'] = args[1].split('+')
            url_params['chan'] = args[2].split('+')
            url_params['time_start'] = args[3]
            url_params['time_end'] = args[4]
            url_params['filter'] = args[5]

        if config.verbose:
            log.msg("Converted query: %s" % str(url_params) ) 

        return url_params
        # }}}

    def getChild(self, name, request):
#{{{
        return self
#}}}

    def render(self, request):
#{{{ Setup template, init variables

        response_data = defaultdict()

        tvals = defaultdict(dict)

        tvals = { 
            "dir":               '&mdash;',
            "key":               '&mdash;',
            "error":             'false',
            "meta_query":        'false'
        }

        args = request.uri.split("/")[1:]

        #
        # remove all empty  elements
        # This (localhost:8008/stations/) is the same as 
        # (localhost:8008/stations) 
        #
        if config.debug:
            log.msg('Removing empty arguments args:(size %s)%s' % (len(args),args) )

        while True:
            try: 
                args.remove('')
            except: 
                break

        if config.debug:
            log.msg('Fixed arguments args:(size %s)%s' % (len(args),args) )

#}}}

        if args:

            log.msg("\tQUERY: %s " % args)

            if args[0] == 'data':
                #{{{
                if config.verbose:
                    log.msg("Data query of type: %s " % args[0])

                request.setHeader("content-type", "application/json")

                if 'meta' in args:
#{{{
                    """
                    TEST metaquery parsing response. Return json with meta-query data for further ajax requests.
                    """
                    return json.dumps(self.eventdata.parse_query(self._parse_url(args), self.stations, self.events))

#}}}

                elif 'wf' in args:
#{{{
                    """
                    Return JSON object of data. For client ajax calls.
                    """

                    return json.dumps(self.eventdata.get_segment(self._parse_url(args), self.stations, self.events))

#}}}

                elif 'coverage' in args:
#{{{
                    """
                    Return coverage tuples as JSON objects. For client ajax calls.
                    """

                    response_data.update(self.eventdata.coverage(self._parse_url(args),self.stations))

                    return json.dumps(response_data)
#}}}

                elif 'events' in args:
#{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument
                    """

                    if len(args) == 3:

                        for event in [args[2]]:
                            response_data[event] = self.events(event)
                        return json.dumps(response_data)

                    elif len(args) == 4:
                        return json.dumps(self.events.phases(args[2],args[3]))

                    else:
                        return json.dumps(self.events.table())
#}}}

                elif 'stations' in args:
#{{{
                    """
                    Return station list as JSON objects. For client ajax calls.
                    Called with argument return dictionary
                    """
                    if len(args) == 3:
                        args = self._parse_url(args)

                        for sta in args[2]:
                            log.msg("\n\n\tcalling self.stations(%s)\n\n" % sta)
                            response_data[sta] = self.stations(sta)
                        return json.dumps(response_data)

                    else:
                        return json.dumps(self.stations.list())
#}}}

                elif 'channels' in args:
#{{{
                    """
                    Return channels list as JSON objects. For client ajax calls.
                    """
                    return json.dumps(self.stations.channels())
#}}}

                elif 'filters' in args:
#{{{
                    """
                    Return list of filters as JSON objects. For client ajax calls.
                    """
                    return json.dumps(config.filters, sort_keys=True)
#}}}

                else:
#{{{ ERROR: Unknown query type.
                    request.setHeader("content-type", "text/html")
                    request.setHeader("response-code", 500)
                    evdata._error("Unknown type of query: %s" % args)
                    tvals['error'] =  json.dumps( "Unknown query type:(%s)" % args )
#}}}

                #}}}

            elif args[0] == 'wf' or args[0] == 'wfframe':
#{{{
                """
                Parse query for data request. Return html with meta-query data for further ajax requests.
                """
                log.msg('args: %s (%s)' % (len(args),str(args)))

                tvals['meta_query'] = json.dumps(self.eventdata.parse_query(self._parse_url(args), self.stations, self.events))

                if args[0] == 'wf':
                    tvals['dir'] = 'wf'
                    #args.remove('wf')
                else:
                    tvals['dir'] = 'wfframe'
                    #args.remove('wfframe')

                tvals['key']  = " / ".join(str(x) for x in args)

#}}}

            elif args[0] != '':
                request.setHeader("response-code", 500)
                evdata._error("Unknown type of query: %s" % args)
                tvals['error'] =  json.dumps( "Unknown query type:(%s)" % args )


        if 'wfframe' in args:

            template = config.simple_html_template

        else:

            template = config.html_template

        tvals['dbname'] = self.dbname
        tvals['application_title'] = config.application_title
        tvals['jquery_includes'] = self._jquery_includes()
        tvals['filters'] = '<option value="None">None</option>'


        for filter in config.filters:
            tvals['filters'] += '<option value="'+config.filters[filter].replace(' ','_')+'">'
            tvals['filters'] += filter
            tvals['filters'] += '"</option>'

        if config.display_arrivals:
            tvals['display_arrivals'] = 'checked="checked"'
        else:
            tvals['display_arrivals'] = ''

        if config.simple:
            tvals['event_controls'] = ''
        else:
            tvals['event_controls'] = ' \
                <p>Get time from event list:</p> \
                <input type="submit" id="load_events" value="Show Events"/> '

        html_stations = Template(open(template).read()).substitute(tvals)

        return html_stations
