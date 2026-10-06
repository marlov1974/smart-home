# P0069 memory map

Original: 96,692 bytes mapped at0x08008000, exclusive end0x0801F9B4. Vector SP0x20010000, reset Thumb0x0800A341. Reset helper0x0800A330 explicitly writes VTOR0x08008000.

Inferred L433 family supports128/256KiB flash and64KiB SRAM (48KiB SRAM1 plus16KiB SRAM2). Exact fitted density/package unverified. M1 uses only16KiB flash [0x08008000,0x0800C000) and16KiB SRAM1 [0x20000000,0x20004000), with2KiB minimum stack reserve. It does not depend on SRAM2 aliasing.

Candidate: raw1704 bytes, padded2048 bytes (one2KiB page), address range[0x08008000,0x08008800). Stack0x20004000, reset0x0800818D. Code never unlocks/programs/erases flash. ELF checker rejects flash load segments below application base or outside conservative bounds.

[0x08000000,0x08008000) is the inferred resident bootloader reservation. Device-side bootloader is absent from supplied archive; its erase implementation has NOT been disassembled or independently verified. Existing vendor updater use and application VTOR support the boundary inference.

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.

P0070: M1 r2 now hardware-confirmed; next experimental build adds CN10524008E1 on PA9/10AF7 and read-only compressor telemetry. See `../releases/P0070-compressor-r1/README.md` and `CN105.md`. Same conservative flash/RAM/vector limits and96KiB FF envelope. Physical CN105 result pending. No setting writes or physical flash by Codex.

## P0071 brine candidate

Adds a separate read-only service27/28 state machine with exclusive CN105 transaction ownership, bounded retries and continued GET04 telemetry. Preserves P0070 registers0–15 (build marker71); adds16–67, with max16 registers per read. Raw completed payloads are retained per service; temperature candidates use reference-backed signed little-endian encoding and remain experimental. See [BRINE.md](BRINE.md) and `../releases/P0071-brine-r1/README.md`. Software tests pass; no P0071 hardware readings or physical flash yet. Previous P0070 hardware result remains valid historical evidence.
