"""P0088 pure byte mappings; no frame transmission or freshness inference."""

def _unsigned(value, maximum):
    if not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValueError('bounded unsigned raw value required')
    return value


def flow_byte(raw):
    """A4316: unsigned division then byte truncation, not saturation."""
    return (_unsigned(raw, 65535) // 100) & 255


def state_byte(raw):
    """A43C8: a native enumeration is permuted, not a Boolean."""
    return (0, 2, 1, 3, 4)[raw] if _unsigned(raw, 255) < 5 else 0


def control_flags(word_082a, byte_0630):
    """A4AE8: selected bits, no external flag-name assumptions."""
    return ((_unsigned(word_082a, 65535) >> 11) & 7) | ((_unsigned(byte_0630, 255) & 2) << 3)
