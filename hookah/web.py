from twisted.web import client, error, http
from twisted.web.resource import Resource

import dispatch

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
            params = {}
            for k in request.args:
                value = request.args[k]
                if type(value) is list and len(value) == 1:
                    params[k] = value[0]
                else:
                    params[k] = value
            dispatch.post_and_retry(url, params)
            request.setResponseCode(http.ACCEPTED)
            return "202 Scheduled"
        else:
            request.setResponseCode(http.BAD_REQUEST)
            return "400 No destination URL"
