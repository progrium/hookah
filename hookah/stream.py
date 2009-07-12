from twisted.web import client, error, http, server
from twisted.web.resource import Resource

# known sessions, session list
# request gets a queue
# buffer between main queue and request queue
# push adds to buffer queue, adds to any request buffers

listeners = {}

def touch_active_sessions():
    for topic in listeners:
        if listeners[topic]:
            for request in listeners[topic]:
                request.getSession().touch()

def __mk_session_exp_cb(self, sid):
    def f():
        print "Expired session", sid
        del sessions[sid]
    return f
    
def __req_finished(whatever, sid):
    sessions[sid] = None

class StreamResource(Resource):
    isLeaf = True
    
    def render_GET(self, request):
        session = request.getSession()
        if session.uid not in sessions:
            sessions[session.uid] = request
            session.notifyOnExpire(__mk_session_exp_cb(session.uid))
        request.notifyFinish().addBoth(__req_finished, session.uid)
        return server.NOT_DONE_YET