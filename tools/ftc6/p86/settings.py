"""P0086 conservative observer, not a CN105 settings command sender.
Synthetic read/close event coverage is not proof of the internal D handshake.
"""
class Blocked(ValueError): pass

class ReadSession:
    def __init__(self, category=6):
        if category != 6: raise Blocked('Only category6 studied')
        self.state = 'closed'
        self.category = category
        self.snapshot = {}
        self.closure_verified = False

    def event(self, event, category=6, elapsed=0, deadline=10):
        if category != self.category or elapsed >= deadline or event in ('abort', 'bad_reply'):
            self.state = 'closure_required'
            return self.state
        transitions = {
            ('closed','open_intent'): 'await_internal_1002',
            ('await_internal_1002','observed_read_gate_7'): 'read_pending',
            ('read_pending','observed_internal_ack_9'): 'read_ready',
            ('read_ready','captured_settings'): 'read_ready',
            ('read_ready','close_intent'): 'closure_required',
            ('read_pending','close_intent'): 'closure_required',
            ('closure_required','observed_state0_and_prior_control'): 'closed'}
        key = self.state, event
        if key not in transitions: raise Blocked('Unknown/unqualified transition')
        self.state = transitions[key]
        self.closure_verified = event == 'observed_state0_and_prior_control'
        return self.state

    def capture(self, selector, block):
        if self.state != 'read_ready' or selector not in (0x65, 0x79) or len(block) != 16:
            raise Blocked('Wrong state, block or category')
        self.snapshot[selector] = bytes(block)
        return block[10 if selector == 0x65 else 7]

    def proposed_block(self, selector, level):
        """Offline diff only. GET→SET neighboring field correspondence not qualified."""
        if selector not in self.snapshot or level not in (4, 5): raise Blocked('Missing snapshot/level')
        result = bytearray(self.snapshot[selector])
        result[10 if selector == 0x65 else 7] = level
        return bytes(result)

    def apply(self, *args):
        raise Blocked('Apply/persistence/link-loss rollback and whole-block mapping unqualified')
