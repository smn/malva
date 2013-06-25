from twisted.trial.unittest import TestCase


class MalvaTestCase(TestCase):

    def test_is_it_delicious(self):
        self.assertTrue('generally yes')
