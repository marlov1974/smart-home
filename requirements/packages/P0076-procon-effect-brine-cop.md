# P0076 — Procon EFFECT and multi-unit Modbus addressing

## Status and authorization
Ordered for Codex implementation/design. **No long-duration brine tests or COP experiments in P0076**; those are moved to P0077. No physical flashing or uncontrolled actuation authorized by this document.

## Package order, scope and ownership
P0076 follows P0072 r3; independent of P0075 readback success. Two features:
- **F0076-A EFFECT**: regulate an individual heat pump's delivered heating kW through safe Zone1 flow-target adjustments.
- **F0076-B Modbus addressing / two Procons on one RS485 bus**: unique persistent addresses, discovery and independent control.

Standalone `marlov1974/procon-melcobems-mini-a1m` owns portable application source, tests and documentation; Smart Home owns package evidence and site integration. Both units have STM32L433 CPUs per operator inspection. VP1 and VP2 use a shared borehole/source. Do not infer independent brine circuits or identical heat meter boundaries.

## Existing baseline
P0072 r3 reports water-side estimated watts in MVP field i7, calculated from GET0C supply/return and GET14 primary flow: `W = trunc(flow_cL_min * delta_cC * 418 / 60000)`; source flow resolution is whole L/min and sample alignment matters. It is **not automatically verified delivered floor heat**: identify heating/DHW/hydraulic routing first. A3/27 and /28 provide provisional brine readings, with whole-degree source resolution. P0072 r3 FC16 holding offset300/count8 envelope v2 supports OFF/AUTO/FIXED_FLOW/DHW/TARGETS; existing modes and telemetry must remain backward-compatible. Physical evidence: supervised FIXED_FLOW38C, AUTO and lease expiry restoration; no persistent restoration after MCU reset/power loss (snapshot in RAM only). Current replacement firmware hardcodes Modbus slave 1 at 9600 8N1 and does not interpret DIP addressing.

## F0076-A — EFFECT feedback regulation

### Control interface
- New named `EFFECT` mode with target **delivered space-heating/floor kW**, explicit W scaling, validation and range/lease.
- Define an explicitly versioned backward-compatible Modbus write contract; existing FC16 holding offset300/count8 envelope v2 and OFF/AUTO/FIXED_FLOW/DHW/TARGETS must continue unchanged. Never repurpose a v2 mode code without versioning.
- Scope initial hardware validation to **one verified pump**, then review separate dual-unit coordination. Treat each pump's achievable target independently; a 18/24/27 kW target is not legal for one unit.
- No direct compressor Hz/pump-speed control; modulate the Zone1 flow target using existing SET/readback path approximately **once a minute**.

### Measurement and regulator
- Reuse existing field i7 and raw GET0C/GET14. Average genuinely new, valid distinct generations across multiple cycles; expose instantaneous, short and slow filtered W with windows, sample count and age. Do not smooth invalid/stale/asynchronous values into apparently valid regulation feedback.
- Phase machine: `START` (strong but limited initial response), `CAPTURE` (progressively soften as measured power approaches requested power, anticipate derivative), `HOLD` (deadband/hysteresis, few adjustments), plus `LIMITED`, `INVALID_FEEDBACK` and `RESTORING`.
- Bounded change in flow setpoint per control tick and bounded cumulative setpoint; conservative allowed native temperature range, dwell/minimum command interval, overshoot handling, no integral windup and no oscillation escalation.
- Distinguish target unattainable due to hydraulics/load, power/compressor limits, native inhibit, stale telemetry or temperature cap. Do not continue raising flow target solely because kW remains below goal.
- Verify readback after SET; never interrupt exclusive A3 operations. Preserve holiday/server/heating prohibit checks and native Mitsubishi safety. No pump overrides, fault resets or protection bypass.
- Snapshot original settings and retain exclusive lease, verified AUTO/expiry restore. A lost link, invalid heat measurement, aborted experiment or unexpected operating mode stops further increases and enters guarded restoration. Power-cycle/reset durability is unsolved and blocks unsupervised deployment until separately verified.
- Publish read-only Modbus diagnostics: target, instantaneous/filtered measured W, signed error, sample ages/quality, active phase, current flow target, last adjustment, Hz, limit reason, decision counts and restore status.

### Acceptance F0076-A
Pass offline tests first, including telemetry freshness, source generation uniqueness, zero flow, DHW transition, request limits, response delay, anti-windup, noisy/quantized measurements, native rejects, timeout and power-loss state reporting. Hardware gate: supervised low/medium reachable targets; no continuous tuning while reference measurements invalid; measured convergence and stability reported with actual bands (initial goal ±0.5–1 kW, not promised precision). Verify explicit AUTO and lease restoration; no claim of post-reset restoration without a proven persistent recovery solution.


## F0076-B — Individual RS485 Modbus addresses

### Desired operating model
- Support **two physically distinct Procon STM32L433 units on one half-duplex RS485 bus**, each with one unique Modbus RTU slave address (operator-configured candidate: VP1=1, VP2=2; actual mapping requires read-only identity proof before final assignment).
- Preserve current 9600 8N1 application serial configuration and existing UART/DE direction behavior until separately authorized otherwise; bootloader's 115200 profile is not part of this feature.
- Prefer the hardware DIP-address model **only if physically verified**; the original vendor DIP semantics do not prove replacement-firmware semantics. Otherwise specify a safe nonvolatile per-device configuration mechanism with verified persistence, bounds, wear protection and recovery, without arbitrary writes to the bootloader/EEPROM.
- Document whether address changes are sampled on cold boot, application reset or live; define deterministic effective address, valid range 1–247, reserved/broadcast address 0 behavior, precedence and invalid configuration fallback. Avoid assigning the same fallback address to two live units.
- Before joining devices on the same bus, verify their addresses **individually with the other slave isolated**. Reject duplicate address as a hard blocker; do not attempt discovery by writing broadcasts or issuing control commands. Maintain a stable mapping from device identity (physical VP, unique observable identity) to slave address; never infer identity solely from a returned 888 marker.
- Unaddressed and CRC-invalid Modbus frames must be silent; preserve the known FC04/FC16 exception and read-only restrictions per slave. No shared control lease or target between devices; diagnostics and sequence ownership stay local to each device.
- With both attached, poll interleaved FC04 on both addresses; verify no collisions, overlap, stale cross-device data or bus starvation while each device continues its independent CN105 FAST/A3 service. Ensure RS485 is a single-master bus, with validated termination/bias and line lengths. A Shelly Modbus master must be configured to address both slaves correctly.
- Any controller issuing EFFECT/FC16 must target exactly one slave address; forbid broadcast control; maintain independent desired-state, sequence numbers, lease tracking, recovery logs and backup of original native settings for VP1/VP2.
- Expose read-only identity/address/config-source and diagnostics per unit; report a mismatch between requested and observed address as an error, not a success.
- Include a setup guide for isolated initial provisioning, sequential join, dual polling, independent control and rollback/recovery. Do not overwrite the previous running image on two units simultaneously before one-unit validation.

### Acceptance F0076-B
1. Offline tests prove separate slave1/slave2 behavior, correct silence/CRC handling, addressed FC04 and FC16, broadcast refusal, persistence/restart semantics and invalid/duplicate-address detection strategy.
2. On real hardware, each unit can be read individually; after joining, both can be read on one bus over extended intervals, with unique recorded device identity and successful CN105 telemetry per unit.
3. Existing slave1-only installs continue behaving as before when left unconfigured.
4. One pump's setting, telemetry, command sequence, lease and restore cannot alter or masquerade as the other pump's.
5. A failed provisioning/join can be rolled back without uncontrolled writes or resetting the heat pump.

## Safety, scope, handoff
Preserve existing native Mitsubishi inhibit/holiday/server protection, A3 exclusive retries, readback and lease semantics. EFFECT must not force brine/primary pump speed, compressor Hz, native-protection bypass or fault reset. Loss of fresh process feedback must stop new upward setpoint changes. RAM-only restore after reset remains a deployment blocker for unattended control; document a separately verified recovery mechanism rather than claiming one.

No scripted multi-hour staircase, borehole recovery, COP comparison or 18–27 kW combined dispatch in P0076. All such test sequences and electrical/thermal metering specifications are in **P0077**. Designing per-unit EFFECT and safe shared-bus communications is not permission to run P0077.

## Implementation process and deliverables
Codex follows normal bootstrap/review/design/functions gates, and creates `requirements/package-runs/P0076/review.md`, `design.md`, `functions.md`, attempts/verification/CHANGELOG with real code/test evidence. Inspect P0072 r3 `CHANGELOG`, `procon/docs/MVP_API.md`, `CONTROL_API.md`, UART and DIP evidence. Implement deterministic native/ARM/mock tests before live integration; no flash or active heat control without a separate operator handoff. At most three supervised hardware-debug attempts per reviewed validation round. Include test vectors for different addresses, DIP/config change on reboot, collisions, independent FC04/FC16, stale power and cross-unit state isolation. Update source/deploy artifacts and function catalog only within scope; synchronize REPOSITORY_FILES.md for file changes, and keep private logs/vendor binaries out of public standalone exports.

**Codex completion condition**: EFFECT and addressing features implemented/tested offline with explicit unverified hardware stages; follow-up operator approval needed before physical provisioning or control. P0077 begins only after its stated blockers are cleared.
