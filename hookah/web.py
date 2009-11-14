from twisted.python.util import sibpath
from twisted.web import client, error, http, static
from twisted.web.resource import Resource
from twisted.internet import task




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

        return ''

    @classmethod
    def setup(cls):
        r = cls()
        from hookah import dispatch
        r.putChild('dispatch', dispatch.DispatchResource())
        return r
