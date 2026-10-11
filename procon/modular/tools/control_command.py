"""P0076: encode v2/v3 operator commands offline; never send device traffic."""
import argparse
import json
from decimal import Decimal, InvalidOperation

MODES = {'off': 0, 'auto': 1, 'fixed-flow': 2, 'dhw': 3, 'targets': 4, 'effect': 5}


def validate_slave(slave):
    if type(slave) is not int or not 1 <= slave <= 247:
        raise ValueError('Slave must be an explicit unicast address from 1 through 247')
    return slave


def temperature(value, low, high):
    try:
        n = Decimal(str(value)) * 100
        if not n.is_finite() or n != int(n) or not low <= n <= high:
            raise ValueError('Target outside allowed range/precision')
        return int(n)
    except (InvalidOperation, TypeError) as error:
        raise ValueError('Temperature must be a finite decimal Celsius value') from error


def crc16(frame):
    crc = 65535
    for byte in frame:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xa001 if crc & 1 else 0)
    return crc


def encode(sequence, mode, flow=None, dhw=None, lease=0, *, slave=1,
           target_w=None, max_flow=None, boundary_verified=False):
    validate_slave(slave)
    if type(sequence) is not int or not 1 <= sequence <= 65535 or not isinstance(mode, str) or mode not in MODES:
        raise ValueError('Invalid sequence/mode')
    if type(lease) is not int:
        raise ValueError('Lease must be an integer number of seconds')
    if mode == 'effect':
        if flow is not None or dhw is not None:
            raise ValueError('EFFECT accepts target W and maximum flow, not v2 temperature targets')
        if boundary_verified is not True:
            raise ValueError('EFFECT requires explicit verification of the space-heating measurement boundary')
        if type(target_w) is not int or not 1000 <= target_w <= 12000:
            raise ValueError('Per-unit EFFECT target must be 1000–12000 W')
        if max_flow is None or not 90 <= lease <= 1800:
            raise ValueError('EFFECT requires maximum flow and lease 90–1800 seconds')
        cap = temperature(max_flow, 3000, 5500)
        words = [0xc076, sequence, 5, target_w, cap, lease, 1, 3]
    else:
        if target_w is not None or max_flow is not None or boundary_verified is not False:
            raise ValueError('EFFECT options cannot be used with a v2 command')
        flags = (1 if flow is not None else 0) | (2 if dhw is not None else 0)
        f = temperature(flow, 2000, 4500) if flow is not None else 0
        d = temperature(dhw, 4000, 6000) if dhw is not None else 0
        if mode == 'auto':
            if flags or lease:
                raise ValueError('AUTO accepts no targets/lease; restores saved session')
        elif not 30 <= lease <= 1800:
            raise ValueError('Lease must be 30–1800 seconds')
        if mode == 'fixed-flow' and flow is None:
            raise ValueError('Fixed flow requires target')
        if mode == 'targets' and not flags:
            raise ValueError('No targets')
        if mode in ('off', 'dhw') and flow is not None:
            raise ValueError('Flow not permitted in this mode')
        words = [0xc072, sequence, MODES[mode], f, d, lease, flags, 2]
    frame = bytes([slave]) + bytes.fromhex('10 01 2c 00 08 10') + b''.join(word.to_bytes(2, 'big') for word in words)
    return {'sent': False, 'slave_id': slave, 'function': 16, 'address': 300, 'words': words,
            'rtu_hex': (frame + crc16(frame).to_bytes(2, 'little')).hex(' '),
            'warning': 'Supervised candidate. Verify the addressed physical UID and heating boundary, preserve original settings externally, and verify applied sequence/readback. No reboot restoration guarantee.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sequence', type=int, required=True)
    parser.add_argument('--mode', choices=MODES, required=True)
    parser.add_argument('--slave', type=int, default=1)
    parser.add_argument('--flow')
    parser.add_argument('--dhw')
    parser.add_argument('--lease', type=int, default=0)
    parser.add_argument('--target-w', type=int)
    parser.add_argument('--max-flow', help='maximum heating flow temperature in Celsius, 30–40')
    parser.add_argument('--boundary-verified', action='store_true', help='operator has verified this unit’s space-heating measurement boundary')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(encode(args.sequence, args.mode, args.flow, args.dhw, args.lease,
                                slave=args.slave, target_w=args.target_w, max_flow=args.max_flow,
                                boundary_verified=args.boundary_verified), indent=2))
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
