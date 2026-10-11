# P0087 function design

Only new tools/ftc6/p87 code: local analysis wrapper and evidence verifier (pinned inputs/operands and repeat exports); model.py (verified target, demand/thermostat and actuator transitions with explicit unresolved dependencies); scenarios.py (deterministic prescribed trajectories and UNKNOWN specifications); historical.py (offline timestamp/quality-aware summaries of existing private records); tests for identity, integer arithmetic, boundaries, transitions and absence of transport. Exact modeled functions and evidence bindings will be added as they are qualified, before implementing their equations.

Reports, compact evidence tables, relevant catalog/knowhow, package status and generated index may change. P86 helpers are reused read-only. Production EFFECT, control, telemetry, BL2 and settings tooling remain unchanged.

Implemented: `model.evaluate/lookup/temperature_byte/error_byte/pump_step/TimerWord/water_balance_delta`; `scenarios.scenarios`; `replay.replay` (the planned historical.py responsibility); `verify_local.derive/verify`; `run_analysis.py`. Thermostat/peerHz remain UNKNOWN rather than an invented transition implementation. `evidence.json` binds source chains; `extraction-verification.json` records checked operands/table and deterministic export hashes. The final model is narrower than the initial design ambition, as documented in findings.

## Continued investigation

Continuation planned functions: profile/request selector, native state transitions, timer update and expanded replay once semantics are qualified. Inputs include real control state rather than assumed event intervals; outputs retain unknown peer fields. No production functions change.

ROM differential validation: add a package-local Ghidra EmulatorHelper harness invoking original functions with controlled RAM and a return sentinel. Compare complete routine results/state against Python transcriptions, including history sequences and encoded output. This tests more than the earlier selected-opcode checks. Any CPU-language discrepancy blocks the affected claim until resolved; original binary is never modified on disk or on a device.

Continuation implemented: `native_state.NativeClock/TimerDescriptor/timer_event/History70/History50/FixedFlowLimits/heating_limit/final_limit/limit_code`; original-ROM execution in `P87RoutineProof.java`; full-vector comparison in `compare_rom_proof.py`. See continuation.md and rom-proof.json. The earlier partial model and reports are retained as historical scope, not the full reconstruction goal.
