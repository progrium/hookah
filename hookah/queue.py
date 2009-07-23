from twisted.internet import defer

queues = {}

def put(name, message):
    queues[name].put(message)

def register(name, queue):
    queues[name] = queue
    

class Queue(defer.DeferredQueue):
    HISTORY_SIZE = 20
    
    def __init__(self, handler=None):
        defer.DeferredQueue.__init__(self)
        self.message_handler = handler
        def f(msg):
            self.history.append(msg)
            if len(self.history) > self.HISTORY_SIZE:
                self.history = self.history[1:]
            if self.message_handler:
                self.message_handler(msg)
            else:
                self.receivedMessage(msg)
            self.get().addCallback(f)
        self.get().addCallback(f)
        self.history = []
        
    
    def receivedMessage(self, message):
        pass