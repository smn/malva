from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, succeed, Deferred
from twisted.test import proto_helpers

from malva.utils import ModemProbe

from txgsm.tests.base import TxGSMBaseTestCase

from serial.tools import list_ports


class MalvaUtilTestCase(TxGSMBaseTestCase):

    timeout = 1
    verbose = True

    def setUp(self):
        super(MalvaUtilTestCase, self).setUp()
        self.patch(list_ports, 'comports', lambda: [
            # device, description, hardware-id
            ('/dev/ok', 'OK Modem', 'HARWARE_ID'),
            ('/dev/bad', 'Bad Modem', 'HARWARE_ID'),
        ])
        self.patch(ModemProbe, 'serial_port_class', self.mock_connection)
        self.modem_probe = ModemProbe(self.verbose)
        self.transports = {}

    @property
    def mock_connection(self):

        class MockSerial(object):
            def __init__(_, protocol, port, reactor):
                transport = proto_helpers.StringTransport()
                self.transports[port] = (protocol, transport)
                protocol.makeConnection(transport)

        return MockSerial

    def wait_for_connection(self, name):
        d = Deferred()

        def checker():
            if name in self.transports:
                d.callback(self.transports[name])
                return
            reactor.callLater(0, checker)

        checker()
        return d

    @inlineCallbacks
    def test_probing(self):
        # the time-out here is likely going to cause random test failures
        # because of CPU time differences per platform the tests are run on.
        # The fix is to fiddle with mocking the reactor's clock.
        modem_probe = self.modem_probe.probe_ports(timeout=0.01)
        ok_modem, ok_transport = yield self.wait_for_connection('/dev/ok')
        bad_modem, bad_transport = yield self.wait_for_connection('/dev/bad')

        yield self.assertExchange(['ATE0'], ['OK'],
                                  modem=ok_modem, transport=ok_transport)
        yield self.assertExchange(['AT+CIMI'], ['1234567890', 'OK'],
                                  modem=ok_modem, transport=ok_transport)
        yield self.assertExchange(['AT+CGMM'], ['FOO CORP', 'OK'],
                                  modem=ok_modem, transport=ok_transport)

        yield self.assertExchange(['ATE0'], ['FOO'],
                                  modem=bad_modem, transport=bad_transport)

        # yield ok_probe_d
        # yield bad_probe_d
        results = yield modem_probe

        for success, result in results:
            if success:
                port, imsi, manufacturer = result
                self.assertEqual(port, '/dev/ok')
                self.assertEqual(imsi, '1234567890')
                self.assertEqual(manufacturer, 'FOO CORP')
