# -*- test-case-name: malva.tests.test_utils -*-

from twisted.internet.serialport import SerialPort
from twisted.internet.defer import DeferredList, Deferred
from twisted.internet import reactor

from txgsm import txgsm

from serial.tools import list_ports


class ModemProbe(object):

    protocol = txgsm.TxGSMProtocol
    serial_port_class = SerialPort

    def __init__(self, verbose):
        self.verbose = verbose

    def available_ports(self):
        return list_ports.comports()

    def probe_ports(self, timeout=2):
        dl = [self.probe_port(port, timeout)
              for port, _, _ in self.available_ports()]
        return DeferredList(dl, consumeErrors=True)

    def setup_protocol(self, port):
        # separate function for easier stubbing in a test
        proto = self.protocol()
        proto.verbose = self.verbose
        self.serial_port_class(proto, port, reactor)
        return proto

    def probe_port(self, port, timeout):

        def get_results(probe_result):
            (_, imsi, _, manufacturer, _) = probe_result
            return (port, imsi, manufacturer)

        d = Deferred()
        d.addCallback(self.setup_protocol)
        d.addCallback(lambda modem: modem.probe())
        d.addCallback(get_results)
        reactor.callLater(0, d.callback, port)
        reactor.callLater(timeout, d.cancel)
        return d
