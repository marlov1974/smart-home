# P0076 — EFFECT, brine step-response and COP comparison

## Status and authorization
Ordered requirements package; implementation may be prepared by Codex after normal package review/design/function-design gates. Creating this package does **not** authorize physical flashing, live actuation, unattended operation or a high-load field trial. Physical experiments require explicit supervised go/no-go and safe restoration.

## Package order and ownership
P0076 follows P0072 r3; independent of P0075 bootloader-readback outcome. Two separately accepted features:
- F0076-A: EFFECT — feedback regulation of delivered heating power in kW.
- F0076-B: BRINE STRESS / COP — time-series acquisition, staged-load analysis, recovery and efficiency comparison.

Reusable Procon firmware and portable tests belong to `marlov1974/procon-melcobems-mini-a1m`. Experiment planning, Mac logging, analysis and site evidence belong to `marlov1974/smart-home`. No unrelated system modifications.

## Operator decisions — measurement boundaries
**The independent load variable is heat delivered to the floor-heating circuit in kW.** Do not substitute ground extraction, electric compressor consumption, requested setpoint, or compressor Hz. The existing MVP field i7 measures estimated water-side output from GET0C/GET14, not automatically floor heat delivered. Before labeling it 'floor kW', determine hydraulic routing (space-heating vs DHW, bypass, mixing, buffers/pool, pumps) and validate the sensor/meter boundary. For an unsuitable hydraulic state, tag `FLOOR_HEAT_UNCONFIRMED` and do not claim a floor-load or floor-COP point.

**A single pump cannot deliver 18 kW as a sustained target** per operator's current planning constraints. For a single unit, 9 and 12 kW are example comparison levels, subject to its actual observed capability and native limits. **18 kW is a combined VP1+VP2 load point.** The operator expects the pair *may* achieve 24–27 kW continuously, but this is an **unverified hypothesis**, not rated capacity, continuous capability, or authorization to demand it. Validate each pump and the combined hydraulic/electrical system separately before claiming sustained capability.

For two pumps, record `P1_floor`, `P2_floor` and `P_total_floor` only when measurement topology allows non-overlapping contributions; otherwise use a valid common downstream floor meter and label its boundary. **Never add two measurements that count the same circulating heat twice.** Collect `E1` and `E2` electric power on corresponding synchronized boundaries; separate compressors, internal pumps, booster/immersion heat, other auxiliaries and shared loads if metered. Record exactly which components enter COP. A single Procon does not itself control the other heat pump; coordinating two units is a separate guarded Mac/controller layer, not an implicit Modbus command broadcast.

## Existing source baseline
P0072 r3 is the latest discussed firmware. MVP field i7 delivers signed water heat in W, `W = trunc(flow_cL_min * delta_cC * 418 / 60000)`, based on GET0C supply/return and GET14 primary flow. It assumes water properties, has whole-L/min source resolution and a 2-second alignment criterion. A3 service27/28 TH32/TH34 candidates have source whole-degree resolution and limited across-range calibration. GET04 exposes compressor Hz. P0072 r3 has supervised physical evidence for FIXED_FLOW38 C, explicit AUTO and lease-expiry restoration; other modes and persistent reboot recovery remain unverified. Its snapshot and lease live only in RAM: loss of power/reset may leave native setpoints changed. Do not claim unattended autonomous recovery.

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

## F0076-B — BRINE STRESS / COP

### Acquisition
- Log TH32 brine in, TH34 brine out and brine delta **once per minute**, recording separate source sample timestamps, generations and age; do not pretend asynchronous samples are simultaneous.
- Log faster process/electric data as available, aggregate per minute with actual timestamp boundaries (mean/min/max Hz, power, flow, flow/return, temperatures and EFFECT state).
- Measure actual delivered floor kW, requested kW, independently measured electric kW, heat-pump mode, primary flow, supply/return, TH32/TH34, load-step ID, minutes since transition, validity/quality and source IDs.
- No fabricated electric power or COP. If Shelly 3EM measurements are not installed/validated/assigned to correct circuits, output `COP_UNAVAILABLE`. Sensor placement and shared-load inclusion must be explicit.
- Retain raw timestamped measurements locally on Mac and export CSV/Parquet plus machine-readable metadata. Never replace failed/missing minutes with silent interpolation for analysis.

### Controlled staged experiment
- Passively validate acquisition first. Later conduct supervised rising load, downward load and recovery intervals, preferably 15–30 min per plateau where safe/feasible; select step setpoints from **actual accessible output** not assumed capacities.
- One-unit and two-unit experiments are separate datasets. Run only a tested, explicitly coordinated two-pump sequence for combined 18 kW or higher. 24–27 kW continuous is a **research objective to verify**, not a guaranteed setting or a minimum acceptance target.
- Each plateau must be classified by measured achieved floor kW and fraction of time held, with native limits and compressor Hz. Reject comparisons based solely on requested kW.
- Stop conditions before field test must be defined from verified Geodan native operating envelopes and observed supply/brine temperatures; never disable built-in safety. A stop request does not guarantee immediate compressor stop. Test must be supervisable, bounded, and allow a safe return to the previously recorded state.

### Analysis of curves and knees
- For each interval calculate TH32/TH34 starting temperature, deviations after 1/5/10/15/30 min where measured, fast/slow °C/min slopes, best-fitting response family only when justified, continued decay versus plateau, and post-load recovery.
- Compare multiple real **floor-delivered** kW plateaus at matched time since step and matched/adjusted initial thermal state. Look for thresholds/plateaus and reproducibility; do not label a single transient 'collapse' without repeats and quantified uncertainty. Document 1°C source quantization and sample-age limitations.
- Analyze up/down hysteresis, prior operating history and the common borehole interaction if two units share the source. Keep brine sensor identities per unit and do not assume hydraulic source topology.
- Produce time-series graphs of TH32/TH34 with load overlays, achieved kW/Hz against time, equal-time brine depression vs achieved floor kW, recovery curves and knee/uncertainty report.

### COP comparison and future optimization
- Define `COP_boundary = delivered_floor_heat_kW / measured_electric_input_kW` over synchronized windows, explicitly stating what electrical/thermal loads are included. This is **floor-delivery system COP** unless measurement boundaries support a narrower heat-pump COP. Reject zero/invalid watts and windows dominated by transients if reporting steady-state COP.
- Compare at **9 and 12 kW per individual pump where reachable**, and **18 kW combined VP1+VP2**. Optionally compare combined 24–27 kW only if subsequently demonstrated safe/reachable. Also compare equivalent combined output under alternative load splits, such as 9+9 vs 12+6 if both feasible, rather than attributing one fixed COP to a total output level.
- Capture outdoor/ground-entry, floor flow temperature, return temperature, DHW state, compressor Hz, primary pump behavior, electrical heater status and test history. Normalize or stratify comparisons; COP difference from unequal supply temp / starting brine is not automatically a kW-caused effect.
- Compute per-unit and combined COP **only with consistent, non-overlapping heat and electric measurement boundaries**. Record inclusion of both circulation pumps and any booster heater. Prefer measured delivered thermal energy divided by measured electrical energy over the stable comparison window, with sample count, duration and measurement uncertainty. Avoid point-ratio artifacts.
- Deliver a comparison table with achieved heat (kW), electrical input (kW), COP, window length, input brine temperature, supply/return, split VP1/VP2, limits and uncertainty. No result claimed where measurement support is missing.
- Later control optimization based on COP is **out of scope** for this initial package; report recommendations separately and require a new authorized control package before closed-loop dual-unit dispatch.

### Acceptance F0076-B
Pass offline tests using labelled simulated input (no fabricated hardware success), validate minutely collection, timestamps, source generations, energy integration, COP boundaries, no double counting, missing sensors, individual-vs-pair identifiers and knee detection under drift/noise. Physical acceptance is staged: passive capture first, supervised one-unit tests second, then separately authorized two-unit tests. A sound inconclusive result (no detectable knee or no measured COP at a target) must be reported honestly rather than forced to pass.

## Operator-defined weekend long-duration protocols (2026-10-07)

Two distinct studies are requested. They are **future physical experiment protocols**, not authorization to execute before hardware/control gates are satisfied. The calendar start, machine identity, monitoring responsibility and exact safety thresholds remain to be confirmed with the operator. Do not merge them into a single uninterrupted 16-hour run without transition/restoration checks. Separate run identifiers and complete timestamped datasets are required.

### Study A — 4-hour heat-output staircase

| Step | Target delivered floor heat | Duration |
|---|---:|---:|
| A1 | 3 kW | 4 h |
| A2 | 6 kW | 4 h |
| A3 | 9 kW | 4 h |
| A4 | 12 kW | 4 h |

Total target dwell time **16 hours**, excluding setup, any transitions/pauses and the subsequent recovery observation. Targets are requested **floor-delivered heat**, not compressor electric kW or extraction from brine. Keep each step's achieved kW, tracking error and percentage of valid within-band time; an unattainable 12 kW plateau must be flagged `TARGET_NOT_REACHED`, not silently forced. The thermal state at step A2/A3/A4 includes accumulated heat extraction from earlier stages, so raw step differences are *not* pure causal power-response curves. Capture initial state and optionally validate with repeated or reordered plateaus on a later day.

### Study B — repeated 9 kW recovery comparison

| Sequence | Requested load/hold | Interval |
|---|---|---:|
| B1 | 9 kW delivered floor heat | 4 h |
| B2 | Rest / source recovery | 1 h |
| B3 | 9 kW | 4 h |
| B4 | Rest / source recovery | 2 h |
| B5 | 9 kW | 4 h |
| B6 | Rest / source recovery | 4 h |
| B7 | 9 kW | 4 h |

Total is **16 h of requested 9 kW plus 7 h of rest = 23 h**. If both studies are performed once, minimum scheduled holds total **39 h**, not counting inter-study stabilization, initial baseline, transitions or final recovery. Log continuously during every rest and consider adding a separately agreed post-B7 recovery observation; no default duration is invented.

**Rest definition must be explicitly implemented and verified.** A request for `EFFECT=0` does not mean actual compressor shutdown. Choose and record a safe native state that genuinely stops *the tested unit's* heat extraction when appropriate, preserve operator-approved antifreeze/native protections and note other loads (DHW/pool/other heat pump) that may prevent the ground source from resting. Record actual compressor Hz=0 and brine-pump state when available; do not call a rest period `RECOVERY_ZERO_LOAD` if another machine continues extracting from a shared loop. If no confirmed shutdown/restore procedure exists, block active recovery testing rather than assuming Modbus OFF is equivalent to zero source extraction.

### Continuous capture and analysis
- Record brine TH32/TH34 at **one valid time-stamped observation per minute**, retaining source age, whole-degree quantization, acquisition order and confidence. Maintain uninterrupted logging during load, rest, transitions and any stops.
- Also record each minute: requested and measured floor kW, rolling power, compressor Hz, primary flow, forward/return temperatures, native mode, DHW/boost and other heat-source activity, regulation phase and flow target, electric kW (when validated), and current step/run ID. Calculate achieved heat energy per phase using only validated time-aligned measurements.
- For Study A, compare TH32/TH34/ΔTbrine level and slope at common elapsed times 5/15/30/60/120/240 min, as data allow, plus end-of-step decay and possible threshold changes versus **achieved** floor heat.
- For Study B, capture temperature just before/after each shutdown and restart; quantify rebound during 1/2/4 h rest, starting temperature for each subsequent 9 kW hold, first-hour response, final 4-hour temperature and cumulative history. A 1/2/4 h rest sequence has a changing starting thermal state and order confounding; do not claim isolated recovery constants or a precise sustainable ground-output threshold from one sequence.
- Log actual heat-delivered and electrical energy during load and rest; compute COP only for valid consistently bounded periods, and do not claim 9/12 kW COP comparison is causal unless supply temperature, initial brine and load mix are considered.

### Multi-hour execution / lease and recovery gate
- Existing r3 command envelope has **30–1800 s lease** and RAM-only snapshots. **Four-hour holds cannot be executed by simply setting a four-hour lease.** Define and test bounded supervised lease renewals, single-writer ownership, stop/resume and application/native-state reconciliation after host, Shelly, Procon and heat-pump restarts. On network disconnect, inability to refresh state, failure of telemetry freshness, run-away target, native inhibit or exceeded temperature/rate limits, command no new up-ramp; enter a verified safe stop/restore path and alert the operator.
- Require a documented check of cooling/pump/source and heat-sink capacity for a sustained 12 kW requested floor load. Confirm exact safe temperatures/abort margins from the device and plumbing before running; native protections must remain enabled.
- Before running over a weekend, require operator approval of: specific VP, test start, supervision/availability, logging path, effect setpoint ceilings, compressor/source limits, rest mechanism, what happens if host loses power, and automatic stop/rollback behavior. If persistent recovery and abort behavior cannot be validated, run only shorter supervised periods; **do not run these 16/23 h scripts unattended**.
- Time-based test schedule belongs in the experiment controller with monotonic elapsed-time accounting, durable step state, explicit human pause/resume and restart checks. A device reboot must never restart a long test automatically at a high-load step without operator reapproval.
- Include dry-run tests covering all 7 recovery phases, both 4-hour staircase boundaries, failed/unattainable plateaus, missing brine minutes, lease renewals, and interruptions during a rest/load transition.

## Non-goals and invariants
No bootloader/readback development, firmware programming over Shelly, EEPROM changes, arbitrary CN105 SET, brine/primary pump override, fault reset, native safety bypass, automatic compressor-Hz command, or unattended load scheduling. No claim that 18kW is a single-unit target, or that 24–27kW continuous combined is established. No uncontrolled simultaneous masters or control leases. Preserve existing P0072 Modbus layout/telemetry and deterministic release paths.

## Implementation phases and gates
1. **Review/design:** read Smart Home bootstrap and `AGENTS.md`; relevant P0072 r3 changelog, `procon/docs/MVP_API.md`, `CONTROL_API.md`, test evidence, and standalone repo hardware/API reference. Preimplementation PASS/WARN/STOP, write `requirements/package-runs/P0076/review.md`, `design.md`, `functions.md` before changes. Any STOP blocks implementation. No changed API silently.
2. **Offline:** implement and test regulator, interface/mocks, Mac collector and analysis with synthetic datasets. Preserve stable existing modes and output. Test determinism, no changes to unrelated control paths and full safety behaviors.
3. **Passive hardware measurements:** only after operator go-ahead; no thermal-setting writes. Validate floorside thermal-power measurement location, A3 TH32/34 identity/quantization, logging and electrical metering.
4. **Supervised single-unit EFFECT:** separately authorized, record original native settings externally, test bounded low/medium targets and restoration; cap debugging attempts at 3 before review.
5. **Supervised load-staircase and optional dual-pump COP:** separately authorized with verified power and hydraulic measurement boundaries, thermal limits, pause/abort and per-unit controls. Never assume the package authorizes 18kW single-unit or 24–27kW continuous combined.

## Test cases / expected deliverables
- TC1 unchanged P0072 existing Modbus telem/FC16 v2 behavior and exclusive A3 scheduling.
- TC2 rolling valid power from distinct cycles; stale/skew/unavailable/zero-flow fail safe; bounded filter lag.
- TC3 START/CAPTURE/HOLD convergence, overshoot prevention, limited state and no setpoint ratchet at unreachable kW.
- TC4 timeout, native inhibits, concurrent lease, reset/power interruption; no claim of durable automatic restore.
- TC5 passive one-minute brine capture and timestamp/quality correctness.
- TC6 rising/descending experiments and safe incomplete data handling.
- TC7 identical target but changed starting brine distinguishes hysteresis; quantified knees vs false positives.
- TC8 COP 9/12 single unit, 18 combined, optional 24–27 combined: correct metering boundaries; refuse missing electric readings or overlapping heat meters; separate transient vs stable windows.
- TC9 end-to-end restoration, telemetry revalidation and durable signed-off evidence with real operator go-ahead.

Codex to produce review/design/functions/CHANGELOG, test outputs and sanitized findings under `requirements/package-runs/P0076/`, portable release/test artifacts in standalone repo, exact commit/release hashes, and an explicit not-yet-tested statement for physical phases. New source paths require a synchronized `REPOSITORY_FILES.md`. No vendor binaries, raw dumps, proprietary updaters, credentials or site-private logs enter standalone repo.

## Codex execution order
Implement the offline package first. Before any deployment/physical actuation, stop and report the remaining safety blockers, accurate capability boundaries, valid COP measurement channels and proposed field runbook. User alone authorizes the next physical phase.
