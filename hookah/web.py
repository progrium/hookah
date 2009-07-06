from twisted.web import client, error, http
from twisted.web.resource import Resource

import dispatch, pubsub

class HookahResource(Resource):
    isLeaf = False
    
    def getChild(self, name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)

    def render(self, request):
        path = '/'.join(request.prepath)
        
        if path in ['favicon.ico', 'robots.txt']:
            return
        
        return "TODO: Show some documentation"
    
    @classmethod
    def setup(cls):
        # These should probably go somewhere else
        pubsub.fetch_queue.get().addCallback(pubsub.do_fetch)
        pubsub.dispatch_queue.get().addCallback(pubsub.do_dispatch)
        pubsub.verify_queue.get().addCallback(pubsub.do_verify)
        
        r = cls()
        r.putChild('dispatch', dispatch.DispatchResource())
        r.putChild('subscribe', pubsub.SubscribeResource())
        r.putChild('publish', pubsub.PublishResource())
        return r
