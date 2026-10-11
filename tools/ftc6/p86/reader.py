#!/usr/bin/env python3
"""P0086 deterministic offline planner/replayer. Hardware backend intentionally absent."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import uart1
import energy

def plan(operation, address=None, length=None):
    middle = [] if operation == 'session' else [dict(operation=operation, address=address, length=length)]
    steps = [dict(operation='open')] + middle + [dict(operation='close')]
    for s in steps:
        s['request_hex'] = uart1.request(s['operation'], s.get('address'), s.get('length')).hex()
        s['retries'] = 0
    return steps

def replay(steps, fixture, request_timeout=2, total_timeout=10):
    """Fixture times are simulated elapsed seconds. Raw evidence survives every failure."""
    out = dict(status='PASS', physical='NOT RUN', evidence=[], errors=[], closure_verified=False)
    if not all(math.isfinite(t) and 0 < t <= 60 for t in (request_timeout, total_timeout)):
        raise ValueError('Finite positive bounded timeouts required')
    elapsed = 0
    for i, step in enumerate(steps):
        if i >= len(fixture):
            out['errors'].append('missing_response'); break
        record = fixture[i]
        out['evidence'].append({'step': step, 'raw_fixture': record})
        if record.get('cancelled'):
            out['errors'].append('cancelled_no_further_requests'); break
        try:
            dt = float(record['elapsed'])
            if not math.isfinite(dt) or dt < 0: raise ValueError('Invalid elapsed time')
            elapsed += dt
            if dt > request_timeout or elapsed > total_timeout:
                raise ValueError('deadline_exceeded_no_retry')
            data = bytes.fromhex(record['response_hex'])
            if step['operation'] == 'close':
                if data: raise ValueError('Unexpected close response')
                out['close_silence_observed'] = True
            else:
                payload = uart1.response(data, step['operation'], step.get('length'))
                out['evidence'][-1]['decoded'] = uart1.logs(data) if step['operation'] == 'log' else {'data_hex': payload.hex(), 'sha256': hashlib.sha256(payload).hexdigest()}
        except (ValueError, KeyError, TypeError) as exc:
            out['errors'].append(str(exc)); break
    if out['errors']: out['status'] = 'FAIL'
    if len(fixture) > len(steps):
        out['errors'].append('extra_fixture_records'); out['status']='FAIL'
    out['elapsed_simulated_seconds'] = elapsed
    out['closure_note'] = 'Silence is not proof; verify native state separately. On failure session may remain open.'
    return out

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', required=True, choices=uart1.PROFILES)
    p.add_argument('--image-sha', default=uart1.IMAGE_SHA)
    p.add_argument('--operation', choices=('session', 'read', 'log', 'energy'), default='session')
    p.add_argument('--address', type=lambda x:int(x,0))
    p.add_argument('--length', type=int)
    p.add_argument('--fixture', type=Path)
    p.add_argument('--output', type=Path, help='Exclusive creation; existing evidence never overwritten')
    p.add_argument('--request-timeout', type=float, default=2)
    p.add_argument('--total-timeout', type=float, default=10)
    p.add_argument('--execute', action='store_true', help='Always rejected until hardware profile qualified')
    a = p.parse_args(argv)
    try:
        uart1.profile(a.profile, a.image_sha)
        if a.execute: raise ValueError('LIVE BLOCKED: connector, levels, personality, DTR/RTS and 21.00 addresses unqualified')
        if a.operation == 'energy':
            if not a.fixture: raise ValueError('Energy requires timestamped fixture')
            result = dict(status='PASS', physical='NOT RUN', observations=energy.observations(json.loads(a.fixture.read_text())))
        else:
            steps = plan(a.operation, a.address, a.length)
            result = replay(steps, json.loads(a.fixture.read_text()), a.request_timeout, a.total_timeout) if a.fixture else dict(status='DRY_RUN', physical='NOT RUN', steps=steps)
        result['profile'] = a.profile
        result['image_sha256'] = a.image_sha
        text = json.dumps(result, indent=2, sort_keys=True)+'\n'
        if a.output:
            with a.output.open('x') as f: f.write(text)
        else: sys.stdout.write(text)
        return 0 if result['status'] != 'FAIL' else 1
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.exit(2, str(exc)+'\n')

if __name__ == '__main__':
    raise SystemExit(main())
