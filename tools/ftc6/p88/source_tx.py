"""P0088 source-link descriptor extraction and offline logical packing.

9C228 packs little-bit-order fields; 9C34A appends the selected checksum.
Does not emulate GPIO symbols, callback code, scheduler or link state.
"""
START, END = 0x82a7a, 0x8320c


def call_sites(rows, listing):
    """Qualify contiguous PUSH high/PUSH low/JSR operands in a private listing."""
    import re
    instructions = []
    for line in listing.splitlines():
        fields = line.split('\t')
        if len(fields) >= 2 and fields[0].startswith('ram:'):
            instructions.append((int(fields[0][4:], 16), fields[1]))
    index = {int(row['address'], 16): row for row in rows}
    found = {address: set() for address in index}
    for a, b, c in zip(instructions, instructions[1:], instructions[2:]):
        if a[1] != 'PUSH.w #0x8' or b[0] != a[0] + 4 or c[0] != b[0] + 4:
            continue
        low = re.fullmatch(r'PUSH.w #0x([0-9a-f]+)', b[1])
        if low is None or c[1] not in ('JSR.w 0x0009c228', 'JSR.a 0x0009c228'):
            continue
        address = 0x80000 + int(low[1], 16)
        if address in found:
            found[address].add(f'{a[0]:08x}')
    if any(not sites for sites in found.values()):
        raise ValueError('missing qualified source descriptor call site')
    return [dict(row, qualified_call_sites=sorted(found[int(row['address'], 16)])) for row in rows]


def descriptors(image):
    result = []
    at = START
    while at < END:
        base = at
        head = image.at(at, 6)
        if head[0] != 0x10 or head[1] or any(head[3:]):
            raise ValueError('unsupported descriptor header')
        length, checksum = head[2] & 15, head[2] >> 6
        if not 1 <= length <= 6 or checksum not in (0, 1, 2):
            raise ValueError('invalid logical length/checksum')
        at += 6
        fields = []
        while at + 6 <= END:
            raw = image.at(at, 6)
            operand = at
            at += 6
            if raw[0] == 255:
                if any(raw[1:]):
                    raise ValueError('malformed terminator')
                break
            bit, width, kind = raw[0] - 1, raw[1] & 15, (raw[1] >> 4) & 3
            value = int.from_bytes(raw[2:], 'little')
            if bit < 0 or not 1 <= width <= 8 or bit + width > length * 8 or kind == 3 or raw[1] & 0xc0:
                raise ValueError('invalid field')
            if kind == 2 and not 0x80000 <= value < 0x100000:
                raise ValueError('invalid callback')
            fields.append({'operand': f'{operand:05x}', 'bit_offset': bit,
                           'width': width, 'kind': ('constant', 'memory-byte', 'callback')[kind],
                           'source': value})
        else:
            raise ValueError('unterminated descriptor')
        result.append({'address': f'{base:05x}', 'profile': 16,
                       'length': length, 'checksum_kind': checksum,
                       'symbol_encoding': bool(head[2] & 0x20),
                       'bank_flag': bool(head[2] & 0x10), 'fields': fields})
    if at != END or len(result) != 37:
        raise ValueError('descriptor region/count mismatch')
    return result


def pack_logical(descriptor, values):
    """values keys are (kind, source); callbacks must already be evaluated."""
    packed = 0
    for field in descriptor['fields']:
        value = field['source'] if field['kind'] == 'constant' else values[(field['kind'], field['source'])]
        packed |= (int(value) & ((1 << field['width']) - 1)) << field['bit_offset']
    data = bytearray(packed.to_bytes(descriptor['length'], 'little'))
    checksum = descriptor['checksum_kind']
    if checksum:
        data[-1] = (-sum(data[:-1]) - (checksum == 2)) & 255
    return bytes(data)


if __name__ == '__main__':
    import argparse, json
    from pathlib import Path
    from extract import Image
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    parser.add_argument('listing', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = call_sites(descriptors(Image(args.image.read_bytes())), args.listing.read_text())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
