"""P0088: selected native settings-store semantics, pure offline functions.

Not an EEPROM driver or a full scheduler. Shadow equality is not proof of saving.
"""
SIZE = 512


def _image(value):
    value = bytes(value)
    if len(value) != SIZE:
        raise ValueError('settings image must be 512 bytes')
    return value


def pump_fields(image):
    image = _image(image)
    return {'dhw_pump_raw': image[0x160], 'heating_pump_raw': image[0x1ab]}


def first_dirty_word(desired, shadow):
    desired, shadow = _image(desired), _image(shadow)
    return next((i for i in range(0, SIZE, 2) if desired[i:i+2] != shadow[i:i+2]), None)


def verify_word(desired, shadow, offset, reads, failures):
    desired, shadow = _image(desired), bytearray(_image(shadow))
    if not 0 <= offset < SIZE or offset % 2 or len(reads) != 2 or any(not 0 <= x <= 65535 for x in reads):
        raise ValueError('invalid word offset/readbacks')
    if failures not in (0, 1, 2):
        raise ValueError('invalid prior verification-failure count')
    expected = int.from_bytes(desired[offset:offset+2], 'little')
    verified = reads[0] == reads[1] == expected
    failures = 0 if verified else failures + 1
    fault = failures >= 3
    accounted = verified or fault
    if accounted:
        shadow[offset:offset+2] = desired[offset:offset+2]
        failures = 0
    return {'shadow': bytes(shadow), 'failures': failures, 'fault': fault,
            'accounted': accounted, 'persistence_verified': verified}
