from twisted.python.util import sibpath
from twisted.web import client, error, http, static
from twisted.web.resource import Resource
from twisted.internet import task

from hookah import dispatch, pubsub, stream

class HookahResource(Resource):
    isLeaf = False
    
    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'hub':
            mode = request.args.get('hub.mode', [None])[0]
            if mode in ['subscribe', 'unsubscribe']:
                print "HELLO"
                return pubsub.SubscribeResource()
            elif mode == 'publish':
                return pubsub.PublishResource()
        return Resource.getChild(self, name, request)

    def render(self, request):
        path = '/'.join(request.prepath)
        
        if path in ['favicon.ico', 'robots.txt']:
            return

        return self.index()

    def index(self):
        
        def subscriberRow(url):
            return '<div><a href="%s">%s</a></div>' % (url, url)

        subscriptionList = "\n".join(
            '<dt>Topic: <span class="topic">%s</span></dt><dd>%s</dd>' % (
                topic, '\n'.join(map(subscriberRow, subscribers)))
            for topic, subscribers in
            sorted(pubsub.subscriptions.items()))
        
        return """<html>
                    <head>
		      <title>hookah admin</title>
		      <link rel="stylesheet" href="style.css"/>
		    </head>
		    <body>
		      <h1>hookah admin</h1>
                      <h2>Create subscription</h2>
                      <form method="post" action="subscribe">
                        <div>Callback URL (POST target):
                             <input type="text" name="hub.callback"/></div>
                        <div>Topic: <input type="text" name="hub.topic"/></div>
                        <div>Mode: <select name="hub.mode">
                          <option value="subscribe">subscribe</option>
                          <option value="unsubscribe">unsubscribe</option>
                          </select></div>
                        <div>Verify: <select name="hub.verify">
                          <option value="sync">sync</option>
                          <option value="async">async</option>
                          </select></div>
                        <div><input type="submit" value="Submit"/></div>
                      </form>
		      <h2>Current subscriptions</h2>
		      <dl>%(subscriptionList)s</dl>
		    </body>
                  </html>""" % vars()

    
    @classmethod
    def setup(cls):
        r = cls()
        r.putChild('dispatch', dispatch.DispatchResource())
        r.putChild('subscribe', pubsub.SubscribeResource())
        r.putChild('publish', pubsub.PublishResource())
        r.putChild('stream', stream.StreamResource())
        r.putChild('style.css', static.File(sibpath(__file__, 'styles.css')))
        return r
