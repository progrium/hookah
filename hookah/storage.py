from collections import deque

class MemoryStorage(object):

    def __init__(self):
        self._recent = deque()
        self._storage = {}
        self._sequence = 0

    def put(self, hookahRequest):
        self._sequence += 1
        self._storage[self._sequence] = hookahRequest
        self._recent.appendleft(hookahRequest)
        return self._sequence

    def recent(self, n=10):
        return list(self._recent)[0:n]

    def __getitem__(self, key):
        return self._storage[key]

    def __delitem__(self, key):
        del self._storage[key]

instance = MemoryStorage()

