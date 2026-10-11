# P0086 — memory load proof

Analytical **PASS for the reviewed instruction/range model**, physical **NOT RUN**. Applies only to supplied 20.01; full21.00 dump feasibility through another implementation UNKNOWN.

CONFIRMED: request contains a24-bit little-endian address.9E938 rejects address<0400 or address+length>0FFFFF. This is an exclusive-end check: last requested byte cannot be0FFFFF with positive length. Parser acceptance is not actual addressability.

At9E98B/9E98E the routine loads both address words, adds index usingADD/ADC, but9E997 copies onlyR0 toA0.9E99C bytes **72 6D 48 13** decode as `MOV.b [A0],0x1348[A1]`. It is not LDE, and R2 is not consumed by the memory load. Effective source is `(address+index)&FFFF`. M16C/60 software manual §2.3 printedpp24–25 explicitly limits[A0]/[A1] to00000..0FFFF. The repaired decoder, exact opcode check and8 instruction-emulator cases agree; this is not a whole-firmware emulator or physical protection test.

| Requested range | Parser | Effective access / tool policy |
|---|---|---|
|0000–03FF|Rejected directly|MMIO excluded; aliased high addresses are also blocked|
|0400–4FFF, bounded legalN|Accepted|Conservative candidate RAM, dry-run only; installed 21.00 address/content not qualified|
|5000–FFFF|Accepted if endfits|Near space, exact MCU map/reserved areas unknown; tool blocks|
|FFFF length2|Accepted|FFFF then0000; wraps intoMMIO, tool blocks|
|10000 /80000|Accepted|0000, not flash; tool blocks|
|80400|Accepted|0400; tool blocks alias|
|FFFFE length1|Accepted|FFFE, not upperflash; tool blocks|
|FFFFF length1|Rejected|Exclusive end exceedslimit|

Thus the reviewed route is **not a technically valid full programflash reader**. No bank switch or far-pointer load exists at the actual read instruction. Disabling protections would not fix this address truncation and is outside scope. No dump claimed or attempted. A different21.00 routine would require its own evidence/profile.

Normal0x52 through8ACFC uses packed14-bitaddress: firstbyte low7 bits, secondbytebit0→bit7 andbits1..6→bits8..13.0..FF remaps to0EE4+address;100..1FF to0AE4+(address-100);200..3FF is a two-entry key/pointer lookup at806A4;400..3FFF directnear. This offers plausible bounded diagnostics while staying8N2, but full normal frame exchange is not qualified by this package and is not executable. It is not a flash route.45/46 service loops were not implemented or activated.

Volatile RAM can change between reads; repeated differences are not corruption. The CLI tags each planned address and preserves raw replies/hashes. Stable flash comparisons/gap completion are deliberately unavailable because no qualified flash range exists. Candidate0400 in a dry-run is a codec test vector, not a justified expected21.00 byte value.
