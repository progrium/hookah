import base64
import cPickle
from collections import deque

class LocalStorage(object):

    MAX_ITEMS = 20

    def __init__(self):
        self._recent = deque()

    def recent(self, n=10):
        return list(self._recent)[0:n]

    def recordLocal(self, ob):
        if len(self._recent) >= self.MAX_ITEMS:
            self._recent.pop()
        self._recent.appendleft(ob)

class MemoryStorage(LocalStorage):

    def __init__(self):
        super(MemoryStorage, self).__init__()
        self._storage = {}
        self._sequence = 0

    def put(self, hookahRequest):
        self._sequence += 1
        self._storage[self._sequence] = hookahRequest
        self.recordLocal(hookahRequest)
        return self._sequence

    def __getitem__(self, key):
        return self._storage[key]

    def __delitem__(self, key):
        del self._storage[key]

class InlineStorage(LocalStorage):

    def __init__(self):
        super(InlineStorage, self).__init__()
        self._recent = deque()

    def put(self, hookaRequest):
        self.recordLocal(hookaRequest)
        return base64.encodestring(cPickle.dumps(hookaRequest))

    def __getitem__(self, key):
        return cPickle.loads(base64.decodestring(key))

    def __delitem__(self, key):
        pass

instance = MemoryStorage()

