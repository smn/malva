import random
import json

from twisted.internet.defer import Deferred, CancelledError
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from malva.command import MalvaCommand, CommandRunner


class CustardResource(Resource):

    isLeaf = True

    def __init__(self, modems, verbose=False):
        self.modems = modems
        self.verbose = verbose

    def find_suitable_modem(self, tx_mccmnc):
        # TODO: fix this
        return random.choice(self.modems)

    def render_POST(self, request):
        post_data = request.content.read()
        mc = MalvaCommand.parse(post_data)

        d = Deferred()
        d.addCallback(self.handle_command, mc)
        reactor.callLater(0, d.callback, request)
        return NOT_DONE_YET

    def handle_command(self, request, malva_command):
        modem = self.find_suitable_modem(malva_command.tx_mccmnc)

        def eb(failure):
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            if failure.check(CancelledError):
                request.write("Modem Timeout")
            else:
                request.write(failure.getErrorMessage())
            request.finish()

        def cb(history):
            request.write(json.dumps(history))
            request.finish()

        d = CommandRunner().run(modem, malva_command)
        d.addCallback(cb)
        d.addErrback(eb)
        return d
