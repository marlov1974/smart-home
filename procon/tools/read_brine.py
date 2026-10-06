"""P0071 operator-run, read-only Modbus evidence capture. No device writes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.request import urlopen


def request_block(host, address, quantity):
    stamp = datetime.now(timezone.utc).isoformat()
    url = f'http://{host}/rpc/MbRtuClient.ReadInputRegisters?id=100&sid=1&addr={address}&qty={quantity}'
    with urlopen(url, timeout=8) as response:
        result = json.load(response)
    values = result.get('values')
    if not isinstance(values, list) or len(values) != quantity or any(type(v) is not int or not 0 <= v <= 65535 for v in values):
        raise ValueError(f'Invalid read response: {result}')
    return {'timestamp': stamp, 'address': address, 'quantity': quantity, 'values': values}


def decode_samples(before, words, after):
    result = []
    for i, code in enumerate((27, 28)):
        b, a = before[8*i:8*i+8], after[8*i:8*i+8]
        coherent = b[5] == a[5] and b[6] == a[6]
        payload = b''.join(v.to_bytes(2, 'little') for v in words[8*i:8*i+8])
        known = coherent and a[6] == 1
        valid = known and b[2] == a[2] == 1
        frame = bytes.fromhex('fc 62 02 7a 10') + payload
        frame += bytes([(0xfc - sum(frame)) & 255])
        result.append({'service': code, 'coherent': coherent, 'valid_completed_sample': valid,
                       'completed_ever': bool(a[6]), 'age_seconds': a[3],
                       'raw_u16': a[0] if known else None,
                       'experimental_signed_degree_candidate': int.from_bytes(payload[4:6], 'little', signed=True) if valid else None,
                       'payload_hex': payload.hex(' ') if known else None,
                       'reconstructed_frame_hex': frame.hex(' ') if known else None,
                       'hardware_correlated': False})
    return result


def capture(host):
    blocks = [request_block(host, a, n) for a, n in [(0, 16), (16, 16), (32, 16), (44, 8), (52, 16), (16, 16)]]
    if blocks[0]['values'][:2] != [888, 71]:
        raise ValueError('Expected P0071 marker888/build71; do not interpret another register map')
    return {'read_only': True, 'blocks': blocks,
            'samples': decode_samples(blocks[1]['values'], blocks[4]['values'], blocks[5]['values']),
            'note': 'Frames reconstructed from retained Modbus payloads; not a direct CN105 wire capture. Temperature candidates require display correlation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='192.168.86.85')
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--interval', type=float, default=1.0)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.samples <= 3600 or not 0.2 <= args.interval <= 60:
        parser.error('samples must be1–3600 and interval0.2–60 seconds')
    with args.output.open('x') as output:
        for index in range(args.samples):
            start = time.monotonic()
            try:
                record = capture(args.host)
            except Exception as error:
                record = {'timestamp': datetime.now(timezone.utc).isoformat(), 'read_only': True, 'error': str(error)}
            output.write(json.dumps(record) + '\n'); output.flush()
            print(json.dumps(record), flush=True)
            if index+1 < args.samples:
                time.sleep(max(0, args.interval-(time.monotonic()-start)))


if __name__ == '__main__':
    main()
