"""Offline decoder for one statically traced source-link result envelope.

Not a transport/state-machine emulator; never sends bytes.
"""


def decode(data):
    data = bytes(data)
    if len(data) != 6:
        raise ValueError('service result must contain six bytes')
    if data[0] & 0x1f != 0x1d:
        raise ValueError('not the traced service-result family')
    if sum(data) & 0xff:
        raise ValueError('invalid checksum')
    word = int.from_bytes(data[1:3], 'little')
    return {
        'selector': word & 0x3ff,
        'format': word >> 13,
        'unresolved_selector_bits': (word >> 10) & 7,
        'unresolved_type_bits': data[0] >> 5,
        'value_bytes': list(data[3:5]),
        'raw_word_le': int.from_bytes(data[3:5], 'little'),
        'state_acceptance': 'not evaluated',
    }
