import threading
import webbrowser
import BaseHTTPServer
import SimpleHTTPServer
import logging

PORT = 8080
LOG_PATH = u'../data/UI-data/UI-data.log'
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.INFO, filename = LOG_PATH)


class TestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """The test example handler."""

    def do_POST(self):
        """Handle a post request by returning the square of the number."""
        length = int(self.headers.getheader('content-length'))        
        data_string = self.rfile.read(length)
        logging.info(data_string)
	self.wfile.write("OK")

    def do_GET(self):
       self.wfile.write("Hello")


def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = BaseHTTPServer.HTTPServer(server_address, TestHandler)
    server.serve_forever()

if __name__ == "__main__":
    start_server()
