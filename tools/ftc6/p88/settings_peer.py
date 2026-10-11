"""Offline FTC side of the D-peer settings handshake; no packet sender."""


def advertisement(state, direction, category_mask, alternate_role=False):
    if not 0 <= state <= 12 or direction not in (0, 1) or not 0 <= category_mask <= 255:
        raise ValueError('invalid state/direction/mask')
    if alternate_role:
        return 6, 0
    value = direction
    if state == 1:
        return 1, ((category_mask << 2) & 0x1fc) | value
    return 6, value


def control_response(image, state, direction, selector, argument, result):
    """8D36C: result is existing (format, low byte, high byte)."""
    if not 0 <= state <= 12 or direction not in (0, 1) or not 0 <= argument <= 255:
        raise ValueError('invalid state/direction/argument')
    if not 0 <= selector <= 65535 or len(result) != 3 or any(not 0 <= v <= 255 for v in result):
        raise ValueError('invalid selector/result')
    row = {1002: 0, 1003: 4, 1004: 6, 0: 8, 9999: 12}.get(selector, 10)
    row += min(argument, 3 if selector == 1002 else 1)
    column = image.at(0x806fe + direction * 13 + state, 1)[0]
    if column >= 15:
        raise ValueError('invalid response column')
    code = image.at(0x80718 + row * 15 + column, 1)[0]
    if code > 11:
        raise ValueError('invalid response action')
    fmt, low, high = result
    if code in (0, 1, 2, 3):
        fmt = 7 if code < 2 else 0
        low = (low & 0xfc) | (code & 1)
    elif code in (4, 5):
        fmt, low, high = (15 if code == 4 else 14), 0, 0
    elif code in (6, 7):
        fmt = 15 if code == 6 else 14
    elif code == 8:
        fmt = 0
    elif code == 10:
        low, high = 0, 0
    elif code == 11:
        fmt, low, high = 0, 0, 0
    return {'action': code, 'result': (fmt, low, high)}
