import sys
from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker, Service
from twisted.web import server
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import serverFromString

from malva.utils import ModemProbe
from malva.web import CustardResource


class ProbeModems(usage.Options):
    pass


class CustardNode(usage.Options):
    optParameters = [
        ['endpoint', None, 'tcp:port=8000:interface=localhost',
            'The endpoint to listen on.'],
    ]


class Options(usage.Options):

    optFlags = [
        ["verbose", "v", "Log verbosely"],
    ]

    subCommands = [
        ['probe-modems', None, ProbeModems,
            "Probe serial ports for things that look like a modem."],
        ['custard-node', None, CustardNode,
            'Run as a Custard node.'],
    ]


class OneShotService(Service):
    def __init__(self):
        self.onStart = Deferred()

    def startService(self):
        self.onStart.callback(self)


class MalvaServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "malva"
    description = "A Custard node implementation."
    options = Options

    def makeService(self, options):
        dispatch = {
            'probe-modems': self.probe_modems,
            'custard-node': self.custard_node,
        }

        callback = dispatch.get(options.subCommand)
        if callback:
            return callback(options)
        else:
            sys.exit(str(options))

    def probe_modems(self, options):

        def do_probe(srvc):
            mb = ModemProbe(options['verbose'])
            return mb.probe_ports()

        def list_results(results):
            for success, result in results:
                if success:
                    log.msg(
                        "Port: %s, IMSI: %s, Manufacturer info: %s" % result)
            reactor.stop()

        service = OneShotService()
        service.onStart.addCallback(do_probe)
        service.onStart.addCallback(list_results)
        return service

    def custard_node(self, options):

        def find_modems(srvc):
            mb = ModemProbe(options['verbose'])
            d = mb.get_modems()
            d.addCallback(
                lambda results: [modem for (success, modem) in results
                                 if success])
            return d

        def start_node(modems):
            log.msg('Found %s modems.' % (len(modems,)))
            endpoint = serverFromString(reactor, options.subOptions['endpoint'])
            factory = server.Site(
                CustardResource(modems, verbose=options['verbose']))
            endpoint.listen(factory)

        service = OneShotService()
        service.onStart.addCallback(find_modems)
        service.onStart.addCallback(start_node)
        return service

serviceMaker = MalvaServiceMaker()
