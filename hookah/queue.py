from twisted.internet import defer, task

import storage

class Consumer(object):

    def __call__(self, key):
        request = storage.instance[key]
        # TODO:  Work
        return defer.succeed("yay")

class Queue(object):

    def submit(self, key):
        """Submit a job by work queue key."""
        raise NotImplementedError

    def finish(self, key):
        """Mark a job as completed."""
        raise NotImplementedError

    def retry(self, key):
        """Retry a job."""
        raise NotImplementedError

    def startConsumers(self, n=5):
        """Start consumers working on the queue."""
        raise NotImplementedError

    def shutDown(self):
        """Shut down the queue."""
        raise NotImplementedError

    @defer.inlineCallbacks
    def doTask(self, c):
        key = yield self.q.get()
        # XXX:  Indicate success/requeue/whatever
        try:
            worked = yield c(key)
            self.finish(key)
        except:
            self.retry(key)

class MemoryQueue(Queue):

    def __init__(self, consumer=Consumer):
        self.q = defer.DeferredQueue()
        self.keepGoing = True
        self.consumer = consumer
        self.cooperator = task.Cooperator()

    def submit(self, key):
        self.q.put(key)

    def finish(self, key):
        del storage.instance[key]

    retry = submit

    def shutDown(self):
        self.keepGoing = False

    def startConsumers(self, n=5):
        def f(c):
            while self.keepGoing:
                yield self.doTask(c)

        for i in range(n):
            self.cooperator.coiterate(f(self.consumer()))

instance = MemoryQueue()

