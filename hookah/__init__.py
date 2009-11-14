import yaml
from twisted.internet import reactor
from twisted.web.server import Site
from hookah.web import HookahResource
from hookah import queue

config = {}

def configure(config_file):
    config = yaml.load(open(config_file, 'r').read())
    queue.instance.startConsumers(1)
    reactor.listenTCP(config['port'], Site(HookahResource.setup()))


class HookahRequest(object):
    def __init__(self, url, headers, body):
        self.url = url
        self.headers = headers
        self.body = body
