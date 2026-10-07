# P0075 changelog

Partial readback tooling and research, 2026-10-07. Physical discovery works, but the read protocol remains unresolved and no application bytes were extracted. Hardware PASS is not claimed. Normal operation was restored and verified after the operator handoff.

- Standalone: offline decoder/capture/comparator, authenticated bounded discovery and experimental Shelly adapters, a private-output host runner, failure/transport tests, exact experiment catalog and documentation. Existing firmware sources, immutable releases and licensing are unchanged.
- Smart Home: package authorization amendments, phase evidence, findings, hardware state, verification and focused function catalog. No G2 production runtime or Procon application change.
- Live: temporary Shelly Serial/maintenance-script changes and approved reboots, read-only bootloader discovery and bounded operator-authorized hypotheses. No erase, program, EEPROM, Modbus control or CN105 SET.
- Recovery: normal DIP/Serial/script states restored, identity and advancing telemetry verified. Removing the temporary script caused an unexpected Shelly restart even after the planned reboot; final normal state was checked again. No further deletion attempt.
- Both tracked-file indexes are updated in this change. Raw logs, snapshots, session tokens and firmware dumps are excluded.
- Knowhow promotion considered and intentionally skipped globally; profile-specific lessons remain in package evidence and standalone documentation.

See verification.md for offline checks and findings.md for remaining uncertainty.
