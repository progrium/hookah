from twisted.trial import unittest

from hookah import storage

class BaseStorageTest(object):

    storageFactory = None
    deletionMeaningful = True

    def setUp(self):
        self.s = self.storageFactory()

        self.oneKey = self.s.put("one")
        self.twoKey = self.s.put("two")

    def testGet(self):
        self.assertEquals("one", self.s[self.oneKey])
        self.assertEquals("two", self.s[self.twoKey])

    def testDelete(self):
        self.assertEquals("one", self.s[self.oneKey])
        self.assertEquals("two", self.s[self.twoKey])

        del self.s[self.oneKey]
        self.assertEquals("two", self.s[self.twoKey])

        try:
            v = self.s[self.oneKey]
            if self.deletionMeaningful:
                self.fail("Expected failure, got " + v)
        except KeyError:
            pass

    def testRecent(self):
        self.assertEquals(['two', 'one'], self.s.recent())
        self.assertEquals(['two'], self.s.recent(1))

class MemoryStorageTest(BaseStorageTest, unittest.TestCase):

    storageFactory = storage.MemoryStorage

class InlineStorageTest(BaseStorageTest, unittest.TestCase):

    storageFactory = storage.InlineStorage
    deletionMeaningful = False
