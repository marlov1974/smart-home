# P0082 image validation

PASS for file integrity, not board identity. `ftc6.mot` SHA-256 `e94f9d9369b5efb9d2af66209fb431fde6ed0a1690b9ce0960adbf5cdb53b0c3`; `ftc6.id` SHA-256 `f488249ce1e39e098e5862458773133155eb135dd7f2a7fbf64b38fdf70924c2`. Originals and derived binaries remain outside the repository.

11,283 S2 data records, one S0 and one S8. Every record length and checksum passes; no overlaps. S8 entry is zero, **not** a proven CPU reset address. 349,889 populated bytes in 191 sparse regions, covering 0x80000–0xFFFFF. 174,399 absent bytes must not be marked as code. 12,933 populated bytes are FF. The optional FF-filled local binary has SHA-256 `d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a`.

Independent parser and Ghidra MotorolaHexLoader agree on all 349,889 address-byte pairs: SHA-256 `2beabad902a617333229b35abf0236813f55e7db754bee4d16c2c50d5cfe63e5` (ascending address as four big-endian bytes, followed by one data byte). The initial unspecified loader selected Intel HEX and failed; explicit MotorolaHexLoader fixes this. No address relocation was applied.

Reset bytes at FFFFC are `40 55 0D 7F`: low 20-bit target D5540; fourth byte is not part of the PC. ID-file values match the fixed-vector high-byte locations and spell PACIC02; FFFFF is 7F. Do not infer permission to alter protection.

The beginning of the image is `20 01 00 00`. Service handlers 190/191 read these bytes, unlike P0081's observed 21.00. This is not proven to be the installed image.
