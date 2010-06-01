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
    def __init__(self):
#{{{
        resource.Resource.__init__(self)

        self.dbname = config.dbname
        self.db = dbopen(self.dbname)

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
        template = config.html_template

        response_data = defaultdict()

        tvals = defaultdict(dict)

        tvals = { 
            "dir":               '&mdash;',
            "key":               '&mdash;',
            "error":             'false',
            "meta_query":        'false',
            "coverage":          'false',
            "event_list":        'false',
            "event_data":        'false',
            "event_selc":        'false',
            "station_selc":      'false',
            "station_data":      'false',
            "station_list":      'false',
            "dbname":            config.dbname,
            "application_title": config.application_title,
            "jquery_includes":   self._jquery_includes(),
            "filters":           '<option value="None">None</option>'
        }

        for filter in config.filters:
            tvals['filters'] += '<option value="'+config.filters[filter].replace(' ','_')+'">'
            tvals['filters'] += filter
            tvals['filters'] += '"</option>'

        if config.display_arrivals:
            tvals['display_arrivals'] = 'checked="checked"'
        else:
            tvals['display_arrivals'] = ''

        args = request.uri.split("/")[1:]

        #
        # remove last element if it's empty... 
        # This (localhost:8008/stations/) is the same as 
        # (localhost:8008/stations) 
        #
        if args[len(args)-1] == '':
            args.pop()
#}}}

        if args:

            tvals['dir'] = args[0]

            log.msg("\tQUERY: %s " % args)

            if args[0] == 'data':
                #{{{
                if config.verbose:
                    log.msg("Data query of type: %s " % args[0])

                request.setHeader("content-type", "application/json")

                if 'wf' in args:
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

                    response_data.update(self.eventdata.coverage(self._parse_url(args)))

                    return json.dumps(response_data)
#}}}

                elif 'events' in args:
#{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument
                    """
                    if len(args) == 3:
                        args = self._parse_url(args)

                        for event in args[2]:
                            log.msg("\n\n\tcalling self.events(%s)\n\n" % event)
                            response_data[event] = self.events(event)
                        return json.dumps(response_data)

                    else:
                        return json.dumps(self.events.table())
#}}}

                elif 'stations' in args:
#{{{
                    """
                    Return station dictionary as JSON objects. For client ajax calls.
                    Called with or without argument
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
                    dbwfserver.eventdata._error("Unknown type of query: %s" % args)
                    tvals['error'] =  json.dumps( "Unknown query type:(%s)" % args )
#}}}

                #}}}

            elif args[0] == 'events':
#{{{
                if len(args) > 1:

                    tvals['key'] = args[1]
                    tvals['event_selc'] = args[1]
                    tvals['station_list'] = self.stations.list()

                else:

                    tvals['event_list'] = json.dumps(self.events.table())

#}}}

            elif args[0] == 'stations':
#{{{
                if len(args) > 1:

                    tvals['key'] = args[1]
                    args = self._parse_url(args)
                    tvals['station_data'] = {}

                    for sta in args['sta']:
                        if config.debug: log.msg("\n\n\tcalling self.stations(%s)\n\n" % sta)
                        tvals['station_data'][sta] = json.dumps( self.stations(sta) )

                    if not tvals['station_data']:
                        dbwfserver.eventdata._error("No matching station in db: %s" % args)
                        tvals['error'] =  json.dumps( "No matching station in db: %s" % args )

                    tvals['station_selc'] = json.dumps( args['sta'] )
                    tvals['event_list'] = json.dumps(self.events.table())

                else:

                    tvals['station_list'] = json.dumps( self.stations.list() )

#}}}

            elif args[0] == 'wf':
#{{{
                """
                Parse query for data request. Return html with meta-query data for further ajax requests.
                """
                log.msg('args: %s (%s)' % (len(args),str(args)))
                if len(args) > 2:

                    tvals['meta_query'] = json.dumps(self.eventdata.parse_query(self._parse_url(args), self.stations, self.events))

                    args.remove('wf')
                    tvals['key']  = " / ".join(str(x) for x in args)

                else:
                    request.setHeader("response-code", 500)
                    dbwfserver.eventdata._error("You must provide a station code and epoch time or origin: %s" % args)
                    tvals['error'] =  json.dumps( "You must provide a station code and epoch time or origin: %s" % args )

#}}}

            elif args[0] == 'coverage':
#{{{
                """
                Parse query for coverage and return data inside html code.
                """

                tvals['coverage'] = json.dumps(self._parse_url(args))

                args.remove('coverage')
                tvals['key']  = " / ".join(str(x) for x in args)

#}}}

            elif args[0] != '':
                request.setHeader("response-code", 500)
                dbwfserver.eventdata._error("Unknown type of query: %s" % args)
                tvals['error'] =  json.dumps( "Unknown query type:(%s)" % args )

        html_stations = Template(open(template).read()).substitute(tvals)

        #request.write( html_stations )
        #request.finish()
        return html_stations
