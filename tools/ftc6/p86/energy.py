"""P0086: offline energy qualification, NOT a calibrated energy meter."""
from datetime import datetime

PAIRS = {520: 'consumed_dhw', 522: 'consumed_heating', 524: 'consumed_cooling',
         526: 'delivered_dhw', 528: 'delivered_heating', 530: 'delivered_cooling'}
CODES = frozenset(range(520, 532))

def bcd(word):
    if not isinstance(word, int) or not 0 <= word <= 65535:
        raise ValueError('BCD word outside uint16')
    digits = [(word >> n) & 15 for n in (12, 8, 4, 0)]
    if any(n > 9 for n in digits):
        raise ValueError('Invalid BCD nibble')
    return sum(d * 10 ** (3-i) for i, d in enumerate(digits))

def api600(selector, correlation=1):
    """Candidate envelope only; production allowlist is deliberately unchanged."""
    if selector not in CODES or not 1 <= correlation <= 65535:
        raise ValueError('Unqualified selector/correlation')
    return [0x81d1, 1, 0xfd, correlation, 2, selector, 0, 0]

def pair(selector, high, low, repeated_low=None):
    if selector not in PAIRS:
        raise ValueError('Expected even energy selector')
    h, l = bcd(high), bcd(low)
    if low & 255:
        raise ValueError('Odd handler must zero low byte')
    if repeated_low is not None:
        bcd(repeated_low)
        if repeated_low & 255:
            raise ValueError('Invalid repeated low portion')
    return dict(bucket=PAIRS[selector], raw_units=h*1000+l//10,
                resolution_raw_units=10, unit='UNCALIBRATED',
                censored=(h == 9999 and l == 9900),
                consistency='changed' if repeated_low is not None and repeated_low != low else 'unverified',
                atomic=False)

def delta(previous, current):
    if previous['bucket'] != current['bucket']:
        raise ValueError('Unmatched buckets')
    if previous['censored'] or current['censored']:
        return {'delta_raw_units': None, 'quality': 'censored'}
    n = current['raw_units'] - previous['raw_units']
    return {'delta_raw_units': n if n >= 0 else None,
            'quality': 'reset_restore_or_wrap_unknown' if n < 0 else 'non_atomic_uncalibrated'}

def fold(pending, mode=1):
    """CD8F6/CDDCA: mode1 clears remainder after divide-by-60."""
    if pending < 0 or mode not in (1, 2):
        raise ValueError('Unsupported accounting mode')
    return pending // 60 if mode == 1 else pending

def get07(frame):
    if len(frame) != 22 or frame[:5] != bytes.fromhex('fc62027a10') or sum(frame) % 256 != 0xfc or frame[5] != 7:
        raise ValueError('Not a complete GET07 response')
    p = frame[5:21]
    return {'consumed_raw': int.from_bytes(p[3:5], 'big'),
            'produced_raw': int.from_bytes(p[5:7], 'big'),
            'counter_raw': int.from_bytes(p[11:13], 'big')}

def a3(frame, selector):
    api600(selector)
    if len(frame) != 22 or frame[:5] != bytes.fromhex('fc62027a10') or sum(frame) % 256 != 0xfc:
        raise ValueError('Invalid A3 frame')
    p = frame[5:21]
    if p[0] != 0xa3 or int.from_bytes(p[1:3], 'big') != selector or p[3] != 1:
        raise ValueError('Wrong A3 selector or format')
    raw = int.from_bytes(p[4:6], 'little')
    bcd(raw)
    return raw

def observations(rows):
    """Decode timestamped, correlated captures without requesting hardware."""
    out = []
    last = {}
    for row in rows:
        selector = row['selector']
        api600(selector, row['correlation'])
        stamps = [datetime.fromisoformat(row[k]) for k in ('high_at', 'low_at', 'repeat_at')]
        if any(t.tzinfo is None for t in stamps) or not stamps[0] <= stamps[1] <= stamps[2]:
            raise ValueError('Timestamps require ordered offsets')
        if row['format'] != 1:
            raise ValueError('Energy requires format1')
        frames = row['raw_frames']
        if len(frames) != 3: raise ValueError('Require high, low, repeated-low raw frames')
        values = [a3(bytes.fromhex(f), code) for f, code in zip(frames, (selector, selector+1, selector+1))]
        if values != [row['high'], row['low'], row['repeat_low']]:
            raise ValueError('Decoded values disagree with raw frames')
        result = pair(selector, *values)
        result['capture'] = row
        result['delta'] = delta(last[selector], result) if selector in last else None
        last[selector] = result
        out.append(result)
    return out
