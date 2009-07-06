from twisted.internet import reactor
from twisted.web import client, error, http
from twisted.web.resource import Resource
import urllib
import sys

# TODO: Make these configurable
RETRIES = 3
DELAY_MULTIPLIER = 5

def post_and_retry(url, data, retry=0, content_type='application/x-www-form-urlencoded'):
    if type(data) is dict:
        print "Posting [%s] to %s with %s" % (retry, url, data)
        data = urllib.urlencode(data)
    else:
        print "Posting [%s] to %s with %s bytes of postdata" % (retry, url, len(data))
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(data)),
    }    
    client.getPage(url, followRedirect=0, method='POST' if len(data) else 'GET', headers=headers, postdata=data if len(data) else None).addCallbacks( \
                    if_success, lambda reason: if_fail(reason, url, data, retry, content_type))

def if_success(page): pass
def if_fail(reason, url, data, retry, content_type):
    if reason.getErrorMessage()[0:3] in ['301', '302', '303']:
        return # Not really a fail
    print reason.getErrorMessage()
    if retry < RETRIES:
        retry += 1
        reactor.callLater(retry * DELAY_MULTIPLIER, post_and_retry, url, data, retry, content_type)

class DispatchResource(Resource):
    isLeaf = True

    def render(self, request):
        path = '/'.join(request.prepath[1:])
        
        print path
        
        url_param = request.args.get('_url', [None])[0]
        if url_param:
            del request.args['_url']
        
        url = 'http://%s' % path if len(path) else url_param
        if url:
            params = {}
            for k in request.args:
                value = request.args[k]
                if type(value) is list and len(value) == 1:
                    params[k] = value[0]
                else:
                    params[k] = value
            post_and_retry(url, params)
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 No destination URL"