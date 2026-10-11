# P0087 — FTC6 flow-temperature control: compressor, pumps and time

## Execution handoff — 2026-10-11

Authorized offline work completed with a partial native reconstruction. See [P0087 findings](../package-runs/P0087/findings.md) and verification.json. Tracks A–D remain PARTIAL; E passes for the explicitly bounded model and tests. Physical testing NOT RUN; EFFECT unchanged. Original order and acceptance requirements follow.

## Status, order and authorization
**Ordered next package for Codex, after P0086.** The operator reports that Codex is currently executing P0086. Do not interrupt that run, extend its scope, edit its requirements/results, or reuse a live Ghidra project concurrently. Prepare this independent package now; execute it in a separate package context after the P0086 handoff. Read its committed findings when available and reuse relevant clock/decoder evidence rather than repeating the work.

Primary objective: reconstruct how Mitsubishi FTC converts requested flow temperature, measured flow/return temperatures and their time history into heat demand, compressor requests, pump operation and start/stop decisions. This is an investigation of the **native L1 control system**, not a redesign of it or an instruction to retune production EFFECT.

Authorized completion level: **offline analysis, package-local modeling/tests, documentation and commit/push of verified scoped results only**. No device access, new live captures/GET/SET, firmware deployment, equipment starts/stops, pump-level changes, settings/DIP changes, port moves or protection changes are authorized. Historical private traces may be analyzed locally. Later physical verification is a proposed handoff, not an automatic step of this package.

Use FTC **20.01 as the principal working reference**. Obtaining 21.00 is useful, not a general prerequisite. Distinguish externally stable command hypotheses from internal addresses and algorithm constants; never treat 20.01 RAM addresses as verified on installed 21.00.

## Operator questions and intended result
The operator wants concrete answers to:

1. With actual flow temperature below its setpoint, what makes the compressor increase output, by how much, and when?
2. Is the temperature error mapped to an absolute demand, integrated heat deficit, repeated demand increments, a rate-limited request, PID-like control, a lookup/state machine, or a combination?
3. Does identical current temperature error produce different actions after different histories? Which internal state retains that history?
4. What happens when actual temperature reaches or passes the setpoint: modulation down, minimum-capacity operation, a timed condition, or thermostat-off? What allows restart?
5. How do the water pump, brine pump, compressor request, three-way valve and auxiliary heaters coordinate before, during and after heating/DHW operation?
6. Which delays are sensor/filter delay, periodic control updates, communication delay, compressor/refrigerant-controller limits, minimum run/off times or normal scheduling?
7. How should Procon's EFFECT controller use the native loop without repeatedly exciting an internal accumulator or unintentionally losing compressor operation near a 6 kW target?

Deliver an evidence-backed **control model, timer/threshold catalog and actuator state machine**. A list of new addresses, generic PI/PID advice, or a plausible fitted curve alone does not answer these questions.

## Starting context and minimum relevant inputs
Follow AGENTS.md synchronization and package-bootstrap rules. Read the repository index for relevant paths, not all unrelated source or logs. Reuse:

- `requirements/packages/P0078-geodan-ftc-system-identification.md`: earlier direct/integral/ramp/hybrid hypotheses and the unwanted-stop scenario. This is a requirements reference, not proof that its experiments ran. Find actual results only where they exist; do not recreate historical tests as new physical work.
- P0076 EFFECT requirements and the current modular `procon/modular/firmware/src/effect.c`, `effect_feedback.c`, `control.c` and telemetry/API documentation, only to establish the current L2 inputs/actions and identify implications. These files are read-only in P0087.
- P0081 `CHANGELOG.md`, `implementation-report.md`, `command-map.md` and existing private captures where available; distinguish acquisition timestamps, stale cache samples and true device updates.
- P0083 `CHANGELOG.md`, `service-trace.md`, `pump-control-trace.md`, `energy-trace.md`, `decoder-validation.md`, `provenance.md` and compact address evidence.
- P0084 `settings-trace.md`, `screen-cn22-trace.md`; P0085 `protocol-matrix.md`, `access-gates.md`, `verification.json`; completed P0086 clock, mode, decoder and settings findings when available.
- Project Geodan service/installation manuals, especially heating control modes, Heat pump thermo diff. adjust, Pump speed, Water flow control, pump economy/cycles, DHW arbitration and actual protections. Use the applicable model's manual; do not import MHI, NIBE, another Ecodan generation or generic defaults as facts about this Geodan.
- Existing local Ghidra/M16C environment, original MOT/ID and verified derived binary. The P0085 binary SHA-256 is `d828c2e18a013a6adea8a191448b5c5f7d52ac17b3bbc1182c977e190b60976a`. Pin exact image, tool/module revision and analysis scripts.

### Useful established leads, not substitutes for tracing
All addresses here are hexadecimal in the analyzed 20.01 image:

- P0083 identifies measured water temperatures at `0662`/`0664`, flow at `322E`, and the separation of measured heat calculation from heat-control demand. Trace writers/filters and consumers, not just telemetry packers.
- P0084 traces ordinary SET32 temperature/mode handling, including mode assignments through `BBE92` to `3913/3914`. Trace the **flow-target** field specifically; DHW target `3906` is not automatically the heating-flow target.
- P0083: `AF400` selects stored water-pump steps `0770` or `07E6`, writes `3A33`; `B1AF0` maps steps to PWM, `B1B9C` writes the timer, GET15 reports requested PWM/run/feedback. The missing question here is **who requests pump operation and when**, not another discovery of SET65/79 staging.
- P0083: service17/18/19/27/28/52/54 are forwarded through another control path rather than computed by the local service dispatcher. Their physical source/controller and its algorithms must not be fabricated from the FTC image.
- P0084/P0085: UART2 CN105 and a distinct D-path have code evidence, but D's physical identity as CN22 versus another link is not established. Diagnostic-log fragments are not original wire frames.

## Track A — reconstruct the effective temperature target and feedback
Produce a signal/data-flow chain from external request or native mode to the actual regulator input:

`requested setpoint -> validation/mode selection -> effective target/filter/clamp -> measured/filtered feedback -> demand calculation -> transmitted request -> reported compressor response`.

For each variable record address, width, signedness, raw scale, physical unit if proven, initialization, update event, writers/readers and observable GET/A3 counterpart where known.

Distinguish at least: requested vs accepted/readback vs effective internal flow target; raw sensor vs calibrated/filtered water temperature; return temperature; water flow; DHW target; room/curve-derived target; heating mode vs actual operating phase; thermal W vs electrical W vs demand level vs compressor Hz. Do not infer a command's unit from a similar-looking telemetry value.

Analyze **fixed-flow heating first**, because EFFECT uses it. Then identify which portions are shared or different for weather-compensation heating, room-temperature control and DHW. Determine whether a new CN105 setpoint is applied immediately, sampled on a later tick, quantized, filtered/rate-limited or deferred by mode/priority. Follow the relevant comparisons to establish the actual error sign, thresholds and clamping order. Determine whether repeated identical setpoints refresh any timer or reset any internal state.

## Track B — identify the running compressor-demand law
Trace from the verified effective temperature error to its downstream output. Work backward from request serialization as well as forward from the sensor/target consumers, to avoid confusing energy accounting, GUI averages or error-history buffers with a control integrator.

Answer from instructions and state updates whether the algorithm uses:

- Direct error-to-demand, error bands/lookup tables, a persistent error sum, error derivative/trend, incremental demand changes, time-qualified bands, low-pass filters or ramp limits.
- Absolute demand versus change in demand versus a rate request; preserve the distinction between integrating temperature error and limiting the rate of an otherwise direct controller. An incrementing variable alone is not proof of degree-minutes.
- Fixed versus elapsed-time-scaled updates, rounding/deadband, saturation, lower/upper limits, anti-windup/freeze/decay, and reset or transfer of state at start, stop, target changes and heating/DHW transitions.
- Startup demand/boost and transition to normal running; minimum stable operation, maximum request and limit feedback.

Where supported, express a discrete update as `x[k+1] = f(x[k], effective_target, measured_values, mode, dt)` and its output as `u[k] = g(...)`. Every coefficient, state update, clamp and branch order must link to evidence. Unknown terms stay named unknowns. Do not label the result P/PI/PID/degree-minutes merely because it resembles one at a high level.

### Controller ownership is a required result
Determine what FTC itself sends to the refrigerant/inverter controller: temperature target, demand level, frequency request, operation/permission flags or another quantity. Identify transmitted fields and readback separately. If actual Hz regulation or brine-pump control belongs to another processor whose firmware is absent, document the boundary and the strongest observable contract. Still complete the FTC-side model; do not require missing source-board firmware before delivering it or invent that board's protections/algorithm.

## Track C — time, hysteresis, start/stop and state memory
Build a timer/threshold catalog and state diagram using actual predicates. Include only states substantiated by the image, with provisional names clearly labeled. Cover:

- OFF/standby, circulation before compressor start, start eligibility, startup, normal modulation, minimum-capacity operation, thermostat-off, pump overrun and restart eligibility.
- Temperature-only versus temperature-plus-duration stop/restart conditions, separate upper/lower thresholds, minimum run time, minimum off time, restart counters and exceptions actually found.
- Heating/DHW changeover, compressor continuity versus required stop, three-way-valve lead/settling delays, post-DHW return to heating, native priority/time limits, auxiliary-heater delay, and communication/fault/flow-related interlocks as they affect this sequence.
- What happens to accumulated error, demand, ramp state and timers during temporary permission changes, natural stops, mode changes and controller reboot; do not conflate a Procon lease timeout with a Mitsubishi timer.

Each catalog row must give: source address/predicate; raw threshold; units/timebase derivation; update cadence; triggering event; whether it pauses/resets/reloads; comparison direction and equality behavior; mode dependence; configurable menu field/default or fixed constant; which controller owns it; confidence. Trace hardware clock/interrupt through scheduler/prescaler/callback before translating counts to seconds. A constant60 or3600 alone is not a minute/hour proof. Differentiate wall clock/calendar scheduling from monotonic control timing.

Determine whether factory parameter **Heat pump thermo diff. adjust** changes thermostat switching only or also the running demand law. Do not transfer room-control-only settings into fixed-flow operation without branch evidence. Separate safety protections from configurable comfort/efficiency behavior where known, but propose no disabling or bypassing of either. Prior chat examples of 10-minute or60-minute restart waits are questions, not established constants.

## Track D — pump and auxiliary-actuator coordination
Start from the existing water-pump request/step/PWM chain and trace its upstream request state. Determine how heating/DHW stored steps, startup/overrun, measured flow, temperature difference, Water flow control ON/OFF, and special/test/freeze conditions interact. Establish whether FTC maintains a fixed selected level, adjusts it dynamically, or uses mode-dependent rules; equal measured flow is not proof of constant speed.

Treat primary water pump, brine pump, optional zone pumps, DHW sanitary pump, three-way valve and booster/immersion heaters as distinct actuators. Identify ownership and actual implemented dependencies rather than assuming they all follow compressor Hz. For brine and compressor-side controls, expose the external-board boundary when reached. Do not invent an independent setting for an actuator that the firmware only enables/disables.

Deliver a timing/coordination table: initiating condition -> FTC request -> actuator/other-controller acknowledgment or observation -> next eligible action -> timeout/stop path. Prioritize primary water pump and compressor; cover other actuators where they affect the same control cycle, without expanding into a complete reverse engineering of every FTC feature.

P0086 owns the SETC8 settings transaction and pump-level write qualification. P0087 consumes those results, but does not change its tooling or execute/write new settings.

## Track E — executable evidence and implications for EFFECT
Build package-local Python model/trace-replay tools under `tools/ftc6/p87/`. Default operation must be fully offline with zero serial/network side effects. Model verified portions of native regulation and state transitions; do not claim full machine emulation from a partial control-law transcription. Add an evidence ledger linking model terms, constants and test expectations to ROM instructions, manual requirements or historical observations.

Use prescribed sensor trajectories to test the controller itself. A separate thermal-plant approximation may be used only if explicitly labeled as an assumed simulation model; do not make its response a claim about the actual borehole, floor or compressor. Reuse available historical logs with their real timestamps and completeness; record missing traces, do not ask for them before attempting code-only work.

### Required scenarios
1. Fixed-flow heating with a positive target step while running; show requested/effective target, feedback, internal memory, demand and state over time. Compare the same instantaneous error after different prior error histories with other modeled conditions controlled.
2. Constant nonzero error, then zero error, then reversed error: distinguish accumulation, direct mapping, incremental demand/ramp and decay. Repeat from minimum and maximum demand to expose saturation/windup behavior.
3. Actual flow just below, equal to and above the setpoint, for short and sustained durations; identify the exact modulation-versus-stop branch and its restart conditions. Test timer boundaries just before/at/after the threshold and reset events.
4. Fast versus slow upward changes of the external setpoint during a synthetic startup/capture trajectory. Address the operator's failure case: heat target6kW but actual flow reaches a native stop condition before the slow external setpoint adjustment has established continuous operation. Thermal target6kW is **not** assumed to be a Mitsubishi native demand unit.
5. Repeated unchanged setpoints versus fewer larger updates; quantify any difference caused by sampling phase, filtering, integrator resets or communication acceptance. Do not substitute Procon polling frequency for native regulator cadence.
6. Pump level/flow variation and rising return temperature at otherwise comparable conditions. A water-side balance may be used to construct the6kW/15L-min example, but desired measured flow temperature is not automatically the correct commanded setpoint.
7. Heating -> DHW -> heating and a natural stop/restart: show which internal states persist, reset or transfer, including pump/valve sequencing where known.
8. Unknown/limited other-controller response, minimum-capacity limits, invalid/stale sensor feedback and relevant communication/flow failures. The model must mark unimplemented boundaries, not silently substitute a safe value or infer actualHz.

For scenarios whose underlying firmware path is unresolved, deliver a discriminating test specification and an explicit UNKNOWN result rather than generating authoritative-looking curves. Separate evidence-transcription tests from independent validation: synthetic tests of your own model do not prove physical behavior. Where historical data allows comparison, report latency, demand/Hz errors, start/stop prediction and confounders including source temperature, actual flow, other VP activity and sensor-update lag; do not overfit two snapshots.

### Required practical conclusion for Procon
Produce an EFFECT interaction note that answers:

- Is external flow target acting primarily as an absolute-demand influence, a sustained accumulated-error influence, or a hybrid, and in which state/mode?
- Which minimum observation/command intervals and startup/capture/hold distinctions follow from the identified time constants, without inventing numeric tuning values?
- What observations predict a **normal avoidable thermostat stop**, and when is continued operation physically/native-limited so an external controller should accept the stop rather than increase target blindly?
- How to avoid competing integrators, delayed overreaction, stale-feedback tuning and misidentifying source-controller limitation as insufficient heat demand.
- Which existing telemetry can test this interpretation; which additional values need a separate diagnostic feature or source-board evidence. Distinguish locally readable variables from unknown external access.

This note is a future L2 design input. Do not modify/tune/install the current EFFECT controller under P0087 and do not guarantee the earlier requested no-overshoot15-minute6kW response from static analysis alone.

## Evidence, reproducibility and acceptance
Every claimed chain must include image/tool provenance, relevant caller/callee, instructions/operands and data writers/readers; use **CONFIRMED STATIC / CORROBORATED BY EXISTING TRACE / STRONG HYPOTHESIS / UNKNOWN**. Preserve original data and register scales; qualify problematic M16C operands/p-code through targeted instruction tests or documented corrections. Reuse validated decoder work; no unsupported decompiler semantics become equations.

Required outputs are a connected flow-target-to-demand trace, ownership boundary, timer catalog with units or explicitly raw ticks, pump/compressor state model, reproducible offline scenarios and the EFFECT note. Report per-track **PASS / PARTIAL / BLOCKED**, with physical testing **NOT RUN**. PASS means evidence-backed outputs, not that every internal/external algorithm was recovered. A limited source-controller boundary should not erase verified FTC results or stop independent tracks. A wrong image/invalid critical opcode blocks only the affected claim until corrected.

Run input/profile and decoder-evidence checks, model tests, boundary/rounding/saturation tests, and repeat targeted extraction on two independent analysis copies with deterministic output/hash checks. Provide runnable commands in `reproduce.md`, including `python3 -m unittest discover -s tools/ftc6/p87/tests -v` (or the justified chosen runner), `python3 -m compileall -q tools/ftc6/p87` and `git diff --check`. Do not predeclare results. No unbounded fuzzing or live tests.

## Files, handoff and repository hygiene
Allowed changes: new `tools/ftc6/p87/` analysis/model/tests; `requirements/package-runs/P0087/` reports; minimal declared shared offline helper changes only after P0086 handoff with regression evidence; relevant function-catalog/knowhow summaries, this package, bootstrap manifest and generated file index. Forbidden: P0086 scope/results rewrites, production Procon/Shelly/HA logic or deployments, G1, unrelated cleanups, installed FTC data or firmware.

Create package-run `review.md`, `design.md`, `functions.md`, `provenance.md`, `flow-target-trace.md`, `demand-law.md`, `controller-boundary.md`, `timing-and-thresholds.md`, `actuator-state-machine.md`, `model-validation.md`, `effect-integration-guidance.md`, `physical-test-proposal.md`, `findings.md`, `open-questions.md`, `verification.json`, `reproduce.md` and `CHANGELOG.md`. Include compact machine-readable signal/timer/state/evidence tables and labeled synthetic or historical timelines where useful. Write review/design/function design before code; treat conflicting evidence as a documented correction in P0087, not hidden history rewriting.

Full vendor firmware and full disassembly/private operational logs stay local. Publish only scoped tooling, minimal substantiating excerpts, hashes and sanitized evidence. A proposed later physical test must name its hypothesis, exact observables, bounded perturbation, stop/restore criteria and missing prerequisites, but remains unexecuted.

On completion update the tracked file index/function catalog, consider knowhow promotion, verify scoped diff/tests before commit/push and report the commit, completed traces, actual tests, unresolved controller/timebase dependencies and the next smallest useful verification. Do not pause P0086 merely because P0087 has been registered.
