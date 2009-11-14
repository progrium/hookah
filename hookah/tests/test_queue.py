from hookah import queue, storage
from time import sleep
from twisted.trial import unittest
from twisted.internet import defer

class MockConsumer(object):

    def __init__(self, i=1):
        self.d = defer.Deferred()
        self.i = i

    def __call__(self, key):
        self.i -= 1
        if self.i == 0:
            self.d.callback(key)
        return defer.succeed("yay")

class TestQueue(unittest.TestCase):

    def setUp(self):
        self.c = MockConsumer()
        self.q = queue.MemoryQueue(consumer=lambda: self.c)
        self.q.startConsumers(1)

    def testOneJob(self):
        k = storage.instance.put('Test Thing')
        self.q.submit(k)

        print "Checking..."
        self.c.d.addBoth(lambda x: self.q.shutDown())
        return self.c.d

    def verifyMissing(self, *keys):
        for k in keys:
            try:
                self.storage.instance[k]
                self.fail("Found unexpected key", k)
            except KeyError:
                pass

    def testTwoJobs(self):
        k1 = storage.instance.put('Test Thing 1')
        self.q.submit(k1)
        k2 = storage.instance.put('Test Thing 2')
        self.q.submit(k2)


        self.c.d.addCallback(lambda x: self.verifyMissing(k1, k2))
        self.c.d.addBoth(lambda x: self.q.shutDown())
        return self.c.d
