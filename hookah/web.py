from twisted.python.util import sibpath
from twisted.web import client, error, http, static
from twisted.web.resource import Resource
from twisted.internet import task

from hookah import dispatch

class HookaRequest(object):

    def __init__(self, url, headers, query, body):
        self.url = url
        self.headers = headers
        self.query = query
        self.body = body

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
        r.putChild('dispatch', dispatch.DispatchResource())
        return r
