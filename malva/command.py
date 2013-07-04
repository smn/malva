import json

from twisted.python import log
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from txgsm.utils import quote


class CommandException(Exception):
    pass


class MalvaAction(object):

    def __init__(self, value):
        self.value = value

    def run(self, modem, history):
        """
        To be implemented by the subclass

        :param modem txgsm.TxGSMProtocol:
            The modem we're connected to.
        :param history dict:
            The full history commands sent & received from the modem.
            {'sent': [], 'received': []}

        """
        raise NotImplementedError


class DialAction(MalvaAction):

    def run(self, modem, history):
        return modem.dial_ussd_code(self.value)


class ExpectAction(MalvaAction):

    def run(self, modem, history):
        pass


class SleepAction(MalvaAction):

    def run(self, modem, history):
        d = Deferred
        reactor.callLater(float(self.value), d.callback, modem, history)
        return d


class ReplyAction(MalvaAction):
    def run(self, modem, history):
        return modem.send_command('AT+CUSD=1,"%s",15' % (quote(self.value),),
                                  expect="+CUSD")


class CancelAction(MalvaAction):
    def run(self, modem, history):
        return modem.loseConnection()


class MalvaCommand(object):

    CALLBACK_MODES = ['email']
    COMMAND_TYPES = ['USSD']
    ACTIONS = {
        'dial': DialAction,
        'expect': ExpectAction,
        'sleep': SleepAction,
        'reply': ReplyAction,
        'cancel': CancelAction,
    }

    def __init__(self, name, description, slug=None, callback_mode=None,
                 callback_value=None, type=None, tx_mccmnc=None,
                 continue_on_fail=None, steps=[]):

        if callback_mode not in self.CALLBACK_MODES:
            raise CommandException('Unknown callback_mode: %s' % (
                                   callback_mode,))

        if type not in self.COMMAND_TYPES:
            raise CommandException('Unknown type: %s' % (
                                   type,))

        if continue_on_fail:
            log.msg('Warning! continue_on_fail set. Ignoring.')

        self.name = name
        self.description = description
        self.slug = slug
        self.callback_mode = callback_mode
        self.callback_value = callback_value
        self.command_type = type
        self.tx_mccmnc = tx_mccmnc
        self.continue_on_fail = False
        self.steps = [self.make_step(step) for step in steps]

    def make_step(self, step):
        name = step['action']
        value = step.get('value', None)
        if name not in self.ACTIONS:
            raise CommandException('Unsupported action: %s' % (name,))
        return self.ACTIONS[name](value)

    @classmethod
    def parse(cls, json_data):
        data = json.loads(json_data)
        return cls(**data)
