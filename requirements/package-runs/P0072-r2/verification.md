# Verification — P0072 r2

2026-10-07. Software PASS; physical controls pending. No device writes, no flash, hardware attempts 0/3. Review status WARN remains because power-loss recovery is not implemented and SETs are not yet physically validated.

- Native ASan/UBSan Modbus, scheduler, telemetry and control suites passed. Control cases include bounds, exact sequencing, duplicate idempotence, renewal, snapshots, modes, AUTO, lease expiry/wrap, lost ACK, mismatched/wrong replies, restoration failure retaining baseline followed by successful retry, and reset limitations.
- Python read helper: 5 tests passed; offline command encoder: 3 passed.
- Actual compiled ELF Unicorn: 14 cases passed (13 telemetry/scheduler cases plus FC16 FIXED38 then AUTO). Integration observed applied state [4,1,1], restored [0,2,2], original mode2/flow2950 restored, four SETs, continued service27/28 and no flash writes. Simulated CN105 responses do not establish hardware correctness.
- ARM test correction: retry cadence now measured from first transmitted wire byte. Last-byte measurements previously varied with serialized Modbus work and falsely failed the cadence assertion; firmware cadence was not changed to accommodate this test.
- Deterministic BIN rebuild: 98304 bytes, SHA256 a6b9d82f3b8fceafeaca2fcc1ac7100b48dd7bfe2a80d554dd3583c434933d90. Image/vector/bounds/FF-padding checks passed. Final comment-only firmware change retained that same BIN hash.

Build: `make -C procon all TOOLCHAIN=<toolchain> PYTHON=<venv-python>`; native build executables host-test, cn-test, tele-test, control-test; Python tests/test_read_mvp.py, tests/test_control_command.py, tests/test_arm.py build/procon-mvp.elf. Exact firmware source hashes accompany this report. Release README lists operating restrictions and recovery.

Still pending: supervised physical SET/readback/AUTO/lease test after operator flash; durable power-failure recovery design. Do not mark all P0072 hardware/failsafe requirements complete.
