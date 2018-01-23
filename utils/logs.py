from inspect import getframeinfo, stack
from web3.utils.threads import (
    Timeout,
)


class LogHandler:
    def __init__(self, web3, address, abi):
        self.web3 = web3
        self.address = address
        self.abi = abi
        self.event_waiting = {}
        self.event_filters = {}
        self.event_verified = []
        self.event_unkown = []

    def add(self, txn_hash, event_name, callback=None):
        caller = getframeinfo(stack()[1][0])
        message = "%s:%d" % (caller.filename, caller.lineno)

        if not event_name in self.event_waiting:
            self.event_waiting[event_name] = {}
            self.event_filters[event_name] = LogFilter(
                self.web3,
                self.abi,
                self.address,
                event_name,
                callback=self.handle_log
            )

        self.event_waiting[event_name][txn_hash] = [message, callback]

    def check(self, timeout=5):
        for event in list(self.event_filters.keys()):
            self.event_filters[event].init()

        self.wait(timeout)

    def handle_log(self, event):
        txn_hash = event['transactionHash']
        event_name = event['event']

        if event_name in self.event_waiting:
            if txn_hash in self.event_waiting[event_name]:
                self.event_verified.append(event)
                event_entry = self.event_waiting[event_name].pop(txn_hash, None)

                # Call callback function with event and remove
                if event_entry[1]:
                    event_entry[1](event)

            else:
                self.event_unkown.append(event)
            if not len(list(self.event_waiting[event_name].keys())):
                self.event_waiting.pop(event_name, None)
                self.event_filters.pop(event_name, None)

    def wait(self, seconds):
        try:
            with Timeout(seconds) as timeout:
                while len(list(self.event_waiting.keys())):
                    timeout.sleep(2)
        except:
            message = 'NO EVENTS WERE TRIGGERED FOR: ' + str(self.event_waiting)
            if len(self.event_unkown) > 0:
                message += '\n UNKOWN EVENTS: ' + str(self.event_unkown)

            # FIXME Events triggered in another transaction
            # don't have the transactionHash we are looking for here
            # so we just check if the number of unknown events we find
            # is the same as the found events
            waiting_events = 0
            for ev in list(self.event_waiting.keys()):
                waiting_events += len(list(self.event_waiting[ev].keys()))

            if waiting_events == len(self.event_unkown):
                print('----------------------------------')
                print(message)
                print('----------------------------------')
            else:
                raise Exception(message + ' waiting_events ' + str(waiting_events), ' len(self.event_unkown) ' + str(len(self.event_unkown)))
