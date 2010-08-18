from __main__ import *

"""
Import Python module JSON or SimpleJSON to 
parse returned results from queries
bsed on Python version test
"""

#log.startLogging(sys.stdout)
#log.msg('Re-start logging ...')


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
    Serve HTML query requests.
    """
#{{{
    def __init__(self,db):
#{{{
        isLeaf = True

        self.dbname = db

        if not os.path.isfile(db):
            log.msg('\n\nERROR on database name %s' % self.dbname)
            sys.exit('Killing Server: No file found (%s)\n'% self.dbname)
    
        try:
            self.db = datascope.dbopen(self.dbname)
        except:
            log.msg('\n\nERROR on database %s' % self.dbname)
            sys.exit('Killing Server: No database found (%s)'% self.dbname)


        db = datascope.Dbptr(self.db)

        db.lookup( table='wfdisc')

        if db.query(datascope.dbTABLE_PRESENT): 
            for check in ['instrument','sensor','origin','arrival']:
                try: db.lookup( table=check )
                except:
                    sys.exit('\n\nKilling Server: Problem on db.lookup on db:%s\n\n'% self.dbname)

                if not db.query(datascope.dbTABLE_PRESENT):
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


        resource.Resource.__init__(self)

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
                jquery_includes += '\n\t<!--[if IE]>\n'
                jquery_includes += '\t\t<script language="javascript" type="text/javascript" src="'
                jquery_includes += jqf + '"></script>\n\t<![endif]-->\n'

            else:

                jquery_includes += '\n\t<script type="text/javascript" src="' + jqf + '"></script>\n'

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
        #if name == '':
        #    return self
        #return resource.Resource.getChild(self, name, request)
        return self
#}}}

    def render_GET(self, request):
#{{{
        response_data = defaultdict()

        tvals = defaultdict(dict)

        tvals = { 
            "dir":               '&mdash;',
            "key":               '&mdash;',
            "error":             'false',
            "meta_query":        'false'
        }

        #
        # Old method of parsing the URI
        #
        #args = request.uri.split("/")[1:]
        #
        # New method using request.postpath and request.args
        #
        
        if config.debug:
            log.msg('')
            log.msg('Request:%s' % request )
            log.msg('Request.uri:%s' % request.uri)
            log.msg('Request.args:%s' % (request.args) )
            log.msg('Request.prepath:%s' % (request.prepath) )
            log.msg('Request.postpath:%s' % (request.postpath) )
            log.msg('Request.path:%s' % (request.path) )
            log.msg('')

        args = request.args
        path = request.prepath

        if config.verbose:
            log.msg('')
            log.msg('Parsing of URI:')
            log.msg('\targs:(size %s)%s' % (len(args),args) )
            log.msg('\tpath:(size %s)%s' % (len(path),path) )
            log.msg('')

        #
        # remove all empty  elements
        # This (localhost:8008/stations/) is the same as 
        # (localhost:8008/stations) 
        #
        if config.debug:
            log.msg('Removing empty arguments path:(size %s)%s' % (len(path),path) )

        while True:
            try: 
                path.remove('')
            except: 
                break

        if config.debug:
            log.msg('Fixed arguments path:(size %s)%s' % (len(path),path) )


        if path:

            log.msg("\tQUERY: %s " % path)

            if path[0] == 'data':
                if config.verbose:
                    log.msg("Data query of type: %s " % path[0])

                request.setHeader("content-type", "application/json")

                if 'meta' in path:
#{{{
                    """
                    TEST metaquery parsing response. Return json with meta-query data for further ajax requests.
                    """
                    return json.dumps(self.eventdata.parse_query(self._parse_url(path), self.stations, self.events))

#}}}

                elif 'wf' in path:
#{{{
                    """
                    Return JSON object of data. For client ajax calls.
                    """

                    return json.dumps(self.eventdata.get_segment(self._parse_url(path), self.stations, self.events))

#}}}

                elif 'coverage' in path:
#{{{
                    """
                    Return coverage tuples as JSON objects. For client ajax calls.
                    """

                    return json.dumps(self.eventdata.coverage(self._parse_url(path),self.stations))

#}}}

                elif 'events' in path:
#{{{
                    """
                    Return events dictionary as JSON objects. For client ajax calls.
                    Called with or without argument
                    """

                    if len(path) == 3:

                        for event in [path['time']]:
                            response_data[event] = self.events(event)
                        return json.dumps(response_data)

                    elif len(path) == 4:
                        return json.dumps(self.events.phases(path[2],path[3]))

                    else:
                        return json.dumps(self.events.table())
#}}}

                elif 'times' in path:
#{{{
                    """
                    Return tuples of min time and max time in db
                    for a list of stations or for the complete db.
                    """
                    if len(path) == 3:
                        path = self._parse_url(path)

                        for sta in path['sta']:
                            log.msg("\n\n\tcalling self.stations.times(%s)\n\n" % sta)
                            response_data[sta] = self.stations.times(sta)
                        return json.dumps(response_data)

                    else:
                        return json.dumps(self.stations.times())
#}}}

                elif 'stations' in path:
#{{{
                    """
                    Return station list as JSON objects. For client ajax calls.
                    Called with argument return dictionary
                    """
                    if len(path) == 3:
                        path = self._parse_url(path)

                        for sta in path['sta']:
                            log.msg("\n\n\tcalling self.stations(%s)\n\n" % sta)
                            response_data[sta] = self.stations(sta)
                        return json.dumps(response_data)

                    else:
                        return json.dumps(self.stations.list())
#}}}

                elif 'channels' in path:
#{{{
                    """
                    Return channels list as JSON objects. For client ajax calls.
                    """
                    return json.dumps(self.stations.channels())
#}}}

                elif 'filters' in path:
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
                    evdata._error("Unknown type of query: %s" % path)
                    tvals['error'] =  json.dumps( "Unknown query type:(%s)" % path )
                #}}}

            elif path[0] == 'wf':
#{{{
                """
                Parse query for data request. Return html with meta-query data for further ajax requests.
                """
                log.msg('path: %s (%s)' % (len(path),str(path)))

                tvals['meta_query'] = json.dumps(self.eventdata.parse_query(self._parse_url(path), self.stations, self.events))

                tvals['dir'] = 'wf'
                #path.remove('wf')

                tvals['key']  = " / ".join(str(x) for x in path)

#}}}

            elif path[0] != '':
                request.setHeader("response-code", 500)
                evdata._error("Unknown type of query: %s" % path)
                tvals['error'] =  json.dumps( "Unknown query type:(%s)" % path )


        template = config.full_template

        if 'mode' in args:
            if args['mode'][0] == 'iframe':
                template = config.iframe_template
        if 'mode' in args:
            if args['mode'][0] == 'simple':
                template = config.simple_template


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
#}}}
#}}}
