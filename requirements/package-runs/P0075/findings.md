# P0075 findings — partial, 2026-10-07

Physical bootloader discovery works through Shelly UART0 at 115200 8N1. The reported maximum-flash field is 225280, EEPROM 255, erase block 2048 and write page 8192 bytes. These fields establish neither flash-read support nor CPU density.

Four bounded series tested **64 distinct read-candidate packets**, covering four length/address layouts, four trailers, absolute and relative/alias addresses, zero-filled length-associated envelopes, multiple counts and field padding. Every read candidate yielded **zero bytes**, including no 0x77 or 0x76 ACK. All **77 standalone discovery checks** across those series and eight parser controls succeeded. The controls produced four additional discovery replies. Exact packet catalog and accounting belong in standalone [firmware-readback-experiments.md](https://github.com/marlov1974/procon-melcobems-mini-a1m/blob/main/docs/firmware-readback-experiments.md); earlier one-shot and zero probes are outside those counts.

Parser controls are consistent with first-byte/receive-group dispatch. This is an inference, not a decoded implementation. A valid 5A response after a silent request proves liveness, not complete parser reset. Possible causes remain unsupported/disabled 0x57, untested framing/address/timing/session requirements or a transport limitation affecting very short responses. No evidence selects one explanation conclusively. More small header permutations are unlikely to resolve that uncertainty efficiently.

The supplied update archive contains the host program and an application image, not the resident bootloader. Public-source and artifact research did not reveal an implemented read request. Unused enum constants are insufficient to reconstruct the device-side contract.

The expected installed reference is immutable P0072 r3, 98304 bytes at 0x08008000, raw code length 11320, SHA256 `f0d33dab1a181d133bc1d5b9c5501ceb1952e71b798d93514a6bf9a1932a2fde`. Before maintenance, input68–71 were 3/1/3/0. The standalone application's r1 image is a separate artifact and must not replace this comparison reference. No capture files were manufactured, no firmware bytes read, and no whole-image comparison performed.

**Current result: BLOCKED_READ_PROTOCOL. Normal communication restored and verified, with a documented Shelly cleanup restart anomaly.**

After the operator confirmed normal DIP10000110 and a Procon-only restart, a fixed read-only Modbus FC04 request through raw UART at9600 8N1 returned13bytes with valid CRC16 and identity3/1/3/0. Eight transmitted bytes included NULs and the request checksum. This establishes that known binary request at9600; it does not qualify115200 short-ACK timing or all256byte values. Exact original Shelly Serial configuration was restored and an approved required reboot performed. The original seven script id/name/enable/running states were verified. Telemetry generations183 and188 advanced86→100; Procon identity remained3/1/3/0 and both Shelly outputs werefalse.

Removing the stopped temporary slot8 after that reboot caused a connection reset and another unexpected Shelly restart (observed uptime160→24). Slot8 was nevertheless removed. Serial, identity, script list and outputs were verified again afterward. No retry of deletion occurred. This extends the earlier cleanup anomaly: a reboot before deletion did not prevent it. Future sessions should retain a stopped/disabled slot and review removal separately. Final normal communication is restored; the firmware-read result remains BLOCKED_READ_PROTOCOL, with no dump or hash comparison.

Next discriminating evidence is passive RS485 wire capture or a demonstrated vendor read contract. A future diagnostic application would require a separate firmware package and physical flash; it would replace the current target and cannot retroactively prove the pre-flash image.


Knowhow promotion was considered and intentionally kept package-local: the UART handle, mode spelling, reboot requirement and delete anomaly are device/profile-specific. No unsupported global Shelly rule was added. The durable function catalog links the bounded tooling and the current limits.
