"""P0076 addressed read-only snapshots, retaining P0072 r1/r2/r3 decoding."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.request import urlopen
from control_command import validate_slave
from commission_units import decode_identity, decode_dip, normalize_uid

NAMES = ['brine_in_cC', 'brine_out_cC', 'brine_delta_cC', 'flow_cC', 'return_cC',
         'water_delta_cC', 'flow_cL_min', 'heat_W', 'compressor_Hz', 'compressor_running',
         'brine_pump_running', 'brine_pump_step', 'water_pump_running', 'water_pump_level',
         'dhw_cC', 'outdoor_cC', 'flow_target_cC', 'dhw_target_cC', 'operating_mode_raw', 'heater_bits']


def request_block(host, address, quantity, slave=1):
    validate_slave(slave)
    if type(address) is not int or address < 0 or type(quantity) is not int or not 1 <= quantity <= 16 or address + quantity > 65536:
        raise ValueError('Read requires a nonnegative address and 1–16 words')
    stamp = datetime.now(timezone.utc).isoformat()
    url = f'http://{host}/rpc/MbRtuClient.ReadInputRegisters?id=100&sid={slave}&addr={address}&qty={quantity}'
    with urlopen(url, timeout=8) as response:
        result = json.load(response)
    values = result.get('values') if isinstance(result, dict) else None
    if not isinstance(values, list) or len(values) != quantity or any(type(v) is not int or not 0 <= v <= 65535 for v in values):
        raise ValueError('Invalid addressed input-register response')
    return {'timestamp': stamp, 'slave_id': slave, 'address': address, 'quantity': quantity, 'values': values}


def signed32(high, low):
    value = (high << 16) | low
    return value - (1 << 32) if value & (1 << 31) else value


def decode_effect(words):
    if not isinstance(words, list) or len(words) != 32 or any(type(v) is not int or not 0 <= v <= 65535 for v in words) or words[0] != 1:
        raise ValueError('Expected P0076 EFFECT diagnostic schema1 at input320')
    values = [signed32(words[i], words[i+1]) for i in (5, 7, 9, 11)]
    values = [None if value == -(1 << 31) else value for value in values]
    signed16 = lambda value: value - 65536 if value & 32768 else value
    return {'words_320_351': words, 'schema': words[0], 'phase': words[1], 'limit_reason': words[2],
            'target_w': words[3], 'maximum_flow_cC': words[4],
            'instant_w': values[0], 'short_w': values[1], 'slow_w': values[2], 'error_w': values[3],
            'quality': words[13], 'ready': bool(words[14]), 'pairs': words[15],
            'age_s': words[16], 'short_span_s': words[17], 'flow_target_cC': words[18],
            'last_adjustment_cC': signed16(words[19]), 'adjustment_age_s': words[20],
            'compressor_hz': words[21], 'decisions': words[22], 'adjustments': words[23],
            'cumulative_up_cC': words[24], 'cumulative_down_cC': words[25],
            'unresponsive_count': words[26], 'pending_flow_cC': words[27],
            'derivative_w_per_min': signed16(words[28]), 'initial_flow_cC': words[29],
            'boot_recovery_unknown': bool(words[30]), 'persistent_recovery_supported': bool(words[31]),
            'atomic': False}


def decode_feedback(words):
    if not isinstance(words, list) or len(words) != 20 or any(type(v) is not int or not 0 <= v <= 65535 for v in words) or words[0] != 1:
        raise ValueError('Expected P0076 feedback diagnostic schema1 at input352')
    if words[1] > 9 or words[2] > 1:
        raise ValueError('Unknown feedback quality/readiness encoding')
    values = [signed32(words[i], words[i+1]) for i in (12, 14, 16, 18)]
    values = [None if value == -(1 << 31) else value for value in values]
    quality_names = ('ready', 'warmup', 'pending', 'stale', 'invalid', 'zero-flow', 'dhw', 'link-loss', 'wait-native', 'settling')
    return {'words_352_371': words, 'schema': words[0], 'quality': words[1],
            'quality_name': quality_names[words[1]], 'ready': bool(words[2]),
            'short_count': words[3], 'slow_count': words[4],
            'short_span_s': words[5], 'slow_span_s': words[6],
            'short_window_s': 60, 'slow_window_s': 180,
            'last_age_s': None if words[7] == 65535 else words[7], 'last_age_s_raw': words[7],
            'temperature_generation': words[8], 'flow_generation': words[9],
            'accepted_count': (words[10] << 16) | words[11],
            'instant_w': values[0], 'short_w': values[1], 'slow_w': values[2],
            'derivative_w_per_min': values[3], 'atomic': False,
            'note': 'Multi-block diagnostic snapshot; counts/spans describe actual partial coverage, not a guaranteed full window. Source generations are the last accepted pair; repeated reads are not new samples.'}


def capture(host, slave=1, expected_uid=None):
    validate_slave(slave)
    if expected_uid is not None:
        expected_uid = normalize_uid(expected_uid)
    blocks = []
    def read(a, n):
        words = []
        for offset in range(0, n, 16):
            block = request_block(host, a+offset, min(16, n-offset), slave)
            blocks.append(block)
            words.extend(block['values'])
        return words
    baseline = read(0, 16)
    identity = read(68, 4)
    legacy = baseline[:2] == [888, 72] and (identity == [1, 1, 1, 4] or (identity[0] in (2, 3) and identity[1:3] == [1, 3] and identity[3] <= 6))
    p76 = baseline[:2] == [888, 76] and identity[0] in (1, 2) and identity[1:3] == [1, 15] and identity[3] <= 6
    if not legacy and not p76:
        raise ValueError('Expected P0072 r1/r2/r3 or P0076 r1/r2 telemetry API; refusing to decode another map')
    unit_identity = None
    if p76:
        unit_words = read(72, 15)
        unit_identity = decode_identity(unit_words[:12], requested_slave=slave)
        if unit_identity['source'] == 3:
            unit_identity['dip'] = decode_dip(unit_words[12:], unit_identity)
    if expected_uid is not None and (unit_identity is None or unit_identity['uid96'] != expected_uid):
        raise ValueError('Expected physical MCU UID does not match addressed firmware identity')
    before = read(180, 20)
    state_before = read(140, 20)
    words = read(100, 40)
    read(16, 16)
    read(32, 16)
    read(52, 16)
    read(200, 56)
    ages = read(160, 20)
    states = read(140, 20)
    after = read(180, 20)
    control = None
    if p76 or identity[0] >= 2:
        control = read(256, 27)
    diagnostics = None
    if p76 or identity[0] >= 3:
        d = read(283, 16)
        raw = b''.join(v.to_bytes(2, 'little') for v in d[5:13])
        diagnostics = {'words_283_298': d, 'received': bool(d[0]), 'age_s': d[1],
                       'generation': d[2], 'blocking_mask': d[3], 'relevant_mask': d[4],
                       'payload_hex': raw.hex(' '), 'last_rejected_query': d[13],
                       'last_rejected_byte': d[14], 'last_rejected_value': d[15],
                       'flags': {name: raw[i] for i,name in enumerate(
                           ['boost','holiday','prohibit_dhw','prohibit_heating_z1',
                            'prohibit_cooling_z1','prohibit_heating_z2','prohibit_cooling_z2','server_control'],3)}}
    samples = {}
    for i, name in enumerate(NAMES):
        # Derived counters alone do not prove that each constituent stayed fixed.
        constituents = {2: (0, 1), 5: (3, 4), 7: (3, 4, 6), 9: (8,)}.get(i, ())
        coherent = all(before[j] == after[j] and state_before[j] == states[j] for j in (i, *constituents))
        raw = (words[2*i] << 16) | words[2*i+1]
        signed = raw - (1 << 32) if raw & (1 << 31) else raw
        samples[name] = {'value': signed if coherent and states[i] == 1 else None,
                         'coherent': coherent, 'status': states[i], 'age_s': ages[i],
                         'generation': after[i], 'hardware_correlated': False}
    effect = decode_effect(read(320, 32)) if p76 else None
    feedback = decode_feedback(read(352, 20)) if p76 else None
    return {'timestamp': datetime.now(timezone.utc).isoformat(), 'read_only': True, 'slave_id': slave,
            'blocks': blocks, 'samples': samples, 'identity': identity, 'control_words_256_282': control, 'controller_diagnostics': diagnostics,
            'package': 76 if p76 else 72, 'unit_identity': unit_identity, 'effect_diagnostics': effect,
            'feedback_diagnostics': feedback,
            'note': 'Multi-block acquisition; generations/status bracket reads. Units are API integers; fresh does not mean physically calibrated.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True)
    parser.add_argument('--slave', type=int, default=1)
    parser.add_argument('--expected-uid', help='optional pinned 24-hex physical UID; requires P0076')
    parser.add_argument('--samples', type=int, default=10)
    parser.add_argument('--interval', type=float, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.samples <= 3600 or not 0.2 <= args.interval <= 60:
        parser.error('samples 1–3600; interval 0.2–60 seconds')
    try:
        validate_slave(args.slave)
        if args.expected_uid is not None:
            normalize_uid(args.expected_uid)
    except ValueError as error:
        parser.error(str(error))
    with args.output.open('x') as output:
        for i in range(args.samples):
            start = time.monotonic()
            try:
                record = capture(args.host, args.slave, args.expected_uid)
            except Exception as exc:
                record = {'timestamp': datetime.now(timezone.utc).isoformat(), 'read_only': True, 'error': str(exc)}
            line = json.dumps(record)
            output.write(line+'\n'); output.flush(); print(line, flush=True)
            if i+1 < args.samples:
                time.sleep(max(0, args.interval-(time.monotonic()-start)))


if __name__ == '__main__':
    main()
