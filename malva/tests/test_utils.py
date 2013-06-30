from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, succeed, fail, Deferred
from twisted.test import proto_helpers
from twisted.python import log

from malva.utils import ModemProbe


class MalvaUtilTestCase(TestCase):

    verbose = True

    def setUp(self):
        self.patch(ModemProbe, 'available_ports', lambda _: [
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

    def handle_dialogue(self, modem, transport, dialogue):

        d = Deferred()

        def check_for_input():
            if not transport.value():
                reactor.callLater(0, check_for_input)
                return

            for expected, responses in dialogue:
                command = filter(None, transport.value().split(modem.delimiter))
                self.assertEqual(command, [expected])
                transport.clear()
                for response in responses:
                    modem.dataReceived(response + modem.delimiter)

            d.callback(True)

        check_for_input()
        return d

    @inlineCallbacks
    def test_probing(self):
        # the time-out here is likely going to cause random test failures
        # because of CPU time differences per platform the tests are run on.
        # The fix is to fiddle with mocking the reactor's clock.
        modem_probe = self.modem_probe.probe_ports(timeout=0.1)
        ok_modem, ok_transport = yield self.wait_for_connection('/dev/ok')
        bad_modem, bad_transport = yield self.wait_for_connection('/dev/bad')

        yield self.handle_dialogue(ok_modem, ok_transport, [
            ('ATE0', ['OK']),
            ('AT+CIMI', ['1234567890', 'OK']),
            ('AT+CGMM', ['FOO CORP', 'OK']),
        ])

        yield self.handle_dialogue(bad_modem, bad_transport, [
            ('ATE0', ['FOO']),
        ])

        # yield ok_probe_d
        # yield bad_probe_d
        results = yield modem_probe

        for success, result in results:
            if success:
                port, imsi, manufacturer = result
                self.assertEqual(port, '/dev/ok')
                self.assertEqual(imsi, '1234567890')
                self.assertEqual(manufacturer, 'FOO CORP')
