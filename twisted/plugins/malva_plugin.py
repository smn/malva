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


class RunCommand(usage.Options):
    optParams = [
        ['file', 'f', None, 'The JSON file.'],
    ]


class Options(usage.Options):

    optFlags = [
        ["verbose", "v", "Log verbosely"],
    ]

    subCommands = [
        ['probe-modems', None, ProbeModems,
            "Probe serial ports for things that look like a modem."],
        ['run-command', None, RunCommand,
            'Run a Custard command read from a JSON file.'],
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
            'run-command': self.run_command,
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

    def run_command(self, options):

        def find_modems(srvc):
            md = ModemProbe(options['verbose'])
            return mb.get_modems()

        service = OneShotService()
        service.onStart.addCallback(find_modems)
        service.onStart.addCallback(print_results)
        return service

serviceMaker = MalvaServiceMaker()
