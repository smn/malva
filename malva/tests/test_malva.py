import os
import pkg_resources

from twisted.trial.unittest import TestCase

from malva.command import MalvaCommand


class MalvaTestCase(TestCase):

    def test_is_it_delicious(self):
        self.assertTrue('generally yes')


class CustardTestCase(TestCase):

    def get_fixture(self, fn):
        fx_path = pkg_resources.resource_filename(
            "malva.tests", os.path.join("fixtures", fn))
        with open(fx_path, 'r') as fp:
            data = fp.read()
        return data

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
