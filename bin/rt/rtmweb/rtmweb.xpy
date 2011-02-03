import time
import subprocess
import datetime
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type',    'text/html')
            self.end_headers()
            self.wfile.write(str(datetime.datetime.now()))
            self.wfile.write("<h2>RTMWEB</h2>")

            p = subprocess.Popen('ls -l', bufsize=-1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            for line in p.stdout.readlines(): self.wfile.write(line + "<BR>")

            return

        except:
            print 'Bad Request.' 
            self.send_error(400,'Bad Request. Not understood by the server due to malformed syntax. ')


    def do_POST(self):
        print 'Sorry! POST Not Supported'
        self.send_error(403,'Sorry! POST Not Supported')

def main():
    try:
        server = HTTPServer(('', 8000), MyHandler)
        print 'started rtmweb...'
        server.serve_forever()
    except Exception,e:
        print 'Shutting down server. %s[%s]' % (Exception,e)
        server.socket.close()

if __name__ == '__main__':
    main()

