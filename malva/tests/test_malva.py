import os
import pkg_resources

from twisted.internet.defer import inlineCallbacks

from txgsm.tests.base import TxGSMBaseTestCase

from malva.command import MalvaCommand, CommandRunner


class MalvaBaseTestCase(TxGSMBaseTestCase):

    def get_fixture(self, fn):
        fx_path = pkg_resources.resource_filename(
            "malva.tests", os.path.join("fixtures", fn))
        with open(fx_path, 'r') as fp:
            data = fp.read()
        return data


class MalvaTestCase(MalvaBaseTestCase):

    timeout = 1

    @inlineCallbacks
    def test_eat_custard(self):
        command = MalvaCommand.parse(self.get_fixture('fnb_script.json'))
        runner = CommandRunner()
        self.modem.verbose = True
        d = runner.run(self.modem, command)
        # dial in
        yield self.assertExchange(
            ['AT+CUSD=1,"*120*321#",15'],
            ['OK', '+CUSD: 1,"Something FNB bla bla FRB!",255'])
        # respond with option 1
        yield self.assertExchange(
            ['AT+CUSD=1,"1",15'],
            ['OK', '+CUSD: 1,"Something with Cellphone number",255'])
        # cancel the session
        yield self.assertExchange(['AT+CUSD=2'], ['OK'])
        log = yield d
        self.assertEqual(log, [
            {
                'command': ['AT+CUSD=1,"*120*321#",15'],
                'expect': '+CUSD',
                'response': [
                    'OK',
                    '+CUSD: 1,"Something FNB bla bla FRB!",255'
                ]
            }, {
                'command': ['AT+CUSD=1,"1",15'],
                'expect': '+CUSD',
                'response': [
                    'OK',
                    '+CUSD: 1,"Something with Cellphone number",255'
                ]
            }, {
                'command': ['AT+CUSD=2'],
                'expect': 'OK',
                'response': ['OK']
            }
        ])


class CustardTestCase(MalvaBaseTestCase):

    def test_parse_json(self):
        mc = MalvaCommand.parse(self.get_fixture('fnb_script.json'))
        self.assertEqual(mc.name, 'FNB Test Up')
        self.assertEqual(mc.description,
                         'Test to see if the FNB USSD service is online')
        self.assertEqual(mc.slug, 'FNB-USSD-1')
        self.assertEqual(mc.callback_mode, 'email')
        self.assertEqual(mc.callback_value, 'your@email.here')
        self.assertEqual(mc.command_type, 'USSD')
        self.assertEqual(mc.tx_mccmnc, '65501')
        # I'm not sure what to do when `continue_on_fail` is set so I'm
        # ignoring it for now.
        self.assertEqual(mc.continue_on_fail, False)
        self.assertEqual(len(mc.steps), 6)
