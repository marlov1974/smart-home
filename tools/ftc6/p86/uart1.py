"""P0086 static FTC6 20.01 codec. No transport; no address migration to 21.00."""
IMAGE_SHA = 'd828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a'
LENGTHS = (1, 2, 4, 8, 16, 32, 64) + (1,) * 9
PROFILES = ('ftc6-20.01-diag-static', 'ftc6-20.01-normal-static')

def profile(name, image_sha=IMAGE_SHA):
    if name not in PROFILES or image_sha != IMAGE_SHA:
        raise ValueError('Unqualified firmware/profile')
    if name != PROFILES[0]:
        raise ValueError('8N2 normal personality cannot use diagnostic session packets')

def checksum(data):
    return bytes(data) + bytes([-sum(data) & 255])

def parser_accepts(address, length):
    return isinstance(address, int) and length in LENGTHS and address >= 0x400 and address + length <= 0xfffff

def effective_addresses(address, length):
    if not parser_accepts(address, length):
        raise ValueError('Parser rejects range')
    return [(address+i) & 0xffff for i in range(length)]

def memory(address, length):
    if not parser_accepts(address, length) or address + length > 0x5000:
        raise ValueError('Only conservative candidate RAM 0400–4fff; alias/MMIO/flash blocked')
    return checksum(bytes([LENGTHS.index(length)*16+1]) + address.to_bytes(3, 'little'))

def request(operation, address=None, length=None):
    if operation == 'open': return checksum(bytes(4))
    if operation == 'close': return checksum(bytes([15, 0, 0, 0]))
    if operation == 'log': return checksum(bytes([2, 240, 0, 0]))
    if operation == 'read': return memory(address, length)
    raise ValueError('Unsupported operation')

def response(data, operation, length=None):
    if not 3 <= len(data) <= 77 or data[1] != len(data) or sum(data) & 255:
        raise ValueError('Truncated, oversized or corrupt response')
    if data[0] == 15:
        raise ValueError('Device error response')
    if operation == 'open' and data == bytes.fromhex('0003fd'): return b''
    if operation == 'read' and length in LENGTHS and data[0] == 1 and len(data) == length+3: return data[2:-1]
    if operation == 'log' and len(data) == 77 and data[:4] == bytes.fromhex('024df002'): return data[4:-1]
    raise ValueError('Unexpected response/operation; close is silent, not acknowledged')

def normal52(address):
    """Address semantics only, not an executable normal-protocol packet."""
    if not 0 <= address <= 0x3fff: raise ValueError('14-bit address required')
    if address < 0x100: return {'kind': 'near', 'address': 0xee4+address}
    if address < 0x200: return {'kind': 'near', 'address': 0xae4+address-0x100}
    if address < 0x400: return {'kind': 'table_lookup', 'table': 0x806a4, 'key': address}
    return {'kind': 'near', 'address': address}

def logs(data):
    raw = response(data, 'log')
    records, packets, pending = [], [], None
    for offset in range(0, 72, 12):
        record = raw[offset:offset+12]
        tag = record[0]
        source = {6:'CN105', 3:'D', 4:'D'}.get(tag & 31, 'UNKNOWN')
        item = {'slot': offset//12, 'raw_hex': record.hex(), 'tag': tag,
                'source': source, 'direction': 'TX' if tag & 64 else 'RX',
                'continuation': bool(tag & 128), 'loss': bool(tag & 32),
                'all_zero_padding_candidate': not any(record), 'timestamp': None}
        records.append(item)
        if not any(record) or tag & 32:
            pending = None
            continue
        if tag & 128:
            if pending and pending[0] == (tag & 127) and source == 'CN105':
                packets.append({'source': source, 'observed_hex': (pending[1]+record[1:11]).hex(),
                                'observed_bytes': 21, 'checksum_captured': False})
            else:
                item['orphan_continuation'] = True
            pending = None
        else:
            pending = (tag, record[1:])
    return {'records': records, 'packets': packets, 'drains_buffer': True,
            'timestamps_available': False, 'loss_count': None}
