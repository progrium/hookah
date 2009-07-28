from twisted.web import client, error, http
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import defer

import urllib
import time

from hookah import dispatch, queue, stream

subscriptions = dict() # Key: topic, Value: list of subscriber callback URLs

class FetchQueue(queue.Queue):
    def receivedMessage(self, url):
        subscribers = len(subscriptions.get(url, []))
        if subscribers:
            print "Fetching %s for %s subscribers" % (url, subscribers)
            client.getPage(url, headers={'X-Hub-Subscribers': subscribers}) \
                .addCallbacks(lambda p: queue.put('dispatch', {'topic': url, 'data': p, 'content_type': 'application/atom+xml'}))

class DispatchQueue(queue.Queue):
    def receivedMessage(self, message):
        subscribers = subscriptions.get(message['topic'], None)
        if subscribers:
            print "Dispatching new content for %s to %s subscribers" % (message['topic'], len(subscribers))
            for subscriber in subscribers:
                dispatch.post_and_retry(subscriber, message['data'], content_type=message['content_type'])
        if message['topic'] in stream.listeners:
            for request in stream.listeners[message['topic']]:
                request.queue.put(message['data'])

class VerifyQueue(queue.Queue):
    def receivedMessage(self, to_verify):
        print "Verifying %s as a subscriber to %s" % (to_verify['callback'], to_verify['topic'])
        challenge = baseN(abs(hash(time.time())), 36)
        verify_token = to_verify.get('verify_token', None)
        payload = {'hub.mode': to_verify['mode'], 'hub.topic': to_verify['topic'], 'hub.challenge': challenge}
        if verify_token:
            payload['hub.verify_token'] = verify_token
        url = '?'.join([to_verify['callback'], urllib.urlencode(payload)])
        def success(page):
            if challenge in page:
                if to_verify['mode'] == 'subscribe':
                    if not to_verify['topic'] in subscriptions:
                        subscriptions[to_verify['topic']] = []
                    subscriptions[to_verify['topic']].append(to_verify['callback'])
                else:
                    subscriptions[to_verify['topic']].remove(to_verify['callback'])
                if 'onsuccess' in to_verify:
                    to_verify['onsuccess'](page)
            else:
                if 'onfail' in to_verify:
                    to_verify['onfail'](page)
        def failure(x):
            if 'onfail' in to_verify:
                to_verify['onfail'](x)
        client.getPage(url).addCallbacks(success, failure)

def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"): 
    return ((num == 0) and  "0" ) or (baseN(num // b, b).lstrip("0") + numerals[num % b])

class SubscribeResource(Resource):
    isLeaf = True
    
    def render_POST(self, request):
        mode        = request.args.get('hub.mode', [None])[0]
        callback    = request.args.get('hub.callback', [None])[0]
        topic       = request.args.get('hub.topic', [None])[0]
        verify      = request.args.get('hub.verify', [None])
        verify_token = request.args.get('hub.verify_token', [None])[0]
        
        if not mode or not callback or not topic or not verify:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Expected 'hub.mode', 'hub.callback', 'hub.topic', and 'hub.verify'"
        
        if not mode in ['subscribe', 'unsubscribe']:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Unrecognized mode"
        
        verify = verify[0] # For now, only using the first preference of verify mode
        if not verify in ['sync', 'async']:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Unsupported verification mode"
            
        to_verify = {'mode': mode, 'callback': callback, 'topic': topic, 'verify_token': verify_token}
        if verify == 'sync':
            def finish_success(request):
                request.setResponseCode(http.NO_CONTENT)
                request.write("204 Subscription created")
                request.finish()
            def finish_failed(request):
                request.setResponseCode(http.CONFLICT)
                request.write("409 Subscription verification failed")
                request.finish()
            to_verify['onsuccess'] = lambda x: finish_success(request)
            to_verify['onfail'] = lambda x: finish_failed(request)
            queue.put('verify', to_verify)
            return NOT_DONE_YET
            
        elif verify == 'async':
            queue.put('verify', to_verify)
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled for verification"


class PublishResource(Resource):
    isLeaf = True
    
    def render_POST(self, request):
        mode = request.args.get('hub.mode', [None])[0]
        url = request.args.get('hub.url', [None])[0]
        
        if not mode or not url:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Expected 'hub.mode' and 'hub.url'"
        
        if mode == 'publish':
            queue.put('fetch', url)
            request.setResponseCode(http.NO_CONTENT)
            return "204 Published"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 Bad request: Unrecognized mode"

queue.register('dispatch', DispatchQueue())
queue.register('verify', VerifyQueue())
queue.register('fetch', FetchQueue())