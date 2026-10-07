# P0075 verification — 2026-10-07

## Offline verification

- Full standalone command: `make verify TOOLCHAIN=<existing-local-toolchain> PYTHON=<existing-local-venv-python>`: PASS. Native ASan/UBSan protocol/telemetry suites, read helper/catalog/platform checks, 13 actual-ELF ARM scenarios, image bounds and deterministic build verification all passed.
- The first sandboxed run stopped in the ARM emulator with Illegal instruction; the approved local run outside that sandbox passed. This was not a Procon result or device access.
- P0075 readback tests: 8 Python storage/comparison cases, 4 independent candidate/catalog cases and 13 injected host-runner cases. Seven JS suites cover 1000 bounded discovery transactions, HTTP adapter, fixed probes, zero probes, series replay/partial-send halt and 70 parser-control cases. Qualification cleanup has five fake-RPC tests, including seven injected failure phases. All tests are offline.
- Deterministic standalone r1 BIN remains SHA256 `f8823fab325018c31f093215cd72d19c6d28dd28082bcd64d83df82e88b3b4a9`; it is distinct from the pinned installed r3 reference. No firmware source or immutable release changed.
- Tracked-file publication scan and diff whitespace check pass. Both repository indexes match the tracked paths. Raw site records, generated credentials and vendor files are excluded.

## Physical evidence and limits

Discovery works, but all64 distinct series read candidates yielded zero bytes. See hardware-report.md and standalone exact experiment report. No application dump, hash comparison or backup exists. The refactored host and final partial-send/cleanup corrections have offline verification only; no claim of a later hardware rerun.

The operator subsequently confirmed normal DIP/restart. The normal-mode raw-UART read passed CRC and returned3/1/3/0; exact Serial/script-state restoration and advancing telemetry were verified. A post-reboot Script.Delete caused another unexpected Shelly restart, after which normal state was verified again. Readback remains BLOCKED_READ_PROTOCOL. Package hardware PASS is not claimed because no firmware dump exists. Final `make readback-test PYTHON=python3` passed after the partial-send and no-delete qualification fixes; full firmware regressions had already passed and firmware code was unchanged.
