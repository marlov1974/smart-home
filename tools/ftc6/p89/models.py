"""P0089 conservative observers; synthetic events are not wire instructions."""
class ServiceObserver:
    def __init__(self,selector):
        self.selector=selector;self.status='idle';self.cache=None;self.pending_polls=0;self.transport_failures=0
    def request(self):
        self.status='pending' if self.cache is None else 'cached-age-unknown'
    def reply(self,record,owned=True):
        if not owned or record['selector']!=self.selector:raise ValueError('unowned result')
        if self.status=='cancelled':raise ValueError('late result after cancellation')
        if record['format']==0:self.pending_polls+=1;self.status='pending'
        elif record['format']==6:self.status='ambiguous'
        else:self.cache=dict(record);self.status='cached-age-unknown'
    def timeout(self):self.transport_failures+=1;self.status='timeout'
    def cancel(self):self.status='cancelled'
    def stale(self):self.status='stale'

class SettingsObserver:
    """Only listed transitions from P86/P88; injected peer evidence explicitly required."""
    def __init__(self,direction,mask):
        if direction not in (0,1) or mask not in (1,2,4,8,16,32,64):raise ValueError('one category mask required')
        self.direction=direction;self.mask=mask;self.state=0;self.applied=False;self.persisted=False
    def event(self,name):
        if name in ('abort','timeout','disconnect','restart'):
            self.state=0;return # never claim rollback or erase applied evidence
        transitions={(0,'open'):1,(1,'peer1002_write'):2,(1,'peer1002_read'):7,
            (2,'stage'):3,(3,'apply'):4,(4,'peer_end'):5,(5,'close'):6,(6,'peer1002_close_write'):12,
            (7,'get'):8,(8,'peer_end'):9,(9,'read_finish'):10,(10,'get'):8,(10,'close'):11,
            (11,'peer1002_close_read'):12,(12,'close_reply'):0}
        if name in ('peer1002_write','peer1002_close_write') and self.direction!=0:raise ValueError('direction')
        if name in ('peer1002_read','peer1002_close_read') and self.direction!=1:raise ValueError('direction')
        key=(self.state,name)
        if key not in transitions:raise ValueError('unknown/unqualified transition')
        self.state=transitions[key]
        if name=='apply':self.applied=True
    def persistence(self,verified):
        if not self.applied:raise ValueError('no applied event')
        self.persisted=bool(verified)

def preserve_category(category,fields,qualified,changes):
    if category!=6:raise ValueError('unqualified category')
    if set(fields)!=set(qualified) or not all(qualified.values()):raise ValueError('unknown affected neighbors/defaults')
    if not set(changes)<=set(fields):raise ValueError('unknown changed field')
    # Even complete caller-supplied flags do not prove the firmware transaction.
    raise ValueError('category6 serializer/session not qualified; no ready packet')
