from twisted.web import client, error, http, server
from twisted.web.resource import Resource
from hookah import queue

# known sessions, session list
# request gets a queue
# buffer between main queue and request queue
# push adds to buffer queue, adds to any request buffers

listeners = {} # Key: topic, Value: list of requests listening
    

class StreamResource(Resource):
    isLeaf = True
    
    def render_GET(self, request):
        topic = request.args.get('topic', [None])[0]
        if not topic:
            return "No topic"
        if not topic in listeners:
            listeners[topic] = []
        request.queue = queue.Queue(lambda m: self._send(request, m))
        listeners[topic].append(request)
        request.setHeader('Content-Type', 'application/json')
        request.setHeader('Transfer-Encoding', 'chunked')
        request.notifyFinish().addBoth(self._finished, topic, request)
        return server.NOT_DONE_YET
    
    def _finished(self, whatever, topic, request):
        listeners[topic].remove(request)

    def _send(self, request, message):
        request.write(message)