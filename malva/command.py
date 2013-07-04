import json

from twisted.python import log
from twisted.internet.defer import Deferred, succeed
from twisted.internet import reactor

from txgsm.utils import quote


class CommandException(Exception):
    pass


class MalvaAction(object):

    ENCODING = 'utf-8'

    def __init__(self, value):
        if isinstance(value, unicode):
            value = value.encode(self.ENCODING)
        self.value = value

    def run(self, modem, history):
        """
        To be implemented by the subclass

        :param modem txgsm.TxGSMProtocol:
            The modem we're connected to.
        :param history list:
            The full history of responses received from the modem
        """
        raise NotImplementedError


class DialAction(MalvaAction):

    def run(self, modem, history):
        return modem.dial_ussd_code(self.value)


class ExpectAction(MalvaAction):

    def is_ussd_resp(self, cmd):
        return cmd.startswith('+CUSD:')

    def run(self, modem, history):
        cmd_history = history[-1]['response']
        ussd_responses = [cmd for cmd in cmd_history
                          if self.is_ussd_resp(cmd)]
        if not ussd_responses:
            raise CommandException('No USSD responses found in history.')
        last_resp = ussd_responses[-1]

        if self.value in last_resp:
            return succeed(None)

        return fail(CommandException('Did not find %s in %s' % (
            self.value, self.history)))


class SleepAction(MalvaAction):

    def run(self, modem, history):
        d = Deferred()
        reactor.callLater(float(self.value), d.callback, None)
        return d


class ReplyAction(MalvaAction):
    def run(self, modem, history):
        return modem.send_command('AT+CUSD=1,"%s",15' % (quote(self.value),),
                                  expect="+CUSD")


class CancelAction(MalvaAction):
    def run(self, modem, history):
        return modem.send_command('AT+CUSD=2')


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
