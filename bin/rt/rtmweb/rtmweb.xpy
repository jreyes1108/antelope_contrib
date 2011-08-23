import os
import re
import sys
import time
import shlex
import getopt
import urlparse
import subprocess
try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except Exception,e:
    print "Problem loading BaseHTTPServer lib. (%s)" % e
    sys.exit()

try:
    import antelope.datascope as datascope
    import antelope.stock as stock
except Exception,e:
    print "Problem loading Antelope's Python libraries. (%s)" % e
    sys.exit()

def usage():
    print "\trtmweb [-v] [-p pf_file] [path_rtexec]\n"
    sys.exit(-1)

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        running = 0
        procs = []
        parsed_path = urlparse.urlparse(self.path)
        
        parsed_list = urlparse.parse_qs(parsed_path.query)

        if verbose:
            message_parts = [
                    'SERVER PARAMS:',
                    'rtexec=%s' % rtexec,
                    'rt_path=%s' % rt_path,
                    'email=%s' % email,
                    'title=%s' % title,
                    '',
                    'CLIENT VALUES:',
                    'client_address=%s (%s)' % (self.client_address,
                                                self.address_string()),
                    'command=%s' % self.command,
                    'path=%s' % self.path,
                    'real path=%s' % parsed_path.path,
                    'query=%s' % parsed_path.query,
                    'parsed_data=%s' % parsed_list,
                    'request_version=%s' % self.request_version,
                    '',
                    'SERVER VALUES:',
                    'server_version=%s' % self.server_version,
                    'sys_version=%s' % self.sys_version,
                    'protocol_version=%s' % self.protocol_version,
                    '',
                    'HEADERS RECEIVED:',
                    ]
            for name, value in sorted(self.headers.items()):
                message_parts.append('%s=%s' % (name, value.rstrip()))
            message_parts.append('')
            message = '\r\n'.join(message_parts)
            print message

        if parsed_path.path == '/ajax/log':

            if 'proc' in parsed_list:
                try :
                    read_file = rt_path + '/logs/' + parsed_list['proc'][0]
                    if os.path.isfile(read_file):
                        file = open(read_file)
                        response = file.read().replace("\n","<br>\n")
                        file.close()
                    else:
                        response = 'Cannot find log %s ' % read_file

                except Exception,e:
                    response = 'Problem while reading log %s [%s: %s]' % (parsed_list['proc'],Exception,e)

            else: 
                response = 'Need name of task to look for log!'

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write( "<p>"+response+"</p>" )

        elif parsed_path.path == '/ajax/cmd':
            response = 'Not implemented now...'
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write( response )

        else:
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Read javascript file
                file = open(js_file)
                while 1:
                    line  = file.readline()
                    if not line:
                        break
                    self.wfile.write(line)
                file.close()

                self.wfile.write('<body style="background-color:#b0c4de;">' )
                self.wfile.write("<h2>%s</h2>" % title)
                self.wfile.write("<p>%s</p>" % stock.strydtime(stock.now()))
                self.wfile.write('<p>%s/rtexec.pf</p>' % rt_path)


                try:
                    file = open(rt_path + '/rtsys/rtsys.process')
                    # iterate over the lines in the file
                    while 1:
                        line  = file.readline()
                        if not line:
                            break
                        if re.search('.* rtexec -M -s.*', line):
                            # split the line into a list of column values
                            columns = shlex.split(line)

                            if columns[1] == '-1':
                                self.wfile.write("<div style='padding:10px; background-color:#FEA320'>SYSTEM IS DOWN!</div><br><br>") 
                            elif columns[1] > 1:
                                self.wfile.write("<div style='padding:10px; background-color:#20D077'>SYSTEM IS UP [pid:%s]</div><br><br>" % columns[1]) 
                                running = 1 
                            else:
                                self.wfile.write("<div style='padding:10px; background-color:#FD0010'>ERROR LOOKING for RTEXEC in rtsys.process [%s]</div><br><br>" % columns) 
                        else:
                            procs.append(line)
                    file.close()


                except Exception,e:
                    self.wfile.write("<p>Cannot open file %s/rtsys/rtsys.process [%s:%s]</p>" % (rt_path,Exception,e))

                self.wfile.write("<hr>")
                if not running:
                    try:
                        file = open(rt_path + '/rtsys/rtsys.shutdown')
                        lines = file.read().split('\n')
                        lines.remove('')
                        if lines[-1]:
                            columns = lines[-1].split()
                            self.wfile.write("<i>Last entry on rtsys.shutdown: [%s  %s:  %s]</i><br>" % (stock.strydtime(float(columns[0])),columns[1],columns[2])) 
                        else:
                            self.wfile.write("<i>No entries on rtsys.shutdown!</i><br>") 
                        file.close()

                    except Exception,e:
                        self.wfile.write("<p>Cannot open file %s/rtsys/rtsys.shutdown [%s:%s]</p>" % (rt_path,Exception,e))

                else:
                    self.wfile.write("<h3>Processing Tasks (click for log)</h3>")

                    for line in procs:
                        try:
                            columns = shlex.split(line)

                            #self.wfile.write(columns)
                            if columns[1] == '-1':
                                self.wfile.write("<div id='%s' style='padding:5px; color:#FD0010;' onClick='JavaScript:getlog(\"%s\")'><i>%s [pid:%s] [started:%s]</i></div><br>"% (columns[0],columns[0],columns[0],columns[1],stock.strydtime(float(columns[5])) )) 
                            elif columns[1] > 1:
                                self.wfile.write("<div id='%s' style='padding:5px;' onClick='JavaScript:getlog(\"%s\")'><b>%s [pid:%s] [started:%s]</b></div><br>"% (columns[0],columns[0],columns[0],columns[1],stock.strydtime(float(columns[5])) )) 
                            else:
                                self.wfile.write("<div style='padding:10px; background-color:#FD0010'>%s [error with task [%s]]</div><br><br>" % (columns[0],columns)) 

                        except Exception,e:
                            self.wfile.write("<div style='padding:10px; background-color:#FD0010'>[error with task %s [%s:%s]]</div><br><br>" % (columns,Exception,e)) 


                self.wfile.write("<hr>")
                self.wfile.write("<h3>All Available Tasks</h3>")
                try:
                    for line in os.popen('rtkill -l').read().split('\n'):
                        if line and not re.search('.*Available tasks are:.*', line):
                            cmd = shlex.split(line)
                            if cmd[1] == 'on':
                                self.wfile.write("<div id='%s_run' style='padding:0;'><b>%s </b><button onClick='JavaScript:cmd(\"%s\")'>STOP</button></div><br>"% (cmd[0],cmd[0],cmd[0])) 
                            else:
                                self.wfile.write("<div id='%s_run' style='padding:0;'><b>%s </b><button onClick='JavaScript:cmd(\"%s\")'>START</button></div><br>"% (cmd[0],cmd[0],cmd[0])) 
                except Exception,e:
                    self.wfile.write("<div style='padding:10px; background-color:#FD0010'>Cannot run {rtkill -l} [%s:%s]]</div><br><br>" % (Exception,e)) 


                self.wfile.write("<hr>")

                if email:
                    self.wfile.write("<p>email: "+email+"</p>")

                self.wfile.write("</body>")

            except:
                print '#########################################\n',
                print '[%s] ERROR ON REQUEST.\n' % stock.strydtime(stock.now())
                print '\tclient_address=%s (%s)\n' % (self.client_address,self.address_string()),
                print '\tcommand=%s\n' % self.command,
                print '\tpath=%s\n' % self.path,
                print '\treal path=%s\n' % parsed_path.path,
                print '\tquery=%s\n' % parsed_path.query,
                print '\trequest_version=%s\n' % self.request_version,
                self.send_error(400,'Bad Request. Not understood by the server due to malformed syntax. ')
                print '#########################################\n',

        return


    def do_POST(self):
        print 'Sorry! POST Not Supported'
        self.send_error(403,'Sorry! POST Not Supported')


if __name__ == '__main__':
    #
    # Default values...
    #
    rtexec = './'
    pfname = 'trmweb'
    verbose = 0
    password = ''
    title = 'RTMWEB - Antelope. BRTT'
    email = ''
    port = 8000

    #
    # Get parameters form command line
    #
    try:
        opts, pargs = getopt.getopt(sys.argv[1:], 'p:v')
    except:
        usage()

    for option, value in opts:

        if '-p' in option:
            pfname = str(value)

        if '-v' in option:
            verbose = 1


    #
    # Get path to rtexec.pf
    #
    if len(pargs) == 0:
        rtexec = os.path.abspath('./rtexec.pf')
    elif len(pargs) == 1:
        rtexec = os.path.abspath(pargs[0])
    else:
        usage()

    if verbose: print "rtexec: %s" % rtexec


    #
    # Verify path to rtexec.pf file
    #
    if os.path.isfile(rtexec):
        rt_path = os.path.dirname(rtexec)
    elif os.path.isfile(rtexec+'/rtexec.pf'):
        rt_path = rtexec
    else:
        print "Cannot find any rtexec.pf file in [%s]\n" % rtexec
        usage()

    if verbose: print "rt_path: %s" % rt_path
    os.chdir(rt_path)


    js_file = os.environ['ANTELOPE']+'/local/data/python/rtmweb/rtmweb_javascript.js'
    if not os.path.isfile(js_file):
        print "Cannot find javascript code file in [%s]\n" % js_file
        usage()



    #
    # Load PF file
    #
    try:
        port = stock.pfget_int( pfname, "port" )
    except:
        pass

    try:
        restart_time = stock.pfget_int( pfname, "restart_sleep_time_sec" )
    except:
        pass

    try:
        password = stock.pfget_string( pfname, "password" )
    except:
        pass

    try:
        title = stock.pfget_string( pfname, "application_title" )
    except:
        pass

    try:
        email = stock.pfget_string( pfname, "email" )
    except:
        pass

    server = HTTPServer(('', port), GetHandler)
    try:
        print '\n[%s] Starting server, use <Ctrl-C> to stop\n' % stock.strydtime(stock.now())
        server.serve_forever()
    except:
        pass

    server.server_close()
    print '\n[%s] Stoping server!\n' % stock.strydtime(stock.now())

