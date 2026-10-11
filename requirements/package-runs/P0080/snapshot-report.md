# P0080 frozen telemetry follow-up

Built, offline verified; not flashed. User authorized build only. Snapshot behavior and caveats in procon/modular/README.md. FC04 raw400 capture,402 sequence check,408..527 frozen records. Legacy registers unchanged.

Dispatcher584/4096 bytes (RAM8/256), Drift2624/4096 (RAM616/2048). Two chunks required because original dispatcher blocked the new range. BL2/Common/Mode/Service/Debug chunks byte-identical to installed release. ABI/layout unchanged. OTA mask10,8192 padded firmware bytes,39 protocol frames (BEGIN,36WRITE,COMMIT,EXIT), maximum252 wire bytes. Original release retained as exact base.

Tests: nine native C suites with ASan/UBSan including new snapshot suite, existing Python reader/control/commission tests and new bounded snapshot reader tests; actual ARM snapshot freeze/stale/rollover/reset/routing checks; real resident OTA C against this exact old/new pair,1037 mutation cuts plus duplicate ACK/status/wrong UID/base/CRC/repair checks. All37 ARM baseline cases passed; result in release-snapshot/arm-regressions.log.

One frozen capture represents coherent cached values with their own age/status/generation, not simultaneous measurements. Concurrent readers replace it and require sequence retry. Snapshot data does not alter EFFECT's internal sampling or pump state. New host CLI assumes existing mb_client mode; current js_uart requires callback adapter. No live commands, commit or push in this follow-up.

Function catalog and repository index updated. Generic knowhow promotion intentionally skipped: capture-specific behavior documented in project docs; physical snapshot OTA remains unverified.
