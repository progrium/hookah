from twisted.internet import reactor
from twisted.web import client, error, http
from twisted.web.resource import Resource
from hookah import queue
import sys, os

import base64

from hookah import HookahRequest
from hookah import storage, queue

# TODO: Make these configurable
RETRIES = 3
DELAY_MULTIPLIER = 5

def dispatch_request(request):
    key = storage.instance.put(request)
    queue.instance.submit(key)

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
    client.getPage(url, method='POST' if len(data) else 'GET', headers=headers, postdata=data if len(data) else None).addCallbacks( \
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
        url = base64.b64decode(request.postpath[0])
        
        if url:
            headers = {}
            for header in ['content-type', 'content-length']:
                value = request.getHeader(header)
                if value:
                    headers[header] = value
            
            dispatch_request(HookahRequest(url, headers, request.content.read()))
            
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 No destination URL"

if __name__ == '__main__':
    from twisted.web.server import Request
    from cStringIO import StringIO
    class TestRequest(Request):
        postpath = ['aHR0cDovL3Byb2dyaXVtLmNvbT9ibGFo']
        content = StringIO("BLAH")
        
    output = DispatchResource().render(TestRequest({}, True))
    print output
    assert output == 'BLAH'