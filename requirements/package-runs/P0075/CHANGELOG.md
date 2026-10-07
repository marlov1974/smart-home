# P0075 changelog

Partial readback tooling and research, 2026-10-07. Physical discovery works, but the read protocol remains unresolved and no application bytes were extracted. Hardware PASS is not claimed. Normal operation was restored and verified after the operator handoff.

- Standalone: offline decoder/capture/comparator, authenticated bounded discovery and experimental Shelly adapters, a private-output host runner, failure/transport tests, exact experiment catalog and documentation. Existing firmware sources, immutable releases and licensing are unchanged.
- Smart Home: package authorization amendments, phase evidence, findings, hardware state, verification and focused function catalog. No G2 production runtime or Procon application change.
- Live: temporary Shelly Serial/maintenance-script changes and approved reboots, read-only bootloader discovery and bounded operator-authorized hypotheses. No erase, program, EEPROM, Modbus control or CN105 SET.
- Recovery: normal DIP/Serial/script states restored, identity and advancing telemetry verified. Removing the temporary script caused an unexpected Shelly restart even after the planned reboot; final normal state was checked again. No further deletion attempt.
- Both tracked-file indexes are updated in this change. Raw logs, snapshots, session tokens and firmware dumps are excluded.
- Knowhow promotion considered and intentionally skipped globally; profile-specific lessons remain in package evidence and standalone documentation.

See verification.md for offline checks and findings.md for remaining uncertainty.

## Subsequent operator-authorized write reference

Added bounded documented0x53 controls and0x50 comparisons before returning to three fixed0x57 hypotheses. All seven0x53 transmissions returned72, including one correct-format FF attempt; the long-gap negative control returned72 after19bytes before the tail. All three reads stayed silent and retained cached7A. No successful write, firmware dump or erase. The new evidence supersedes the earlier final normal-state claim for the current physical session: operator restoration is deferred until evening and the bridge is stopped/disabled. New adapter tests46+27 pass; both file indexes updated. Profile-specific knowhow remains in the package.

## Subsequent pure single-byte opcode survey

Completed the separately risk-authorized `00..FF` sweep: exactly one byte per trial, no helper UART traffic, 3000 ms window and 1700 ms response classification. All 256 transactions validated. Only `50`, `51`, `53` and `5A` responded; `51`/`53` returned negative ACKs at about 1.62 seconds. The silence of `47`/`57` and other opcodes is bounded evidence, not a proof of absent handlers.

Added the bounded sweep adapter, offline sanitizer/validator and full per-opcode map to standalone; coordinated design/results/function documentation here. Focused tests pass: 46 write-reference, 34 read/ACK, 12 sweep and 5 summary cases plus the prior suites. Current bridge stop/disabled state is verified; physical return to normal remains pending until the operator's evening handoff. Both file indexes are updated. No firmware source or G2 runtime changes; no global knowhow promotion for profile-specific hypotheses.

## Following paired-opcode request

The explicitly requested contiguous pairs `40 5A` and `57 5A` each returned zero bytes within three seconds. Four TX bytes in two separate transactions; no helper command. Recorded separately in the opcode report with passive/order/timing mock verification and final script stop/disable readback. This documentation update adds no tracked paths; the file indexes remain unchanged. No inference of read support or a unique `57` parameter wait.
