from twisted.internet.serialport import SerialPort
from twisted.internet.defer import DeferredList, Deferred
from twisted.internet import reactor
from twisted.python import log

from txgsm import txgsm

from serial.tools import list_ports
from serial.serialutil import SerialException


class ModemProbe(object):

    def available_ports(self):
        return list_ports.comports()

    def probe_ports(self):
        return DeferredList(
            [self.probe_port(port) for port, _, _ in self.available_ports()])

    def probe_port(self, port):

        def setup_protocol(port):
            try:
                protocol = txgsm.TxGSMProtocol()
                protocol.verbose = True
                SerialPort(protocol, port, reactor)
                return protocol.probe()
            except SerialException, e:
                log.err(e)

        d = Deferred()
        d.addCallback(setup_protocol)
        reactor.callLater(0, d.callback, port)
        return d
