# P0071 — Geodan brine r1

Experimental candidate for operator flashing. Extends hardware-verified P0070 with read-only A3 service27/28. **No physical P0071 test or completed brine response has been captured yet.** Synthetic test temperatures are not pump measurements.

Flash `procon-brine.bin` through the same vendor updater procedure as P0070. File98304bytes/96KiB, base0x08008000, FF through0x0801FFFF. Bootloader region excluded; physical bootloader implementation remains unverified. Keep the immutable original and P0070 BIN for recovery. Restore DIP/RS485/normal power as before. See../../docs/RECOVERY.md. No mass erase, SET commands, pump controls, persistent writes or changes to device settings.

Preserved: input0=888, PC12 heartbeat, slave1/96008N1, CN105 USART1/24008E1, compressor input2/validity3 and all P0070 address meanings. Build marker input1 now71. **Read at most16 registers per request.** New map extends to raw input67; see../../docs/BRINE.md. The release has no original-Procon H-register compatibility claim.

Service27 then28,1s minimum retries,10 attempts maximum per service,20s pause after both; GET04 remains priority at2s cadence. Exclusive transaction owner prevents overlapping requests;800ms reply deadline,1s TX queue deadline,10s link loss recovery. Samples expire60s after completion. Full16-byte completed payload retained independently for each service, including after stale/error, until a newer completion or reboot.

Reference parser supports signed little-endian16-bit payload4/5 with no scaling; candidate temperatures are **experimental whole degrees**, not hardware-correlated. Completion statuses1/2 are accepted;0 remains pending; other statuses terminate without a value. Missing data must not be read as0C. Input43=1 explicitly means reference-only evidence. Compare real completed service27/28 values with Mitsubishi display before using temperatures as confirmed.

Hardware procedure: operator flashes, confirms heartbeat, then captures read-only blocks and physical service display027/028. Optional operator tool: `python3 procon/tools/read_brine.py --output /tmp/p0071-live.jsonl --samples 60 --interval 1`. It performs only FC04 reads, saves timestamps/raw values and brackets payloads with completion counts. Frames labelled reconstructed are rebuilt from retained payloads, not direct wire capture. No live invocation was performed during build. See../../docs/BRINE.md for success/recovery criteria. At most3 physical debug attempts before reassessment.

Software checks: GCC warnings-as-errors; ASan/UBSan Modbus+CN105 suites; repeated65s service-cycle simulations including millis wrap;12 actual-ELF ARM cases with simultaneous UART traffic; deterministic rebuild; vector/flash/RAM/FF bounds; immutable original/prior releases unchanged. Binary5312code bytes, BSS500, same16KiB flash-code/RAM bounds; package96KiB.

SHA256: `dab6f29a694ddade4c87d967451c7be476fc1a300cebee45a5f335905a51e3ca`.
