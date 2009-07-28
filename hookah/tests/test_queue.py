from hookah import queue
from time import sleep
from twisted.trial import unittest
from twisted.internet import defer

class TestQueue(unittest.TestCase):

    def setUp(self):
        self.queue = queue.Queue()

    def test_history_size(self):
        self.assert_(len(self.queue.history) == 0)
        max_size = self.queue.HISTORY_SIZE
        for x in range(max_size + 2):
            self.queue.put(x)
        self.assert_(len(self.queue.history) == max_size)

    def test_handler(self):
        d = defer.Deferred()
        def test(msg):
            self.assert_(msg == 'test')
        d.addCallback(test)
        def handler(msg):
            d.callback(msg)
        self.queue = queue.Queue(handler)
        self.queue.put('test')
        return d

    def test_history(self):
        for x in ['a', 'b', 'c']:
            self.queue.put(x)
        self.assert_('a' in self.queue.history)

if __name__ == '__main__':
    unittest.main()