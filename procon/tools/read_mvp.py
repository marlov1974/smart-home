"""P0072 operator-run read-only snapshot. No Modbus writes or CN105 control."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from read_brine import request_block

NAMES = ['brine_in_cC', 'brine_out_cC', 'brine_delta_cC', 'flow_cC', 'return_cC',
         'water_delta_cC', 'flow_cL_min', 'heat_W', 'compressor_Hz', 'compressor_running',
         'brine_pump_running', 'brine_pump_step', 'water_pump_running', 'water_pump_level',
         'dhw_cC', 'outdoor_cC', 'flow_target_cC', 'dhw_target_cC', 'operating_mode_raw', 'heater_bits']


def capture(host):
    blocks = []
    def read(a, n):
        words = []
        for offset in range(0, n, 16):
            block = request_block(host, a+offset, min(16, n-offset))
            blocks.append(block)
            words.extend(block['values'])
        return words
    baseline = read(0, 16)
    identity = read(68, 4)
    if baseline[:2] != [888, 72] or not (identity == [1, 1, 1, 4] or (identity[:3] == [2, 1, 3] and identity[3] <= 6)):
        raise ValueError('Expected P0072 r1/r2 telemetry API; refusing to decode another map')
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
    if identity[0] == 2:
        control = read(256, 27)
    samples = {}
    for i, name in enumerate(NAMES):
        coherent = before[i] == after[i] and state_before[i] == states[i]
        raw = (words[2*i] << 16) | words[2*i+1]
        signed = raw - (1 << 32) if raw & (1 << 31) else raw
        samples[name] = {'value': signed if coherent and states[i] == 1 else None,
                         'coherent': coherent, 'status': states[i], 'age_s': ages[i],
                         'generation': after[i], 'hardware_correlated': False}
    return {'timestamp': datetime.now(timezone.utc).isoformat(), 'read_only': True,
            'blocks': blocks, 'samples': samples, 'identity': identity, 'control_words_256_282': control,
            'note': 'Multi-block acquisition; generations/status bracket reads. Units are API integers; fresh does not mean physically calibrated.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='192.168.86.85')
    parser.add_argument('--samples', type=int, default=10)
    parser.add_argument('--interval', type=float, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.samples <= 3600 or not 0.2 <= args.interval <= 60:
        parser.error('samples 1–3600; interval 0.2–60 seconds')
    with args.output.open('x') as output:
        for i in range(args.samples):
            start = time.monotonic()
            try:
                record = capture(args.host)
            except Exception as exc:
                record = {'timestamp': datetime.now(timezone.utc).isoformat(), 'read_only': True, 'error': str(exc)}
            line = json.dumps(record)
            output.write(line+'\n'); output.flush(); print(line, flush=True)
            if i+1 < args.samples:
                time.sleep(max(0, args.interval-(time.monotonic()-start)))


if __name__ == '__main__':
    main()
