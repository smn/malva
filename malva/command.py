import json

from twisted.python import log


class CommandException(Exception):
    pass


class MalvaCommand(object):

    CALLBACK_MODES = ['email']
    COMMAND_TYPES = ['USSD']

    def __init__(self, name, description, slug=None, callback_mode=None,
                 callback_value=None, type=None, tx_mccmnc=None,
                 continue_on_fail=None, steps=[]):
        self.name = name
        self.description = description
        self.slug = slug

        if callback_mode not in self.CALLBACK_MODES:
            raise CommandException('Unknown callback_mode: %s' % (
                                   callback_mode,))
        self.callback_mode = callback_mode
        self.callback_value = callback_value

        if type not in self.COMMAND_TYPES:
            raise CommandException('Unknown type: %s' % (
                                   type,))
        self.command_type = type

        self.tx_mccmnc = tx_mccmnc
        self.continue_on_fail = continue_on_fail
        if self.continue_on_fail:
            log.msg('Warning! continue_on_fail set to True.')
        self.steps = steps

    @classmethod
    def parse(cls, json_data):
        data = json.loads(json_data)
        return cls(**data)
