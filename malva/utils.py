from twisted.internet.serialport import SerialPort
from twisted.internet.defer import DeferredList, Deferred, CancelledError
from twisted.internet import reactor

from txgsm import txgsm

from serial.tools import list_ports


class ModemProbe(object):

    def __init__(self, verbose):
        self.verbose = verbose

    def available_ports(self):
        return list_ports.comports()

    def probe_ports(self, timeout=2):
        dl = [self.probe_port(port, timeout) for port, _, _ in self.available_ports()]
        return DeferredList(dl, consumeErrors=True)

    def probe_port(self, port, timeout):

        def setup_protocol(port):
            protocol = txgsm.TxGSMProtocol()
            protocol.verbose = self.verbose
            SerialPort(protocol, port, reactor)
            return protocol

        def do_probe(modem):
            return modem.probe()

        def get_results(probe_result):
            (_, imsi, _, manufacturer, _) = probe_result
            return (port, imsi, manufacturer)

        d = Deferred()
        d.addCallback(setup_protocol)
        d.addCallback(do_probe)
        d.addCallback(get_results)
        reactor.callLater(0, d.callback, port)
        reactor.callLater(timeout, d.cancel)
        return d
