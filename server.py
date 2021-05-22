import logging
from http.server import HTTPServer
from requesthandler import HTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    logging.getLogger().setLevel(logging.INFO)
    httpd = ThreadedHTTPServer(("0.0.0.0", 80), HTTPRequestHandler)
    logging.info("Starting Server\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopped Server\n")


run()
