import sys
from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker, Service
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from malva.utils import ModemProbe


class ProbeModems(usage.Options):
    pass


class Options(usage.Options):

    optFlags = [
        ["verbose", "v", "Log verbosely"],
    ]

    subCommands = [
        ['probe-modems', None, ProbeModems,
            "Probe serial ports for things that look like a modem."],
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
        }

        callback = dispatch.get(options.subCommand)
        if callback:
            return callback(options)
        else:
            sys.exit(str(options))

    def probe_modems(self, options):

        def do_probe(srvc):
            mb = ModemProbe()
            return mb.probe_ports()

        def list_results(results):
            for status, result in results:
                print status, result

        service = OneShotService()
        service.onStart.addCallback(do_probe)
        service.onStart.addCallback(list_results)
        return service

serviceMaker = MalvaServiceMaker()
