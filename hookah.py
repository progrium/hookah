from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
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


class HookahResource(Resource):
    def getChild(self, name, request):
        return HookahResource()

    def render(self, request):
        if request.prepath in ['favicon.ico', 'robots.txt']:
            return
        if len(request.prepath):
            url = 'http://%s' % '/'.join(request.prepath)
            threading.Thread(target=post_and_retry, args=[url, request.args]).start()
            return "OK"
        else:
            return "No destination."
            
if __name__ == '__main__':
    reactor.listenTCP(PORT, Site(HookahResource()))
    reactor.run()