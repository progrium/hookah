import cherrypy
import threading
import urllib, urllib2
import os, sys

PORT = 8000 if len(sys.argv) < 2 else int(sys.argv[1])
RETRIES = 3
DELAY_MULTIPLIER = 5

def post_and_retry(url, params, retry=0):
    print "Posting [%s] to %s with %s" % (retry, url, params)
    try:
        urllib2.urlopen(url, urllib.urlencode(params) if len(params) else None)
    except urllib2.HTTPError, e:
        print e
        if retry < RETRIES:
            retry += 1
            threading.Timer(retry * DELAY_MULTIPLIER, post_and_retry, args=[url, params, retry]).start()
    
class Root:
    @cherrypy.expose
    def default(self, *path, **params):
        if path:
            url = 'http://%s' % '/'.join(path)
            threading.Thread(target=post_and_retry, args=[url, cherrypy.request.params]).start()
            return "OK"
        else:
            return "No destination."
            
if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': PORT,})
    root = Root()
    cherrypy.quickstart(root)
    