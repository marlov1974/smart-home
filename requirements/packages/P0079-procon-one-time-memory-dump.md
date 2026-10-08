# P0079 — Procon one-time read-only flash and EEPROM diagnostic firmware

## Status and scope
Ordered requirements package. Implementation, offline tests and candidate build are authorized. **No physical flash, memory-dump access or replacement of a running unit without a separate operator-approved handoff.** One-time engineering investigation, not a feature of ordinary MVP/EFFECT firmware.

## Objective
Build a minimal temporary STM32L433 Procon A1M application at the verified application base `0x08008000` which exposes strictly bounded read-only access to MCU flash and, once hardware is identified, external EEPROM. Use the existing Shelly-to-Procon Modbus RTU link at **9600 8N1** if compatible with the physical unit, avoiding Shelly UART mode changes. The Mac collects raw binary outputs, compares two independent reads, records metadata and restores the exact pre-test application build through the separately documented vendor updater process.

## Hard architectural boundaries
- This diagnostic **replaces the existing application while running**, so it cannot back up that original application before flashing it. Require an already-saved and hash-verified exact return BIN and known recovery workflow before altering hardware. Restoration requires an explicit, separate write operation using the supported updater; the diagnostic itself provides **no write, erase, unlock, option-byte, reset-protection or arbitrary memory poke** functionality.
- Resident bootloader reservation `0x08000000..0x08007FFF` is inferred for the investigated STM32 build and is not part of the application update envelope. Reading it may be possible, but cannot be guaranteed; readout protection, execute-only or bootloader policy may prohibit access. Never alter protection settings to gain access. An inaccessible region must result in `READ_BLOCKED`, not a fault/reboot loop or bogus FF/zero data.
- Tested application image envelope `0x08008000..0x0801FFFF`; no assumption that higher flash or entire installed capacity is accessible. Diagnose app range only after confirming memory bounds and application layout. The running diagnostic image changes the app bytes; do not claim these bytes represent the displaced prior firmware.
- An external 8-pin EEPROM is a candidate, **not a confirmed part or I2C pinout**. Identify actual IC marking, bus/power/MCU GPIO/I2C mapping, addressing, capacity, page semantics and any owner/bootloader use before enabling EEPROM probing. If these cannot be verified, keep EEPROM functionality unavailable; no speculative bus scans that could change other devices.
- No persistent diagnostic mode via DIP5 or special bootloader `0x57/0x59` requests. Existing vendor update-entry procedure with all DIP OFF stays separate. No changes to MCU boot reservation, EEPROM layout or production firmware just to support this probe.

## Read-only transport and command contract
- Prefer FC04 input-register access compatible with the current Shelly Modbus client (slave address verified before use; firmware currently uses slave 1). Provide a bounded *address-selector transaction* only if it can be demonstrably read-only at the hardware/memory level and cannot be confused with writable Modbus control registers. **Do not expose arbitrary address/length writes or allow a generic write tunnel.** An acceptable alternative is a fixed indexed window list covering specifically approved ranges, selected by input-register offsets.
- Explicitly whitelist supported ranges (boot flash, current app envelope, verified EEPROM). Unsupported/reserved/option-byte/OTP/system-memory/RAM ranges reject. No arbitrary memory mapping and no side effects from a read, except bounded local cursor/cache management.
- Target bounded payload windows initially 128–256 bytes, maximum 512 bytes when testing supports it; Modbus RTU FC04 has a maximum of 125 registers/250 data bytes per response, so window layout and chunk sizing must respect RTU PDU limits. Select a practical response size of at most 240 data bytes (120 registers) to leave margin for telemetry/metadata; verify real implementation and CRC16. Never attempt an 8192-byte Modbus response.
- Every returned block includes or is accompanied by logical memory area, offset, actual byte count, capture generation/sequence, validity/error status and optionally a CRC32 for *diagnostic data*, not a substitute for end-to-end comparison. Preserve all byte values and ordering; define odd-byte alignment and byte-to-register packing. No data returned for an invalid or ambiguous memory region.
- Mac reads sequential indexed windows, writes untouched bytes in exact offset order to private local files, detects gaps/repeats/stale cache, performs **two separately requested full reads** and compares byte-for-byte and SHA256. On mismatch provide bounded first-offset/range diagnostics and mark `UNSTABLE_READ`, never fabricate/repair values. Save no complete memory image in Shelly scripts, logs or KVS.
- Do not provide EEPROM write access, even to 'test' whether it works. A read-only I2C transaction may still have peripheral side effects; document and test bus ownership and be conservative around other addressable devices.

## Startup behavior and protection
- On diagnostic startup, keep CN105 control disabled, send **no Mitsubishi SET**, stop all application-specific power/effect control functionality, and expose explicit diagnostic identity/version. Do not assert that it is restoring original native FTC state after flashing: original P0072 r3 lease/snapshot are RAM-only and can be lost on reset. Before flashing, verify no active control lease and externally record native settings; restore or safely exit any active control session first.
- The normal Shelly RS485 master and any other pollers must be accounted for. No simultaneous masters; temporary diagnostic register map must not collide with production command meanings in a way that could trigger writes. Preserve known 9600 8N1 electrical UART/DE setup.
- Keep flash range bounds conservative, validate exact MCU flash density before reading beyond documented image envelope. Implement fault-safe reads: do not dereference unvalidated/inaccessible addresses causing hard faults. Never mass erase or erase option bytes.
- Log hardware-specific unknowns as unknown. Different board revisions may have different EEPROM topology; do not generalize one success to other A1M generations.

## Preflight and staged physical handoffs
1. Normal G2 bootstrap, consistency review (PASS/WARN/STOP), `requirements/package-runs/P0079/review.md`, `design.md`, `functions.md` before implementation. Inspect latest P0072 r3, P0074 boot/memory references, P0075 readback findings and current standalone clean-room source. Do not redo completed updater reverse engineering.
2. Offline build and test a deterministic 96 KiB application-envelope BIN, with no out-of-bounds executable/load sections and no firmware writer.
3. Prepare Mac dumper and fixtures; verify CRC, arbitrary bytes, window offsets/endian, source-range allowlist, every edge, repeated 1000-window reads, timeout/stale/gap/reorder handling and double-dump mismatch.
4. Baseline live *read-only* from running Procon: physical ID/MCU, live application release/version/hash reference, RS485 settings, normal telemetry, native FTC settings and absence of active lease. Check available recovery image and updater separate from diagnostic.
5. **STOP and ask operator approval before overwriting the application.** Operator alone controls DIP/power and uses approved updater. Capture actual diagnostic BIN SHA256, hardware identity and rollback image first.
6. After diagnostic boots: first verify diagnostic identity; test harmless bounded application flash reads, then reserved boot flash in narrow permitted segments, then EEPROM only after validated part/pin/bus/address evidence. Separate each type's success/blocked status.
7. Capture each permitted region twice to Mac, compare, save local raw BINs and per-region JSON manifests/SHA256; do not upload raw vendor bytes, bootloader binary, EEPROM contents or private IDs to a public repository.
8. **STOP for an explicit restoration handoff**; restore the exact pinned normal BIN via vendor updater with documented DIP procedure. Verify LED, FC04 identity, independent live CN105 counters, control capability and native settings. A progress bar alone is not a valid restoration proof. If updater entry fails, stop without improvising mass-erase/debug access.

## Test cases and acceptance
- TC1: diagnostic boots with no CN105 control, no FC16/FC06 writable commands and visible unique identity; bounded FC04.
- TC2: invalid/reserved/unaligned/overrun memory selection safely rejected without touching option bytes.
- TC3: complete binary fidelity including all 0x00..0xFF values, byte ordering, odd-length final window and deterministic CRC.
- TC4: two distinct read passes, gap/dup detection, device reset/missing reply/CRC error/timeout/partial capture never reported as successful image.
- TC5: candidate external EEPROM unsupported gracefully until confirmed, then correct range/size and double-read without writes; no assumption free EEPROM storage.
- TC6: memory pressures bounded on MCU, Shelly and Mac, no full-image allocation on Shelly.
- TC7: traceability: device, requested/actual ranges, sample timestamps, binaries and SHA256, unsupported regions, exact installed/restore BIN identities.
- TC8: normal firmware restored to prior known-good behavior under a separately authorized and supervised physical procedure.

A successful deliverable may be **partial**: one or more read ranges blocked by protection or absent EEPROM support. Never label blocked data as a valid dump. Report exactly what was read and what remains unknown.

## Files and evidence
Portable diagnostic firmware, tests, Mac readback helper and sanitized docs belong in `marlov1974/procon-melcobems-mini-a1m`, with the diagnostic excluded from normal production release/deploy paths. G2 package evidence under `requirements/package-runs/P0079/`; function catalog and tracked file index updated as needed. Raw vendor-containing memory captures, physical secrets and private logs remain exclusively on operator Mac. No unrelated Shelly/FTX/EFFECT functionality changes.

## Non-goals
No cloning uninstalled original application, no permanent service mode or DIP reassignment, no arbitrary debug command passthrough, no flash/EEPROM writes, no L1 protection changes, no 0x57/0x59 bootloader protocol completion, no physical high-load tests and no automatic cross-device deployments.
