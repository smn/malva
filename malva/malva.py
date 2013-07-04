from twisted.internet.defer import inlineCallbacks, returnValue


class CommandRunner(object):

    @inlineCallbacks
    def run(self, modem, command):
        history = []
        for step in command.steps:
            res = yield step.run(modem, history)
            if res:
                history.extend([res])
        returnValue(history)
