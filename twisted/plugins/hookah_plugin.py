from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web.server import Site

from hookah import HookahResource


class Options(usage.Options):
    optParameters = [["port", "p", 8080, "The port number to listen on."]]


class HookahMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "hookah"
    description = "Yeah. Hookah."
    options = Options

    def makeService(self, options):
        """
        Construct a TCPServer from a factory defined in myproject.
        """
        return internet.TCPServer(int(options["port"]), Site(HookahResource()))

serviceMaker = HookahMaker()
