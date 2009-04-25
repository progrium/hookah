from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web import client
import urllib
import sys

PORT = 8000 if len(sys.argv) < 2 else int(sys.argv[1])
RETRIES = 3
DELAY_MULTIPLIER = 5

def post_and_retry(url, params, retry=0):
    print "Posting [%s] to %s with %s" % (retry, url, params)
    postdata = urllib.urlencode(params)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(postdata)),
    }
    client.getPage(url, method='POST' if len(postdata) else 'GET', headers=headers, postdata=postdata if len(postdata) else None).addCallbacks( \
                    if_success, lambda reason: if_fail(reason, url, params, retry))

def if_success(page): pass
def if_fail(reason, url, params, retry):
    print reason.getErrorMessage()
    if retry < RETRIES:
        retry += 1
        reactor.callLater(retry * DELAY_MULTIPLIER, post_and_retry, url, params, retry)

class HookahResource(Resource):
    def getChild(self, name, request):
        return HookahResource()

    def render(self, request):
        if request.prepath in ['favicon.ico', 'robots.txt']:
            return
        if len(request.prepath):
            url = 'http://%s' % '/'.join(request.prepath)
            post_and_retry(url, request.args)
            return "OK"
        else:
            return "No destination."
            
if __name__ == '__main__':
    reactor.listenTCP(PORT, Site(HookahResource()))
    reactor.run()