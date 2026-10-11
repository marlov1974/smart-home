# P0084 changelog

- Resolved repository synchronization first: retained all five upstream commits and published completed P83 as57479e79f6361d5c6482b80cfdcf1e86c549e92f. Only generated file-index overlap required reconciliation. P83 results stayed unchanged duringP84.
- Established documented CN22 wiring and traced CN105 to UART2 interrupt/buffer handling.
- Traced a separate bit-oriented D-path to shared service and mode controls; retained explicit uncertainty about its physical connector.
- Found A3 selector filtering, service arbitration and session-gated staged pump-level writes.
- Added capability matrix, reproducible compact evidence, targeted switch helper and verification.
- Updated REPOSITORY_FILES.md, function catalog and reusable knowhow.
- No device calls, bus injection, firmware build/flash, settings changes or physical observations. Vendor images/full listings remain private.
- Result PARTIAL; complete display parity NOT ESTABLISHED.
