from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web import client, error, http
import urllib
import sys

RETRIES = 3
DELAY_MULTIPLIER = 5

def post_and_retry(url, params, retry=0):
    print "Posting [%s] to %s with %s" % (retry, url, params)
    postdata = urllib.urlencode(params)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': str(len(postdata)),
    }
    client.getPage(url, followRedirect=0, method='POST' if len(postdata) else 'GET', headers=headers, postdata=postdata if len(postdata) else None).addCallbacks( \
                    if_success, lambda reason: if_fail(reason, url, params, retry))

def if_success(page): pass
def if_fail(reason, url, params, retry):
    if reason.getErrorMessage()[0:3] in ['301', '302', '303']:
        return # Not really a fail
    print reason.getErrorMessage()
    if retry < RETRIES:
        retry += 1
        reactor.callLater(retry * DELAY_MULTIPLIER, post_and_retry, url, params, retry)

class HookahResource(Resource):
    def getChild(self, name, request):
        return HookahResource()

    def render(self, request):
        path = '/'.join(request.prepath)
        
        if path in ['favicon.ico', 'robots.txt']:
            return
        
        url_param = request.args.get('_url', [None])[0]
        if url_param:
            del request.args['_url']
        
        url = 'http://%s' % path if len(path) else url_param
        if url:
            post_and_retry(url, request.args)
            return "200 Scheduled"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 No destination URL"
