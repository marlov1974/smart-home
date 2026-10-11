"""Offline UART6 codecs derived from FTC20.01; no sender or transport."""
def frame(data):
    data=bytes(data)
    if len(data)<6 or len(data)>22 or data[0]!=0xfc or data[2:4]!=b'\x04\x03':
        raise ValueError('Not a UART6 FC/04/03 frame')
    if data[4]+6!=len(data) or sum(data[1:])&255:
        raise ValueError('Invalid declared length/checksum')
    return data[1],data[5:-1]

def room_value(raw):
    if not isinstance(raw,int) or not 0<=raw<=255:raise ValueError('Not a byte')
    return None if raw==255 else (min(208,max(128,raw))-128)*50

def target_value(raw):
    if not isinstance(raw,int) or not 0<=raw<=255:raise ValueError('Not a byte')
    return (raw-128)*50 if 128<=raw<=248 else None

def decode(data):
    command,payload=frame(data)
    if command not in range(0x48,0x4d) and command!=0x5a:raise ValueError('Uninventoried opcode')
    expected=command-0x21 if command!=0x5a else 0xca
    if not payload or payload[0]!=expected:raise ValueError('Wrong UART6 selector')
    result={'command':command,'payload_hex':payload.hex(),'physical_validation':False}
    if command in range(0x48,0x4c):
        offset=2 if command==0x49 else 1
        if len(payload)<offset+8:raise ValueError('Truncated room channels')
        result['room_centi_c']=[room_value(x) for x in payload[offset:offset+8]]
        result['invalid_channels']=[i for i,x in enumerate(payload[offset:offset+8]) if x==255]
    if command==0x49:
        if len(payload)<15:raise ValueError('Truncated target route')
        result.update(target_centi_c=target_value(payload[1]),mode_raw=payload[10],zone_raw=payload[14])
    return result
