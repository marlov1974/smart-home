"""P0089 offline fixture framing/decoding; no transport and no live SET planner."""
def frame(kind,payload):
    if not isinstance(kind,int) or not 0<=kind<=255:raise ValueError('type')
    payload=bytes(payload)
    if len(payload)>16:raise ValueError('payload exceeds reviewed capacity')
    data=bytes([0xfc,kind,2,0x7a,len(payload)])+payload
    return data+bytes([(-sum(data[1:]))&255])

def parse(data,expected_type,expected_opcode=None,length=16):
    data=bytes(data)
    if not 6<=len(data)<=22 or data[0]!=0xfc or data[2:4]!=b'\x02\x7a':raise ValueError('frame/header')
    if data[1]!=expected_type or data[4]!=length or len(data)!=length+6:raise ValueError('type/length')
    if sum(data[1:])&255:raise ValueError('checksum')
    payload=data[5:-1]
    if expected_opcode is not None and (not payload or payload[0]!=expected_opcode):raise ValueError('opcode')
    return payload

def a3(data,selector):
    p=parse(data,0x62,0xa3)
    if int.from_bytes(p[1:3],'big')!=selector:raise ValueError('selector ownership')
    fmt=p[3]
    if fmt not in (0,1,2,3,4,6,7):raise ValueError('unqualified format')
    return dict(selector=selector,format=fmt,raw_le=int.from_bytes(p[4:6],'little'),raw_bytes=list(p[4:6]),
        kind='pending' if fmt==0 else 'ambiguous' if fmt==6 else 'typed-result',
        scale='unqualified per selector',freshness='unknown acquisition age')

def plan_read(selector):
    if selector in (340,532) or 520<=selector<=531:raise ValueError('effectful/maintenance selector excluded')
    # Only selectors already used by current Procon; this is a fixture, no new allowlist.
    if selector not in (18,19,27,28):raise ValueError('unqualified read selector')
    p=bytearray(16);p[0]=0xa3;p[1:3]=selector.to_bytes(2,'big')
    return dict(offline_only=True,physical_ready=False,frame_hex=frame(0x42,p).hex())
