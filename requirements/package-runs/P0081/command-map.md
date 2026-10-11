# P0081 physical mapping

Firmware manifest `71b30837`. One FTC6/Geodan installation; results are observations, not a universal support list.

Run complete: **True**. 720 / 720 planned observations (512 direct, 208 documented service reads).

Outcomes: DONE=354, TIMEOUT=344, UNSUPPORTED=22.

Only zero-parameter CN105 GET 0x42 and vetted read-only A3 transactions were submitted. No heating controls, service settings, resets or vendor bootloader operations were submitted by the mapper. Native heating-curve operation remained enabled. Device identifiers, raw customer frames and measured values are omitted from this export.

TIMEOUT means no correlated reply within this diagnostic transaction; it does not prove that a code is unsupported. Direct GET A3 and parameterized A3 service requests are separate operations. A reply, zero-filled data or an FF pattern does not establish sensor availability. Different raw replies do not by themselves establish useful dynamic telemetry. Other message types or parameterized variants are outside this zero-parameter GET scan.

For allowed service codes, API status UNSUPPORTED means an unhandled nonzero A3 status outside the established 1/2; it does not prove that the heat pump lacks the command. Raw responses remain in the private evidence for subsequent decoding.

Service labels and display units follow Mitsubishi OCH722A, printed pages 30–32. CN105 interpretation reference: [F1p decoder, pinned revision](https://github.com/F1p/Home-Assistant-Mitsubishi-CN105-to-MQTT/blob/7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5/EcodanDecoder.cpp). Manual units do not establish wire scaling, sensor installation or present-day measurements for historical fault codes.

| Kind | Code | Samples | Outcomes | Valid replies | Unique valid payloads | Manual display candidate (wire scale unverified) | Classification |
|---|---|---:|---|---:|---:|---|---|
| DIRECT | 0x00 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x01 | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x02 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x03 | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x04 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x05 | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x06 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x07 | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x08 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x09 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x0A | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x0B | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x0C | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x0D | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x0E | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x0F | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x10 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x11 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x12 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x13 | 2 | DONE:2 | 2 | 2 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x14 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x15 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x16 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x17 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x18 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x19 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x1A | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x1B | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x1C | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x1D | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x1E | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x1F | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x20 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x21 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x22 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x23 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x24 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x25 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x26 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x27 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0x28 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x29 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0x2A | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x2B | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x2C | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x2D | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x2E | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x2F | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x30 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x31 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x32 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x33 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x34 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x35 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x36 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x37 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x38 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x39 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x3A | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x3B | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x3C | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x3D | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x3E | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x3F | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x40 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x41 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x42 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x43 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x44 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x45 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x46 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x47 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x48 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x49 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x4A | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x4B | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x4C | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x4D | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x4E | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x4F | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x50 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x51 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x52 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x53 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x54 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x55 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x56 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x57 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x58 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x59 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x5A | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x5B | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x5C | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x5D | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x5E | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x5F | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x60 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x61 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x62 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x63 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x64 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x65 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x66 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x67 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x68 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x69 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x6A | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x6B | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x6C | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x6D | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x6E | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x6F | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x70 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x71 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x72 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x73 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x74 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x75 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x76 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x77 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x78 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x79 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x7A | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x7B | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x7C | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x7D | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x7E | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0x7F | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x80 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x81 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x82 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x83 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x84 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x85 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x86 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x87 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x88 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x89 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x8A | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x8B | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x8C | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x8D | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x8E | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x8F | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x90 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x91 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x92 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x93 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x94 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x95 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x96 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x97 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x98 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x99 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x9A | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x9B | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x9C | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x9D | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x9E | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0x9F | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA0 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA1 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0xA2 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; interpretation not established by this scan |
| DIRECT | 0xA3 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; data bytes all zero |
| DIRECT | 0xA4 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA5 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA6 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA7 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA8 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xA9 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xAA | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xAB | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xAC | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xAD | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xAE | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xAF | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB0 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB1 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB2 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB3 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB4 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB5 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB6 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB7 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB8 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xB9 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xBA | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xBB | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xBC | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xBD | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xBE | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xBF | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC0 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC1 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC2 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC3 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC4 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC5 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC6 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC7 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xC8 | 2 | DONE:2 | 2 | 1 | unknown bytes | Valid reply; FF/zero pattern, meaning unknown |
| DIRECT | 0xC9 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xCA | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xCB | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xCC | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xCD | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xCE | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xCF | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD0 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD1 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD2 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD3 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD4 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD5 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD6 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD7 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD8 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xD9 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xDA | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xDB | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xDC | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xDD | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xDE | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xDF | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE0 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE1 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE2 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE3 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE4 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE5 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE6 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE7 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE8 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xE9 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xEA | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xEB | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xEC | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xED | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xEE | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xEF | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF0 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF1 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF2 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF3 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF4 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF5 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF6 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF7 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF8 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xF9 | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xFA | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xFB | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xFC | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xFD | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xFE | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| DIRECT | 0xFF | 2 | TIMEOUT:2 | 0 | 0 | unknown bytes | UNKNOWN / no valid reply |
| A3 service | 0 | 2 | UNSUPPORTED:2 | 0 | 0 | Operating state; status; OCH722A p30 | Unhandled A3 status [4]; captured frame is not proof of absent service |
| A3 service | 1 | 2 | DONE:2 | 2 | 1 | Compressor RMS current; A; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 2 | 2 | DONE:2 | 2 | 1 | Compressor runtime; 10 hours; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 3 | 2 | DONE:2 | 2 | 1 | Compressor starts; 100 starts; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 4 | 2 | DONE:2 | 2 | 1 | Discharge TH4; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 5 | 2 | DONE:2 | 2 | 1 | Liquid pipe TH3; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 9 | 2 | DONE:2 | 2 | 1 | Outdoor TH7; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 10 | 2 | DONE:2 | 2 | 1 | Heat sink TH8; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 12 | 2 | DONE:2 | 2 | 1 | Discharge superheat; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 13 | 2 | DONE:2 | 2 | 1 | Subcooling; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 14 | 2 | UNSUPPORTED:2 | 0 | 0 | Condensing temperature; degC; OCH722A p30 | Unhandled A3 status [6]; captured frame is not proof of absent service |
| A3 service | 16 | 2 | DONE:2 | 2 | 2 | Compressor actual frequency; Hz; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 17 | 2 | DONE:2 | 2 | 2 | Compressor target frequency; Hz; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 18 | 2 | DONE:2 | 2 | 1 | Brine pump command; step 0-10; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 19 | 2 | DONE:2 | 2 | 2 | Brine pump speed; rpm; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 22 | 2 | DONE:2 | 2 | 1 | Expansion valve A; pulses; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 25 | 2 | DONE:2 | 2 | 1 | Primary current; A; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 26 | 2 | DONE:2 | 2 | 1 | DC link voltage; V; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 27 | 2 | DONE:2 | 2 | 1 | Brine inlet TH32; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 28 | 2 | DONE:2 | 2 | 1 | Brine outlet TH34; degC; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 48 | 2 | DONE:2 | 2 | 2 | Thermostat-on duration; minutes; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 51 | 2 | DONE:2 | 2 | 1 | Compressor-board control; status; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 52 | 2 | DONE:2 | 2 | 1 | Frequency limiting/control; status; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 53 | 2 | DONE:2 | 2 | 1 | Fan control; status; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 54 | 2 | DONE:2 | 2 | 1 | Actuator outputs; bitfield; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 55 | 2 | DONE:2 | 2 | 1 | U9 details; status; OCH722A p30 | Valid reply; interpretation not established by this scan |
| A3 service | 70 | 2 | DONE:2 | 2 | 1 | Compressor-board capacity configuration; status; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 71 | 2 | DONE:2 | 2 | 1 | Compressor-board settings; status; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 90 | 2 | DONE:2 | 2 | 1 | Compressor-board version; version digits; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 91 | 2 | DONE:2 | 2 | 1 | Compressor-board version suffix; version digits; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 100 | 2 | UNSUPPORTED:2 | 0 | 0 | Deferred-fault history entry 1; fault code; historical; OCH722A p31 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 101 | 2 | UNSUPPORTED:2 | 0 | 0 | Deferred-fault history entry 2; fault code; historical; OCH722A p31 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 102 | 2 | UNSUPPORTED:2 | 0 | 0 | Deferred-fault history entry 3; fault code; historical; OCH722A p31 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 103 | 2 | UNSUPPORTED:2 | 0 | 0 | Fault history entry 1; fault code; historical; OCH722A p31 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 104 | 2 | UNSUPPORTED:2 | 0 | 0 | Fault history entry 2; fault code; historical; OCH722A p31 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 105 | 2 | UNSUPPORTED:2 | 0 | 0 | Fault history entry 3; fault code; historical; OCH722A p31 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 106 | 2 | DONE:2 | 2 | 1 | TH3/TH7/TH8 fault sensor; sensor identifier; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 107 | 2 | UNSUPPORTED:2 | 0 | 0 | Operating state at fault; status; historical; OCH722A p31 | Unhandled A3 status [4]; captured frame is not proof of absent service |
| A3 service | 108 | 2 | DONE:2 | 2 | 1 | Compressor RMS current at fault; A; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 109 | 2 | DONE:2 | 2 | 1 | Compressor runtime at fault; 10 hours; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 110 | 2 | DONE:2 | 2 | 1 | Compressor starts at fault; 100 starts; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 111 | 2 | DONE:2 | 2 | 1 | Discharge TH4 at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 112 | 2 | DONE:2 | 2 | 1 | Liquid pipe TH3 at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 113 | 2 | DONE:2 | 2 | 1 | Brine outlet TH34 at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 115 | 2 | DONE:2 | 2 | 1 | Brine inlet TH32 at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 116 | 2 | DONE:2 | 2 | 1 | Outdoor TH7 at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 117 | 2 | DONE:2 | 2 | 1 | Heat sink TH8 at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 118 | 2 | DONE:2 | 2 | 1 | Discharge superheat at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 119 | 2 | DONE:2 | 2 | 1 | Subcooling at fault; degC; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 120 | 2 | DONE:2 | 2 | 1 | Compressor actual frequency at fault; Hz; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 121 | 2 | DONE:2 | 2 | 1 | Brine pump command at fault; step 0-10; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 122 | 2 | DONE:2 | 2 | 1 | Fan 1 speed at fault (manual wording; Geodan interpretation uncertain); rpm; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 125 | 2 | DONE:2 | 2 | 1 | Expansion valve A at fault; pulses; historical; OCH722A p31 | Valid reply; interpretation not established by this scan |
| A3 service | 129 | 2 | UNSUPPORTED:2 | 0 | 0 | Condensing temperature at fault; degC; historical; OCH722A p32 | Unhandled A3 status [6]; captured frame is not proof of absent service |
| A3 service | 130 | 2 | DONE:2 | 2 | 1 | Thermostat-on duration before fault; minutes; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 154 | 2 | DONE:2 | 2 | 1 | Water pump 1 runtime since reset; 10 hours; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 156 | 2 | DONE:2 | 2 | 1 | Water pump 2 runtime since reset; 10 hours; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 157 | 2 | DONE:2 | 2 | 1 | Water pump 3 runtime since reset; 10 hours; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 158 | 2 | DONE:2 | 2 | 1 | Water pump 4 runtime since reset; 10 hours; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 162 | 2 | DONE:2 | 2 | 1 | FTC DIP bank 1 readback; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 163 | 2 | DONE:2 | 2 | 1 | FTC DIP bank 2 readback; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 164 | 2 | DONE:2 | 2 | 1 | FTC DIP bank 3 readback; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 165 | 2 | DONE:2 | 2 | 1 | FTC DIP bank 4 readback; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 166 | 2 | DONE:2 | 2 | 1 | FTC DIP bank 5 readback; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 175 | 2 | DONE:2 | 2 | 1 | FTC outputs; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 176 | 2 | DONE:2 | 2 | 1 | FTC inputs; bitfield; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 177 | 2 | DONE:2 | 2 | 1 | Mixing valve command; step 0-10; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 190 | 2 | DONE:2 | 2 | 1 | FTC version first half; version digits; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 191 | 2 | DONE:2 | 2 | 1 | FTC version second half; version digits; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 504 | 2 | DONE:2 | 2 | 1 | Zone 1 room TH1A; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 505 | 2 | DONE:2 | 2 | 1 | Refrigerant liquid TH2; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 506 | 2 | DONE:2 | 2 | 1 | Return water THW2; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 507 | 2 | DONE:2 | 2 | 1 | Zone 2 room TH1B; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 508 | 2 | DONE:2 | 2 | 2 | DHW lower THW5B; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 509 | 2 | DONE:2 | 2 | 1 | Zone 1 supply THW6; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 510 | 2 | DONE:2 | 2 | 1 | Outdoor TH7 via FTC; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 511 | 2 | DONE:2 | 2 | 1 | Supply water THW1; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 512 | 2 | DONE:2 | 2 | 1 | Zone 1 return THW7; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 513 | 2 | DONE:2 | 2 | 1 | Zone 2 supply THW8; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 514 | 2 | DONE:2 | 2 | 1 | Zone 2 return THW9; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 515 | 2 | DONE:2 | 2 | 1 | Boiler supply THWB1; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 534 | 2 | DONE:2 | 2 | 2 | DHW upper THW5A; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 535 | 2 | DONE:2 | 2 | 1 | Mixing tank THW10; degC; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 540 | 2 | DONE:2 | 2 | 1 | Primary water flow; L/min; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 550 | 2 | UNSUPPORTED:2 | 0 | 0 | Latest FTC deferred fault; status; historical; OCH722A p32 | Unhandled A3 status [3]; captured frame is not proof of absent service |
| A3 service | 551 | 2 | DONE:2 | 2 | 1 | FTC heat source at fault; status; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 552 | 2 | DONE:2 | 2 | 1 | FTC operating mode at fault; status; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 553 | 2 | DONE:2 | 2 | 1 | FTC outputs at fault; bitfield; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 554 | 2 | DONE:2 | 2 | 1 | FTC inputs at fault; bitfield; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 555 | 2 | DONE:2 | 2 | 1 | Zone 1 room TH1A at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 556 | 2 | DONE:2 | 2 | 1 | Zone 2 room TH1B at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 557 | 2 | DONE:2 | 2 | 1 | Refrigerant liquid TH2 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 558 | 2 | DONE:2 | 2 | 1 | Supply water THW1 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 559 | 2 | DONE:2 | 2 | 1 | Return water THW2 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 560 | 2 | DONE:2 | 2 | 1 | DHW lower THW5B at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 561 | 2 | DONE:2 | 2 | 1 | Zone 1 supply THW6 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 562 | 2 | DONE:2 | 2 | 1 | Zone 1 return THW7 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 563 | 2 | DONE:2 | 2 | 1 | Zone 2 supply THW8 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 564 | 2 | DONE:2 | 2 | 1 | Zone 2 return THW9 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 565 | 2 | DONE:2 | 2 | 1 | Boiler supply THWB1 at fault; degC; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 567 | 2 | DONE:2 | 2 | 1 | Fault thermistor identifier; status; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 568 | 2 | DONE:2 | 2 | 1 | Mixing valve command at fault; step 0-10; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 569 | 2 | DONE:2 | 2 | 1 | Fault flow-switch identifier; status; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |
| A3 service | 571 | 2 | DONE:2 | 2 | 1 | Primary water flow at fault; L/min; historical; OCH722A p32 | Valid reply; interpretation not established by this scan |

## Communication quality

Observed CN105 parser-error counter values: [0]; UART-error counter values: [0]. Maximum compressor-telemetry age observed at before/after health checks: 6 seconds; this is not a continuous measurement of the exclusive transaction's internal gap. Health checks are not a comprehensive vendor fault decoder.
