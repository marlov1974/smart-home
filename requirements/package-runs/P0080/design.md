# P0080 modular implementation design

## EFFECT + rolling energy v4 — 2026-10-16

Keep the four business layers explicit: rolling quarter energy selects pair
power; pair allocation selects each pump's watt target; the Procon model maps
watts to a frequency goal; the inner controller converts frequency error to a
bounded requested-flow command. L4 remains responsible for day/week COP and
quarter targets. Shelly performs only scalar four-quarter delivery, calm
cross-pump allocation and correction from measured energy.

Persist only the slowly learned kW-to-Hz gain. Shelly binds a strict record to
all 96 UID bits and uses compare-and-swap plus exact readback. Firmware accepts
that gain through C077 only behind the maintenance gate, at most once per boot,
and keeps it in RAM. Do not write EEPROM or flash, and do not persist bias,
trim, response transients or confidence as if they were plant constants.

The rolling plan is an atomic KVS string with current-quarter alignment and
four Wh targets. A later revision for the next boundary is staged and activated
as one unit. Missing/stale measurements remain unknown energy while an existing
lease is held; no plan creates no ownership. Temperature priority, physical
reachability and native DHW/pause states remain best-effort constraints rather
than abort conditions.

Runtime validation is a separate non-actuating path. It must read both exact
identities, model diagnostics, feedback blocks and the complete plan, execute
the scalar planner, publish proof and stop before any EFFECT or C077 write.
Unqualified startup feedback cannot prevent this self-stop; production mode
continues to hold until both power samples are fresh.

## Four-quarter energy mode — 2026-10-14

Use measured delivered Wh as the controlled quantity; do not book assumed
linear ramps. A Shelly pair planner allocates the house plan between D1/D2, and
a per-device Common executor retargets the existing Mode EFFECT loop. Low demand
is scheduled asymmetrically because 2 kW per running pump was below the observed
continuous range. Common has 7,984 bytes free and Mode only 240 bytes; extend
Common and Dispatcher without changing BL2/layout. Full controller, protocol,
feasibility and delivery design: `energy-mode-design-2026-10-14.md`.

The binding initial response model is per device: 5min zero-output startup from
zero, +4kW/5min maximum ramp-up and -2kW/5min maximum ramp-down. Targets and
errors belong to the pair, so recovery and ramps can cross VP1/VP2. Replan from
measured state every30s. Minimize four-quarter energy error first. L4 already
accounts for COP when selecting kWh/quarter; local execution only divides work
when both pumps can stay above their continuous floors and prefers a calm
combined curve over short high-power bursts. With initial3kW floors,4kW total
remains4+OFF while6kW becomes3+3.

L4 alone measures/learns pair COP and uses it for day/week quarter selection.
Shelly does not calculate COP or compare COP bands; it may only forward raw
telemetry. Its executor minimizes four-quarter delivery error, keeps combined
power calm and divides that power evenly subject to each pump's physical state.
The3+3kW/16h versus2+2kW/24h decision for equal96kWh belongs to L4.
An unreachable target saturates to best effort and remains active.

Shelly implementation constraint: no JavaScript arrays. Simulate the24 planning
steps serially with scalar VP states and scalar q0/q1/q2/q3 energy accumulators.
Evaluate and discard one scalar candidate at a time; retain only the current best
candidate's named scalars. Parse compact KVS fields without `split`. Python list
usage is confined to offline reference/testing and is not a device design.
Eight fixed flash slots: BL2 8K, Common12K, dispatcher4K, mode12K, drift4K, service4K, debug-command4K, debug-telemetry4K, manifest2K. All aligned2K. Measure and change budgets only with evidence.
Each module independently linked with 64-byte header and fixed4-byte Thumb branch veneers. External symbols resolve only to versioned veneers; no cross-image LTO. Per-slot RAM regions and startup data copy/BSS zero; no per-module VTOR/stack/heap. BL2 owns peripherals and mainloop; Common owns CN105 scheduling, service module A3 state, mode owns unchanged P76 effect/control/feedback. Debug adapters are explicitly small and not claims of a new full RAW implementation.
BL2 validates every slot CRC/header/ABI and last-written manifest before any module execution. All-or-nothing feature activation, maintenance remains when invalid. Native reset restoration remains P76 limitation: OTA entry requires fresh native curve/DHW readbacks and no active lease; invalid image repair cannot assert restoration.
Addressed FC16 system envelope with FF enter/FE wait. WAIT keeps native pump untouched and produces no RS485 replies until timeout/reset; no persistent WAIT. At115200 target alone accepts bounded P8 frames,240 payload/252 wire, CRC32, duplicate-aware stop-and-wait. BEGIN binds targetUID and expected current manifest; erases manifest first, then changedslots. WRITE ordered8-aligned chunks, COMMIT validates allslots and writes manifest marker last. No BL2 OTA, no originalboot/option writes, no A/B. Host refuses live use without explicit handoff/peer inventory/native verification.
Tests: actual independent ELF routing and baseline behavior, native protocol flash backend with interruption/retry/malformed inputs, build bounds/independent update, sender fakeRPC transport, single/shared-bus simulation. Physical two-device timing and OTA remain unverified.
# Direct fixed-flow target continuation — 2026-10-10

Operator authorized this change after the down/up identification trial. Review WARN: retain the existing P0080 working tree, no automatic merge or publication; remote has no divergent commits. Live evidence and exact sync status are in local P0080/effect-learning. No physical firmware installation in this follow-up.

Allow only v2 flow-only FIXED -> flow-only FIXED replacement while ACTIVE, saved, not waiting and not EFFECT. Require next sequence. Retain original, saved and touched. Re-read native26/09/28, requiring powered fixed heating/pause mode, no boost and normal relevant flags. Reject external target change relative to the prior session target. Plan FLOW only; retain pre-SET mode check and readback. ACK does not advance applied. Lease expiry or failed replacement restores the initial session state, not an intermediate target. Same-sequence retries remain idempotent; changed intent during APPLY remains BUSY. Combined DHW changes and cross-mode replacements remain unsupported.

Tests: multiple up/down targets with zero extra MODE/POWER SETs, exact retries and conflicting sequences, pending replacement BUSY, late ACK, failed readback, blocked native flags, changed native mode, AUTO and lease restoration. Build same ABI/layout; only mode chunk/manifest may differ from release-bl2-v2. Firmware remains unflashed.

## Brine pump A3 telemetry — 2026-10-10
Operator-requested P0080 continuation on the existing uncommitted implementation; fetch confirms no HEAD/origin divergence. Preserve all existing work. Review WARN: OCH722A page30 documents service018 output step0..10 and019 speed0..9999rpm; A3 wire support is a candidate until live correlation. Add18/19 after27/28 with unchanged exclusive retries and FAST between every operation. Keep snapshot20/schema1 and ABI/layout. Index11=step; index10=RPM-derived running, explicitly not independently measured motor state. New FC04 raw87..92 step and93..98 RPM: raw,valid,age_seconds,status,completions,ever. Invalid/range/stale readings never become valid zero. Read-only service queries only. Existing pump temperatures remain independent. Test four-code scheduling, unsupported/timeout starvation bound, echo checks, zero/RPM/range/TTL/link loss, frozen snapshot and slot sizes. Build service+drift update against installed direct-flow image; no flash in this implementation step.

## P0080 brine pump A3 extension (2026-10-10)
OCH722A service manual p30 identifies decimal018 output step0..10 and019 RPM0..9999. A3 support is a wire-mapping candidate pending physical observations, not a confirmed flow sensor. Schedule27,28,18,19 with a full FAST round between service operations; original retry ownership/limits retained. Snapshot schema1 remains20 fields: index11 step, index10 running derived ONLY from valid in-range RPM>0. ZeroRPM is valid stopped feedback, never inferred from missing data or step0. Controller feedback still needs physical correlation for the hydraulic test.
FC04 zero-based87..92 (018) and93..98 (019): retained raw, protocol-valid flag, age_seconds, last status, completion generation, ever-completed. Raw/protocol-valid do not perform engineering range checks; snapshot does. Age TTL60s, link-down invalidates all four services, no stale value becomes valid zero. Temperature and pump sources are asynchronous; a stopped test must require fresh repeated RPM samples and actual water-pump stop feedback. No new pump commands. Only drift/service chunks differ from installed direct-flow; BL2/layout/ABI/control unchanged.

Native ASan/UBSan and actual ARM cross-slot tests passed. OTA C engine1037 mutation cuts, host fake-RPC update/lost-ACK/cleanup passed. Existing tracked paths only; index unchanged. OTA proceeding under operator hydraulic-test task. Knowhow promotion deferred until physical mapping is checked.

## P0080 EFFECT entry starvation correction — 2026-10-10

Operator ended hydraulic experiments and requested fixing EFFECT. Continue existing P0080 work; fetch shows HEAD=origin/main, all existing local changes preserved. Review WARN: live cause originally unknown; full CN105/sampler/controller simulation now reproduces BAD_FEEDBACK, accepted1/applied0, automatic restoration. With220ms replies and six A3 attempts, GET04 age reaches10000ms during entry readback because CONTROL monopolizes the service boundary. Preserve stale/link/mode safeguards; refresh a complete FAST round between control transactions when source age demands it. No interleaving inside an owned transaction or A3 operation. Test real scheduler and sampler together, delays/entry timings, normal and invalid feedback, restore semantics. Build same slots/ABI against pump firmware; no automatic physical installation in this implementation step.

Operator refinement: measurement freshness is strictly age<60000ms. Preserve independent wire/native guard timing and source coherence. WARMUP in an already accepted EFFECT session should suspend adjustments like PENDING, not classify collection as hard failure. Initial admission still requires qualified feedback or supported native pause. Test freshness boundaries and recovery, then build same-ABI three-slot OTA candidate.

## Fast thermal demand regulator — operator-authorized build, OTA and dual6kW/15min test
Separate actual supply40C ceiling from requested supply up to55C. Preserve existing <=40C command behavior for compatibility; cap>40C explicitly selects new fast law. No ABI/layout/export changes. Initial large deficit requests configured cap promptly;15s decisions use maximum of instantaneous/short heat and positive trend30s projection. Approaching target collapses boost to actual supply+1C; bounded corrections seek equilibrium. Supply>=38C or30s projection>=39C lowers demand; actual>=40C initiates restoration independently of power readiness. No cumulative5C/unresponsive latch in fast path. Paused compressor demands stay mild and above measured supply; never55C during native pause. Old data never authorizes a fresh boost; ready but aged15s reduces high demand. Existing hard feedback/link/lease restore remains; softer stale behavior remains follow-up. Validate old mode regressions plus new fast behavior, actual-temperature guard, late feedback, pause and cap acceptance. Build changed mode slot and host encoder. Test candidate ARM and OTA before updating known D1/D2; repeat15min target6000W each, log response and energy, restore both afterward. Existing authorized working changes preserved; fetch origin no divergent commits.

Operator refinement during deployment: unmet high power demand must remain active at the thermal ceiling, report actual available power and temperature-limit reason, rather than restoring at exactly40C. Add hysteretic thermal-limit state: engage at38C or30s projection39C; bound demand to39.5C (sensor/lag margin) while retaining mission; disengage below37C with projection<38C. Power control may still lower demand. At actual40C continue limited operation; actual>40C (first encoded0.5C step40.5C) remains an excursion/failure restore. Actual ceiling remains40C, not an operating target of40.5C. Native minimum power/hysteresis cannot be overridden; no guarantee of continuous operation outside native capability. Existing target/measured short/slow power plus LIMITED/TEMPERATURE_CAP report demand versus delivered power; do not claim a calibrated capacity from a transient point. Retest and install a second mode-only candidate after in-progress deployment finishes, before physical6kW trial.

Persistent best-effort refinement: fast sessions retain the accepted mission through stale/invalid/zero-flow samples, naturalDHW and link/read timeouts. They stop increasing demand, reduce any existing boost to39.5C when native heating guards can be read, retain original snapshot and lease, then read native state again before resuming after a communication interruption. Do not reset native safety/inhibit flags or force power-on. Native ownership/mode changes remain respected. Fast native pause has no20min failure deadline; operator lease and AUTO still end mission. Thermal40C stays active; host trial still records/enforces requested actual-temperature bound. Tests must exercise recovery instead of merely weakening old failure assertions; legacy low-cap paths retain existing semantics.

## P0080 smooth capture — operator refinement 2026-10-10
The852841df physical quarter-hour test oscillated after abrupt55C-to-supply+1C braking. Replace ordinary boost/capture discontinuities with a retained capture state: initial55C is allowed, sustained positive power slope or proximity to target starts gradual taper; thereafter correct the existing demand with bounded small steps and derivative damping, without jumping back to55C on power deficit. Trend is filtered and preserved across normal partial FAST refreshes. Temperature protection and degraded-feedback reduction take priority over smoothness. This is an empirical candidate, not a proven FTC model or stability claim. Verify response sequences, slope/noise handling, no repeated boost, existing recovery/restore, ARM artifact and fixed-slot fit. No new ABI or tracked paths.

## P0080 lease renewal during effect adjustment — 2026-10-10
The short-lease smooth trial expired because repeated APPLY phases prevented equal-intent renewal. Permit a next-sequence, identical-intent EFFECT renewal during APPLY only when the original mission is already applied (saved and applied==accepted). Preserve the in-flight transaction, action queue, original snapshot, controller phase and pending regulator demand. Renewal acknowledges continued ownership of the same already-applied mission; it is not proof that the current internal FLOW adjustment completed. Initial QUEUED/SNAPSHOT/unapplied sessions and changed intents remain BUSY. Exact retransmissions still never extend the lease. AUTO and expiry restoration remain unchanged. Test renewal with a guard read in flight, after SET but before readback, and with suspended adjustment; prove no duplicate SET, no early readback completion and final restoration to the original settings.

## P0080 Hz-leading controller identification — 2026-10-10
Operator authorizes an hour of theory/data/live iteration toward a monotone6kW response, measured supply<=40C. Historical analysis found30–45s lag of rolling thermal power behindHz and a poor universal delta-only model. Trial host law uses35s Hz leading correction110W/Hz and bounded actuator-rate feedback from desired acceleration(error/90s) versus measuredHz acceleration. C candidate uses60s acceleration to suppress staircase alias, suppresses early braking when prediction<target−1.5kW, and freezes downward adjustment whenHz falls near/belowgoal. Initial45C demand matches current host pilot; configured55C remains an upper bound. Ordinary15–59s measurement age holds rather than abrupt reduction; actual/forecast thermal protection remains. New history is module-private; no ABI change. Native host/ARM/OTA tests and physical evidence required, empirical precision limited by0.5C sensors.

P0080 refinement during host pilot:60sHz slope can retain old acceleration after recent35splateau. Falling recentHz freezes braking up togoal+300W; flat recentHz freezes braking only belowgoal−300W. Progressive thermal commandceiling3950+3*max(0,3950−Tlead10s) replaces ordinary38.5Ccliff; actual>=39.5 or30sprojection>=40 retains protective3950override. Cap alwaysrespected, missionretained, no integral accumulation behindbarrier. Physical40C hostlimit retained. New guards covered by host/ARM tests; empiricalbarrier is not a guarantee of zero physicalovershoot.


## P0080 early startup demand and fine correction — 2026-10-10 continuation
The operator requests resolving the two remaining issues, continuing the authorized firmware/OTA/physical work. Fetch confirms no remote divergence; preserve the existing authorized local P0080 changes. Review WARN: native lockout cannot be removed, and the late 0.5 kW deficit was not stationary. Do not claim a calibrated 99% power controller.

Use the first fresh coherent heating pair during EF_SETTLING to authorize a bounded startup demand, separately from averaged-power regulation. Require pairs>=1, age<15s, positive valid Hz, heating mode and valid measured supply. Keep full rolling-power validity unchanged. A flagged startup demand retains existing native GET28/26 guards and readback. Recheck qualifications before sending; discard an unsent stale startup request. Complete readback for already-sent actions. Apply a progressive thermal ceiling during settling too; never force power-on or override native pauses/DHW. Keep the existing pause margin for this experiment to isolate the known software startup delay.

The current requested-temperature update already integrates power error, so do not add an independent bias integrator. Reduce the quiet error band to150W and retain small signed temperature corrections until they amount to0.1C, with reset on pause, long data gap, sign reversal and saturation. Keep Hz lead/acceleration damping and normal bounded steps. Validate quantization, residual cancellation, saturation, stale hold and recovery; then build within fixed slots and test ARM/OTA before updating known D1/D2. No struct, layout or exported-veneer change is intended. A longer uninterrupted native mission must include post-capture observation; actual supply40C and requested55C limits, 180s renewable lease and verified curve restoration remain.

Build qualification: the first startup implementation exceeded the fixed mode slot by232 bytes. Use GCC size-priority -Oz for the mode module only, preserving other modules, veneer addresses and layout. Verify the exact built ARM image and all exported functions; do not silently enlarge the physical slot.

Fixed-slot refinement: -Oz produced no size improvement, so retain the original -Os compiler setting. Consolidate effect.c private regulator variables into one private state structure and reset it as a whole in effect_init. This removes duplicated per-variable initialization/address loads without changing public structs, RAM reservation, function signatures or behavior. Verify the complete host/ARM suites and module size.

### 2026-10-10 live entry transition follow-up
The first physical attempt with prefix784a48ae aborted before applied: both units reported control error8 / BAD_FEEDBACK and restored native curve. No sustained power-control result exists for this attempt. Investigate READY/PENDING/WAIT_NATIVE/SETTLING transitions during initial MODE_FLOW guards. Transient unqualified feedback must defer a not-yet-sent command, preserve the original snapshot and bounded lease, and requalify native guards before resuming. Native ownership/inhibit and already-sent readback handling remain mandatory.

### Prospective atomic entry-demand experiment (not yet installed)
The d64080c7 entry completed on both pumps at15:55:09UTC, then both paused. Initial fixed target30.5C was below actual~32C; causality is a hypothesis, not established. A separate offline candidate should choose the initial atomic MODE_FLOW target after fresh native guards, immediately before sending: qualified fresh running heating feedback below target permits bounded45C startup, capped by the existing thermal ceiling. Recompute while unsent; fresh zero-Hz pause uses mild measured+0.5C demand. Never overwrite original snapshot and never alter expected target after sending. Validate readback, loss of qualification, ownership/inhibit, finite lease and restoration before installation. Current30min run continues unchanged.

### Predictive startup/capture candidate
The uninterrupted155246 trial reached95% about234s after compressor restart, but demand continued increasing through a42Hz plateau before late braking at52Hz; a further~10Hz increase followed. The candidate keeps the35s lead for power averaging and adds45s of positive Hz-rate forecast capped1500W, changes error-to-acceleration divisor165 to220, prevents further positive demand when short power is rising >200W/min above target−2000W, and permits at most1C downward steps when forecast is >target+300W and Hz is rising. Falling/current-leading-power guards remain; forecast never bypasses thermal/native/ownership limits. This is an empirical candidate, not a validated model. Atomic entry and predictive capture are qualified together offline, then physically tested after restoration of the present run.

### Thermal ceiling correction after physical abort
The155246 experiment ended at the unpaired D1 capture t1434.8s: actual40.5C despite fixed39.5C demand since~758s. Actual40C had persisted for~410s, so a fixed39.5C demand ceiling did not correct persistent temperature offset. Both original curve states and helper cleanup were verified restored. Revise the thermal envelope with center39.0C and signed margin `m=3900−supply−max(rate,0)/6`: ceiling `3900+(m>0?3*m:m)`. A30s forecast reaching40C may only lower this ceiling via min(ceiling,3900), never raise it. This preserves early progressive braking and adds downward feedback above the center without another integral state. At flat39.5/40.0/40.5 actual, ceilings are38.5/38.0/37.5 respectively; empirical live validation is still required, not a guarantee of zero overshoot. No change to the explicit40C observation stop guard.

## Response memory and demand recovery — 2026-10-10
The measured e8fc6d86 run exposed a demand hold across a42Hz plateau and slow recovery after thermal limiting. Preserve a bounded positive acceleration forecast (maximum1500W), decaying at10W/s when fresh decisions continue, so a short plateau cannot immediately erase recent momentum. Clear it on observed deceleration, weak demand (requested minus actual below2C), native pause/history discontinuity or actual thermal clipping. This is an empirical lead estimate, not a claimed reconstruction of the native integral.
Replace unconditional rising-power suppression with a30s projection near target. If predicted power is still at least750W below target and demand is within2C of actual supply, allow a bounded1C positive correction rather than the normal0.5C bound; retain fresh-data admission and the existing decision/readback cadence. Thermal ceiling remains unchanged and applies after every proposed correction; clipped demand is never accumulated for later release. Existing legacy cap<=40C mode remains unchanged.
Test retained lead on quantized plateaus, decay and fresh mission reset, recent-frequency decline, stale data, recovery despite modest positive power slope, no added demand near goal, and thermal priority. Replay recorded inputs as a one-step counterfactual diagnostic only, never as a predicted closed-loop trajectory. Build within existing12KiB mode slot; if necessary qualify a mode-only compiler size setting, without changing other module binaries. No live deployment is part of this follow-up's offline validation.

## Source-aware persistent EFFECT continuation — 2026-10-11
User authorizes implementing and live-testing on VP1. Keep all module boundaries,
export veneers and `effect_measurement` ABI unchanged. Mode reads existing Drift
`tele_snapshot` for independent source generation and source time (`now-age`) of
Hz and supply. Duplicate polls cannot create history; wrapped generations and
clock wrap must work. Reject invalid/link-lost sources and hold ordinary control
with 15–59s old data; existing >=60s recovery remains.
Unify EFFECT at every configured demand cap, retaining finite lease, native
interlocks and exact original-state restoration. Remove cumulative/unresponsive
latches and cap-dependent native-pause abort. Fix link-loss during restoration.
Add a soft temperature constraint before the existing emergency ceiling: reduce
requested acceleration as predicted supply approaches39C, retain braking when
thermal margin is exhausted, and clear positive carry. Existing signed hard
ceiling and actual40C trial limit remain. This is an empirical control hypothesis,
not a recovered Mitsubishi Hz equation. Fixed110W/Hz is not changed in this pass.
Build against VP1 build-p81; only Mode should change, BL2 must be identical.
Run host sanitizers, real ARM module tests and OTA cut/sender regressions before
OTA. VP1: target6000W, demand cap55C, actual supply maximum40C,15min observation,
lease180s renewed under supervision. Capture/restore original native settings.
VP2 receives no heating-control writes; temporary protocol WAIT isolates OTA.

## Predictive thermal envelope, dual trial — 2026-10-11
Explicit user continuation authorizes the thermal correction, OTA both units and
VP1 6kW / VP2 5kW trial. Keep P0080 scope, native safeguards, finite lease,
restoration and actual40C/requested55C bounds. Preserve both installed feature
sets, building per-device manifests with only Mode replaced. No BL2 update.
With fresh independent supply history spanning>=40s, forecast supply over60s
plus sample age. Positive slope only; falling temperature never excuses an
already hot actual reading. Use margin3900-forecast and requested ceiling
3900+(margin>0?8*margin:margin), capped by configured demand and floor3000.
This permits47C at flat38C instead of42C, but progressively tightens with rise
and retains39.5/40C actual ->38.5/38C demand protection. The gain8 and60s horizon
are cautious empirical trial parameters, not identified native constants.
Retain original conservative ceiling without fresh established history. Soft
Hz-acceleration constraint uses the same forecast; existing bounded actuator
steps and no repeated startup boosts stay. Tests cover trend/age sensitivity,
fallback, thermal recovery, hot correction, stale data and configured caps.
Build within12KiB Mode, run host/actualARM/OTA checks, then supervised900s dual
trial with independent logging and restoration. No exact tracking claim until
physical results. Record both source freshness and applied thermal restrictions.

### Operator correction: temperature is a regulation condition, not abort
The user explicitly rejected restoring/aborting on40C,42C or time above40C.
Log these exposures, continue the mission and reduce demand smoothly. The
predictive ceiling is now a soft actuator goal: during running regulation use
floor=min(current_verified_request,actual+0.5C), then limit downward movement
to0.5C per30s after verified readback. Configured demand cap remains binding.
Do not chase a hot actual temperature upward. Apply the same taper during
SETTLING recovery; remove the hot-ceiling bypass of the30s decision gate.
Native FTC protections, lease expiry, identity/native-priority checks and
telemetry failure handling remain. Existing stale/invalid-feedback soft39.5C
fallback is a separate data-loss path, not a temperature-triggered abort.
Continuous compressor operation cannot be guaranteed when native minimum output
exceeds demand or actual has already overtaken the request. The trial observes
this directly; no external stop is commanded merely for a warm supply reading.
Operator clarifies priority explicitly: (1) keep actual supply below40C;
(2) produce requested kW within that thermal envelope. Temperature is a higher
priority regulation objective, not a mission-abort trigger. Report actual
delivered power and thermal-limited state instead of claiming unmet power is a
fault or letting accumulated power deficit override the thermal constraint.

### Shared floor circuit and remaining prediction limit — 2026-10-11
The operator confirms that VP1 and VP2 feed the same floor-heating circuit.
Their controllers are independent, but their thermal load is not: one pump can
change the return conditions seen by the other. The dual6/5kW experiment must
therefore report individual and summed delivery, each return/flow measurement,
and temperature-limited intervals. Opposite power movements alone do not prove
controller hunting; source timing, smoothing, warmup and shared load are alternative
explanations. Any future house-level allocation should prioritize the common heat
request within each pump's temperature constraints rather than assume fixed6/5kW
is always the best split. This coordination is not implemented by this Mode OTA.

Code review also identifies an unmodelled actuator delay: thermal prediction uses
60s plus source age, while the0.5C/30s taper can take several minutes to move a
high request to its eventual limit. It does not explicitly include that remaining
slew time. Frequency response begins before all steps finish, so simply adding
the entire slew time would not be a validated model either. Future identification
should fit the measured response to the actual bounded request trajectory. No
mid-trial firmware changes were made to test this hypothesis.


## 2026-10-12 — user-authorized fixed60 candidate
Extend v2 flow validation and host encoder from45C to60C; GET09 maximum55C to60C. Preserve leases, readback verification, restoration and EFFECT behavior. Build separate build-fixed60 candidate, keeping deployed artifacts intact. Test6000 accepted/applied/restored,6001 rejected, encoder boundary and existing sanitized host regressions.


## 2026-10-12 — VP2 fixed60 plateau repeat
VP2 repeat of fixed60: compose only the already-tested Mode into VP2 baseline, preserving its Common/Dispatcher/BL2 and all other chunks. Verify C OTA1551 cuts and actual ARM before transfer; preserve VP1 firmware. Trial VP2 fixed60,VP1OFF; stop after180s unchanged Hz>=90 with>=10 distinct source generations, or50C actual/1800s; restore both. Passive DHW wait before heating. Log brine and source age; compare transitions with VP1 without assuming identical starting thermal state.


## P0080 A3 frequency comparison — 2026-10-12
Add service16/17 after existing27/28/18/19. Preserve exclusive retry ownership and FAST rounds between services. Publish raw/value validity/age/status/completion/ever in unused input372..383. GET04 stays independent. Update only Common+Service on VP2 with all other installed chunks byte-identical. Repeat60C with stop50C,30min or high-frequency plateau180s; restore both originals. A3 timestamps represent reply completion, not underlying acquisition.


### Dense A3 follow-up 2026-10-12
Priority automatically only when controller ACTIVE fixed-flow target6000:16,17,16,17 then one rotating background27/28/18/19. Decide next operation at start boundary, never interrupt retries. Leaving60C restores normal six-code queue; no TTL extension. Background samples can expire honestly. Test existing regressions, explicit scheduling/exit and actual ARM composite. Preserve VP2 installed chunks exceptService. Repeat trial with restoration.


## 2026-10-12 — prioritize host diagnostic17 after normal refresh
Use existing bounded diagnostic mailbox rather than a new firmware profile/ABI. Current diag_finish starts normal FAST plus an ordinary service, delaying next queued diagnostic until that extra service ends. Permit a queued diagnostic at service READY only after all eight FAST replies have completed. Keep existing DONE admission, full exclusive A3 retry sequence, max10 attempts,30s job bound,1s quarantine and IDLE-only control gate. No interleaving inside an A3 job, no change to retry timing or native SET traffic. A finite host runner submits diagnostic17 for~3min while both pumps remain in curve, then stops and verifies ordinary services resume. Retained TTL flags remain honest for background services. Common-only composite preserves all installed other chunks/BL2. Before live: host arbitration test, actual ARM composite regression, scoped byte/manifest/layout assertions. Live count new bounded jobs, pending->completion behavior, generations, temperatures and communication counters; do not infer new acquisition merely from repeated cached replies. Expected upper useful cadence~7.3s per17 (~8/min) from measured5.1s A3+2.15sFAST, to be measured rather than promised.

Live qualification found a composition omission: D2's preserved584-byte Dispatcher predates P81 mailbox, so FC04addr600 was rejected beforeanydiagnosticwrite. Correctwiththeexisting672-byte P81 Dispatcher, unchangedsource, as a second dispatcher-only OTA frominstalled86d693a9. All otherchunksremainbyteidentical. Extendcompiledtest throughactualModbusread600/616 andwrite600, includingrejectionatcontroladdress300; directCommonAPItestingalonecouldnotdetectthis.


## 2026-10-12 — target-only Service during supervised fixed60
ReplaceexperimentalpairedServiceprioritywithA3decimal17onlywhenctlstateACTIVE,modefixed-flow,appliedtarget6000. Keepordinarysixcodequeueoutsideconditionandresumeitspositionafterleavingexperiment. EveryoperationretainsfullFASTrefreshbeforeit,exclusive1000msretry,10attemptbound;Common/control/diagnosticgatesunchanged. ComposeonlyServicefromfreshbuildagainstinstalled5fc25d43;verifyallotherchunksbyteidenticalandARMexports/layout. Hosttestscoverselection,repeat17pending/timeout/rearm,exitandcontrolarbitration;actualARMchecksfinalcomposite.

Hostrunnerusesdocumentedcontrol300,180sleasewith60srenewal,peerOFF,verifiednative60C,actual50C/1800s/highplateau180sstopsandfinallyrestoresboth. ReadService378..383coherentlyandonpendingpollsoverModbus;theseareRAMreadsanddonotinterleaveCN105. Highratepollinginsidethemainobservationsprovidesjobgenerationandpending/completiontimingswithoutthreadscompetingforthebus. Primarymonitoringcontinuesatafewseconds. Analyzechangetimeintervalsagainstminutegridandlookforresolvedoff-grid1Hz/2Hzchanges;7secondresolutioncannotexcludeintraframechanges.


## 2026-10-12 — four constant measured-delta series
P0080 scoped candidate: manual v2 flow command/readback/host encoder max6500; leave DHW6000/EFFECT5500. Experimental Service selects17 for ACTIVE fixed-flow or ACTIVE OFF at operation boundary, keeping fullFAST,1s exclusive retries/max10,TTL,cursor and allcontrol arbitration. All other firmware sources untouched. Composite changesMode+Service only from installedVP2 manifest33143fde; preserveVP1c7a0fbcb and BL2/otherchunks. After controlled trials and native restoration, restore prior VP2 modules via addressed OTA and verify ordinary queue.

Host state machine: preflight/save originals; VP1OFF throughout; VP2OFF cooling until fresh~30C, and minimum900s verified compressor-off between series. Four series actual+500/+1000/+1500/+2000cC, from~30C up to firstactual>=4500. Upper requested6500. Retarget only on newfresh supply generation and changed>=50cC, once previous accepted/applied/native readback is verified; preserve original session snapshot. No periodicminute retarget; renewsame command only forlease. Poll coherentA3/17 allphases and normal primary telemetry, record actual native delta, sourceage and everySETtransaction. Do not equate replycadence with underboard acquisition. Directretarget canlower8/min; report actual cadence. NativeOFF<->fixed transitions requireAUTO/IDLE; verify originalcurve then enternew mission, no hidden changes. Pause starts after confirmedHz0/power0. Finite series bound60min; finite cooling bound90min afterminimum15; failure toreach45 or~30 is explicit partial evidence, not a fabricated completedrange. Each state has boundedentry/readback,identity,lease and primary telemetry guards. On any exit restoreboth viafinally. Ordinary DHW priority must be preserved outside explicitly commandedOFF; heatingseries that entersDHW is markedinterrupted, no forceDHWsettings.

Tests: hostcommand bounds6500/6501, unchangedothercaps, directmovingtargets/originalsnapshot/lease/readbackfailure; ServiceOFF/fixedfocus and AUTO/IDLE/EFFECT normal; integratedretargetmidA3 preservingexclusiveattempts and completion/primaryprogress; fullASan/UBSan and finalARM. Hostrunner syntheticfixture tests for fresh-generationtargeting, pendingcommands,45Cstopbeforewrite,minimumOFFpause,30Cstart,timeout/restoration. Livequalification65 only when needed and verified, never bypassnative readback tocontinue.
# 2026-10-12 — delta-series continuation after native DHW selection

Series1 reached45C; series2 was not started because restoringAUTO after the
902s cooling pause selected nativeGET26mode1(DHW), even though GET04/flow
remainedzero. Bothoriginalcurve settings were verifiedrestored. Preserve this
interruption evidence. Extend only the hostrunner with validated continuation
from a completed prefix, matching saved originals and verifiedrestoration.
Do not repeatseries1. NativeDHW is allowed in baseline/waiting only; wait without
heat commands, then obtain a new900sOFFpause andactual<=30.5C. A priority
selection beforestage_start defers the stage rather than falsely logging it as
started. Keep the existing heating-stage boundary unchanged. Limit priority
waiting and repeated deferrals. Firmware remainsunchanged. Tests must cover
prefix validation, pendingDHW producing no heat command, and correct remaining
series dispatch/restoration on error.


### Completed sweep and bounded cleanup

Four endpoints reached under existing stop/pause gates. Final native-state
restoration and prior-profile OTA are distinct verified steps; both completed.
Normal-service recovery uses individual success generations plus error counters,
not terminal-job count. Physical results support phase-dependent startup/holds
and native reductions, not a universal proportional delta law. Frozen integral
hypotheses failed on later runs. See final changelog and local report; no EFFECT
algorithm changed. All raw command/evidence chain links retained.


Nondecreasing +10 trial (2026-10-12): MonotoneTrial overrides requested_target
with max(previous accepted target, fresh supply+1000cC). Busy/rejected
commands cannot advance the accepted floor. Command boundary rejects any
FIXED decrease; AUTO restoration remains permitted. Stop at actual45C before
another write; maximum55C. Single-run cooling has no mandatory15min pause.
Offline runner and boundary fixtures passed. Live oscillation remained:
three84→70 drops, zero target decreases,27:26 to45C. See monotone trial report.


## Two-loop EFFECT follow-up, 2026-10-13
Replace effect_fast's acceleration-memory controller with a bounded Hz-target controller. RAM-only affine model starts a=135W/Hz,b=-1090W; a represented in0.1W/Hz. Stable independent120s windows update bias10%, capped100W; comparable plateau pairs >=15Hz apart update slope5% only after repeated agreement. Slope70..200W/Hz are engineering bounds; retain prediction at currentHz on slope change. Learn actual A3/16, never desired A3/17. Gate new coherent power generations, fresh Hz/supply/return/flow, stable temperatures/frequency, heating and no heater flags; pause invalid windows, retain learned model across sessions until reboot.
Outer initial Hz target inverse affine; power-feedback trim at most1Hz per60s only when near requested frequency, no thermal/oscillation limiting. Inner loop uses valid A3/17 (<60s), one decision per new generation plus >=30s cadence, +/-0.5C regular correction, no boost from oneHz fall. Near goal hold applied setpoint instead of chasing measured temperature. Large alternating A3 changes enter120s applied-setpoint hold, temperature priority still active; cooldown avoids permanent freeze. Startup retains existing bounded qualified entry policy.
Actual40C soft priority: predictive entry near39C, gradual lowering,90s cool dwell before release, no fresh startup boost on release. Preserve native pause/DHW/lease/restore/SET readback. No below-native safety bypass. Model learning frozen when thermal or oscillation limited.
Add direct EFFECT retarget acceptance during quiescent ACTIVE mission, preserve original snapshot/model and reject ambiguous in-flight changes. Read-only diagnostics308..319 use existing Common->Mode route, no export-layout change. Installed service queue left unchanged to preserve brine and A3 actual; async ages respected.
Verification: model unit tests with temperature-confounded pairs/duplicate generations/poll invariance; inner target hold, loneHzdrop, pendulum hold, thermal release, retarget/restore; existing control/transport/feedback/session tests updated only for changed regulator behavior. ASan/UBSan host tests, ARM built artifacts through public API, Mode<=12KiB/RAM<=4KiB, OTA composition against pinned manifests, preservation of other chunks. Then serial OTA, both native restoration verification, VP1 only6kW then5kW supervised withVP2OFF and finalboth restore.

Fixed-slot implementation note (2026-10-14): the completed controller initially
used12784/12288bytes in Mode. Its RAM-only affine model is now linked into the
underused Service slot and reached through two private veneers immediately after
Service's ten public veneers. Public exports, addresses and layout ID remain
unchanged; Mode and Service form one version-coupled update and must be composed
together. The complete manifest already rejects a mixed or partial image set.
The first composed build uses Mode11352/12288bytes and Service2728/4096bytes;
their RAM use is1152/4096 and352/1024bytes respectively.

### Two-loop build qualification follow-up, 2026-10-13

The initial implementation exceeded Mode12KiB by1976bytes. Grouping private
controller state for a single reset and using bounded32-bit sums/rates removes
unnecessary code without changing exported ABI, fixed flash/RAM boundaries,
or native safety handling. Current Mode uses11760/12288bytes. Diagnostic power
rates use whole-second elapsed time; they are not regulator acceleration inputs.
Sampler power is bounded to2MW before64-sample32-bit accumulation (far above
this17kW unit and above the validated telemetry range).

Full composed ARM testing found D1's installed fixed60 Service has only the
older service set and returns zero for372–383. Therefore D1 requires Mode+Service;
D2's frequency-focus baseline already has16/17 and needs Mode only. Both resident
BL2 images, Common, Dispatcher and other modules are byte-preserved. This
supersedes the preliminary Mode-only-both plan. Layout/export order is unchanged.

Host ASan/UBSan regressions, model numerics, public ARM controller/Service tests,
and snapshot routing pass. The old acceleration-predictor assertions were
replaced with explicit frequency-loop tests; native guards, restoration,
leases, thermal cadence/floor and old-source gates remain tested. Composed ARM
service replies are injected through exported service APIs at45s cadence.

Live plan: VP2 OFF, VP1 EFFECT6kW15min then5kW15min without AUTO between targets,
finite180s leases renewed at55s, original native states restored in finally.
Actual40C remains the higher-priority soft constraint; a brief overshoot does
not terminate the mission. This test establishes observed behavior, not universal
stability or an exact plant model.

## Braking integration and dual quarter trial — 2026-10-14

Mode-only replacement, preserve device-specific baselines5903105e/f3ed161c and BL2/Common/Service. Permit fresh-qualified A3 running braking down to supply−1C when far above Hz goal,−0.5C near it. No ordinary negative braking at<=25Hz; release toward supply+0.5C when within3Hz of goal. Reduce demand at most0.5C per60s; bounded upward release0.5C per decision. Thermal40C priority may use−1C floor even at lowHz; native protections remain. Stale sources do not grant negative braking or upward demand. Pause still gets positive restart demand. Two independent regulators execute the same2/4/6/4kW steps at wall-clock15min boundaries; native waits/DHW do not extend quarters. Leases renewed, all readbacks checked, originals captured and restored finally. Tests: host sanitizer regression, focused braking/release/stale/min-Hz tests, composed ARM ABI/readback/thermal checks, slot fit, OTA manifests, then one-hour live evidence.

## Requested45C actual-supply priority — 2026-10-14

User replaces40C actual-supply limit with45C. Requested setpoint ceiling remains55C. Implement one named compile-time actual-temperature policy, deriving the existing anticipation/release offsets from it. Do not combine this threshold change with the separately proposed thermal/Hz redesign; the old latching weakness remains explicitly documented. Preserve historical40C host fixtures under explicit test-only compile definition and add production45C boundary coverage plus actual-image ARM qualification. Build a new offline image; no further hour test was requested in this message.

## 2026-10-14: continuous 45C envelope candidate
User requests remaining controller improvements. Replace sticky thermal latch with current forecast/actuator constraint; continue Hz law underneath. Upward requests limited to 2C/decision far from Hz goal, 1C intermediate, 0.5C near; reductions remain 0.5C/60s. Ordinary negative delta allowed above20Hz, with earlier brake release below24Hz when target is falling. Thermal priority overrides low-Hz protection. No native safety, ABI, lease, restoration or live device change. Qualify synthetic behavior and composed ARM binaries before any installation.

## 2026-10-14: EFFECT v3 tracking refinement after the autonomous energy trial

The 105-minute pair trial showed that frequent supervisory retargets and the
local actuator dynamics must be treated separately.  A changed watt target must
not erase the bounded per-device frequency correction learned during the same
running session.  Retargeting preserves that correction and the RAM-only affine
model, resets only reversal classification, and transfers the new watt target
directly into a new Hz goal.  A planned reversal therefore cannot be mistaken
for an oscillation caused by the plant.

The inner loop records the A3/17 target present at every verified flow change.
It does not stack another change in the same direction for one native minute
while that target is unchanged.  Once A3/17 moves in the requested
direction, normal cadence resumes; after the response window expires, best
effort also resumes rather than declaring failure.  This is bounded response
memory, not an accumulated integral actuator command.

Direct retargeting no longer discards an otherwise qualified model window.  A
physical change in actual Hz, temperature or water flow breaks that window
through the model's existing range gates.  Coefficients still require a stable
120-second window, and slope still requires repeated comparable plateaus; rapid
supervisory changes therefore do not fabricate learning evidence.

Upward and downward dynamics are distinct.  Upward steps retain the existing
0.5/1/2 C bounds.  Ordinary reduction is 0.5 C/min near the Hz goal and may be
1 C/min when more than 10 Hz above it.  A falling native target does not freeze
that far-above-goal reduction.  The 45 C actual-supply priority may reduce by
1 C every 30 seconds; it remains a regulating action and never commands OFF.
Near the goal, at the observed low-frequency boundary, or with stale source
data, the conservative existing behavior remains.

Diagnostics version 3 retains every existing register.  Phase/reason now
distinguish tracking, response wait, configured request ceiling, observed
minimum-output boundary and thermal limiting.  Input315 keeps bits0/1 and adds
direction/response/minimum/cap/tracking bits.  These reports are advisory plant
state for the Shelly planner; they do not weaken native guards or convert an
unreachable request into an abort.

## Pair-energy supervisor 1.4.1

Keep the Shelly supervisor constant-time and array-free. Every 30 seconds it
derives pair power from remaining cumulative energy, response lag and the
current/next deadline, then clips that demand to the observed conservative pair
seeds of +2.0/-1.25 kW per five minutes and
observed capability. EFFECT target changes dwell at least 120 seconds except
for a limiter-driven reduction; identical writes remain lease renewals through
the existing `equal_intent` control path.

Treat EFFECT phase 4 with reason 4 or 15 as measured saturation. Learn a
per-device temporary cap from actual power, inhibit positive windup, expose
reachable power and forecast energy error, and keep delivering best effort.
Invalid or stale samples cannot reopen a cap. Learn VP1/VP2 response gains only
from fresh stable HOLD observations.

Split every 500 W pair command exactly between two 500 W device requests,
alternating the extra share unless learned gains identify the more productive
pump. Integrate both power streams independently and split a trapezoid at the
exact 900-second boundary. Safe lease expiry and verified native restoration
remain unchanged. This supervisor change does not alter EFFECT firmware.

A missing RPC or a decoded power age of 60 seconds or more suspends planning
and retargeting. The interval is accumulated as unknown rather than zero, the
last limiter phase/reason is retained, and an already accepted pair is renewed
with exactly the same targets once either write is 55 seconds old. `lastPlan`
is intentionally left expired so the first subsequent complete fresh pair
replans immediately. Because integration needs two fresh endpoints, the
recovery sample closes no invented trapezoid; the next fresh interval resumes
normal accounting.

This is current+next cumulative-deadline control, not the full four-quarter
candidate-grid MPC used for offline exploration. Longer-horizon L4 planning
still selects quarter energy goals; Shelly executes them with scalar state.

## Combined EFFECT module placement — 2026-10-14

Mode exceeded its fixed 12 KiB budget when the final regulator and model were
linked together. Keep the regulator and public control API in Mode, but build
`effect_model.c` into Service. Two private, fixed Thumb veneers follow Service's
ten public exports: `effect_model_op` at `0x08012069` and `effect_model_tick` at
`0x0801206d`. They do not extend the public export list or change layout ID
`3833993797`.

The private edge makes Mode and Service an atomic feature pair even though OTA
transfers them as separate chunks. Compose both over each device's own installed
baseline, stage both, then commit one manifest. Never deploy only one of them.
The final pair uses 11,928/12,288 bytes in Mode and 2,728/4,096 in Service.
BL2, Common, Dispatcher, Drift and both debug chunks remain byte-identical to
the corresponding installed device baseline.

The final source policy separates freshness from speed. A coherent value with
age <60 seconds remains usable; only age <15 seconds permits the quick law.
Older usable data can make at most a conservative 0.5 C/minute positive move.
The regulator represents minimum output, request cap and stale source directly.
Actual supply has a 45 C priority envelope independent of the requested-flow
cap; thermal braking is bounded to 1 C/30 seconds and ordinary braking is
slower. The demand floor cannot lift a request already within its cap.
