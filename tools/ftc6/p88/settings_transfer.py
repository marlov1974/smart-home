"""P0088: bounded D-path settings transfer fields. Offline, no sender."""


def ranges(image):
    result = []
    for index in range(33):
        address = 0x807ea + index * 8
        raw = image.at(address, 8)
        first, last, offset, bank = [int.from_bytes(raw[i:i+2], 'little') for i in range(0, 8, 2)]
        if not 1 <= first <= last <= 1023 or bank > 4 or offset + 3 * (last-first) + 2 >= 512:
            raise ValueError('invalid settings transfer range')
        start = 0x1940 + bank * 512 + offset
        result.append(dict(index=index, operand=f'{address:05x}', first=first,
                           last=last, bank=bank, offset=offset,
                           staging_first=start, staging_last=start+3*(last-first)+2))
    return result


def resolve(table, selector):
    if not 0 <= selector <= 1023:
        raise ValueError('selector outside extended field')
    if selector == 0:
        return {'kind': 'end-marker', 'staging_address': None}
    for row in table:
        if row['first'] <= selector <= row['last']:
            return {'kind': 'triple', 'staging_address': row['staging_first']+3*(selector-row['first']),
                    'range_index': row['index']}
    return {'kind': 'unmapped', 'staging_address': None}


def extended_fields(word):
    if not 0 <= word <= 65535 or not word & 1:
        raise ValueError('not an extended settings word')
    return {'selector': word >> 6, 'format': (word >> 1) & 15, 'direction': (word >> 5) & 1}


def admitted(word, session_direction, dispatcher_role, transfer_kind):
    """Only the local8BD02 gate; parser, personality and session gates remain."""
    if session_direction not in (0, 1) or not 0 <= dispatcher_role <= 255:
        raise ValueError('invalid direction/dispatcher role')
    fields = extended_fields(word)
    return dispatcher_role & 15 == 6 and transfer_kind == 2 and fields['direction'] == session_direction
