# P0080 function design

## EFFECT + rolling energy v4 functions

- `modelIdentity` reads the full device identity and derives the exact UID-bound
  KVS key; duplicate or malformed identities block startup.
- `modelRecord` accepts only the versioned gain record with exact UID, field
  order, ranges, evidence count, stability duration and age.
- `loadModel`/`seedModel` wait through the startup allowance, verify diagnostic
  schema 4 and use C077 only when a valid saved gain exists. Validation mode
  marks seeding complete without a holding-register write.
- `sampleModels`/`saveModel` persist only gain after qualified stable evidence,
  compare-and-swap and exact readback. Firmware bias/trim never enter KVS.
- `acceptPlan` installs or stages a strict four-quarter KVS plan atomically;
  revisions, boundary alignment, expiry and Wh ranges are checked before state
  changes.
- `integrate` books each pump independently, splits an interval at an exact
  quarter boundary and records stale intervals as unknown.
- `plan` combines remaining cumulative energy, bounded debt, response lag,
  learned response gain, ramp reachability and thermal capability into one
  scalar pair command, then divides it between pumps.
- `afterPlanRefresh` keeps production commands behind fresh paired feedback.
  `VALIDATEONLY` instead proves the completed read/parse/planner path and stops
  before `commandBoth`, including when post-flash feedback is not ready.
- `validate_observe` snapshots Script 7, serial and both KVS keys before any
  mutation; it restores all prior state on failure and installs exact stopped,
  disabled production code only after successful runtime proof.
build.py: define fixed slots/exports, generate linker and veneer files, compile each slot and create full install + per-slot artifacts and manifests; fail overflow or unresolved imports.
bl2 main/cn_service: boot identity, validate/init modules, polling UART framing, system command routing, WAIT/OTA baud transitions and watchdog. Calls Common only when full manifest valid and normal.
module_validate/module_load: check full-slot CRC, headers, ABI, RAM bounds and initialization lengths before calls.
ota_handle: strict bounded frame decoder, HELLO/BEGIN/WRITE/COMMIT/STATUS/EXIT; target/current-image validation; duplicate recognition, no uncertain write retries.
flash_erase/flash_write: narrow updatable-page checks, RDP1 and WRP/PCROP/context gates, RAM-only busy handling, no option/BL2 writes.
Common maintenance_ready: fresh GET26/28 gate plus idle controller and transaction.
Host sender: deterministic plan; addressed handover, peer WAIT, baud switch, staged binary frames, ACK/status checks, finalCRC verify; explicit CLI live gate and logs/cleanup.
Tests cover bounds, duplicates, interruption, native gate, independent modules and preserved EFFECT semantics.

Implemented details: native handoff uses fresh GET26 curve and GET28 permission observations; no automated restoration command. Protocol uses232 firmware bytes to keep252 wire bound after slot/offset metadata. Service state stays in service chunk while Common owns the bus. No unrestricted RAW commands added. CRC32 is integrity-only.

Physical OTA follow-up: Sender.transfer waits2s for COMMIT/EXIT full-image validation and records that protocol1 status CRC is not exact-version proof. Added delayed ACK host regression. Firmware unchanged.

Protocol2 correction: normal and ota_handle compute prefix56 CRC; wire/version gate bumped. Host frame/decode/plan/status/transfer updated. Detailed scope and tests in bl2-v2-design.md.
# Direct fixed-flow continuation — 2026-10-10

- ctl_submit: accept next-sequence flow-only replacement in eligible active fixed-flow session; preserve initial original/touched/saved, begin fresh guard reads and lease. Existing retry/renewal branches unchanged.
- ctl_reply: validate replacement native mode/power/boost/old target and flags, construct FLOW-only plan without replacing original; verify mode again immediately before SET. Failure uses existing restoration.
- ctl_init / restore_plan: clear replacement flag; no new exported functions or ABI changes.
- tests/test_control.c: extend independent native model to assert replacement never emits MODE/POWER, rejects unsafe/pending changes, and restores the initial snapshot on AUTO/expiry/failure.

## P0080 brine pump telemetry
svc_init/link/tick: operate on all four sample slots; svc_due/advance retain bounded exclusive arbitration across27,28,18,19. svc_read adds87..98 diagnostics without changing existing addresses. telemetry get uses a new pump helper reading those diagnostics; returns range-checked step or RPM-derived boolean with source age/generation and status. No actuator writes. Existing tests extended for scheduling, invalid/stale/zero and snapshot compatibility.

## P0080 EFFECT scheduling correction
cn_tick: at an idle service boundary with pending controller work, reserve complete FAST refreshes when measurement age reaches the refresh budget; retain exclusive wire ownership, A3 sequencing and existing hard-invalid controller guards.
Existing test_cn105.c: add integrated normal-pump wire model using the real controller, effect sampler and A3 scheduler, prove entry/readback/AUTO at realistic reply latency. Include stale/link/native-mode rejection. No new exported ABI or register schema.

P0080 freshness: tele_tick/cn_tick expire measurements at60000ms; effect_feedback_tick uses the same boundary. control effect_collecting recognizes PENDING/WARMUP for suspension/recovery, while effect_feedback_ok requires qualifying pairs and age<60000ms. effect_decide preserves state during WARMUP. Public signatures and ABI unchanged. Tests cover exact expiry and no-write warmup recovery.

Fast demand: new private effect_fast(m,flow,t) computes bounded temperature demand with power/temperature anticipation; existing effect_decide selects it only forcap>4000. effect_capture permits immediate first fast decision. effect_pause_demand uses mild demand without cumulative latch in fast path. ctl_submit accepts fast cap<=5500; ctl_tick latches actual>=4000 as restore reason TEMPERATURE_CAP forfast sessions. Host encode accepts max_flow55; test exact5500/5501 boundary. Existing public interfaces unchanged. Add fast-law tests to existing test_effect and exercise real scheduler using55C cap in test_cn105. Scope P0080 only.
Thermal refinement: effect_fast retains private temperature_limited hysteresis, clamps demand39.5C, reports EFFECT_LIMITED/EFFECT_TEMPERATURE_CAP when power demand is constrained. ctl_tick actual-temperature restore threshold changes from>=4000 to>4000, allowing temperature regulation at the boundary; native protections retained. Tests distinguish40C retained mission versus40.5C protective restoration.
Persistent fast control: fast_session selects opt-in behavior; soft_lower identifies only a reducing FLOW action<=3950; recover_wait retains mission/snapshot and clears wire action state after communication failure. ctl_link_lost/timeout enter this wait for fast saved sessions. ctl_tick schedules bounded fallback without ready power, and snapshot resynchronization after fresh data returns. ctl_observe tolerates naturalDHW only forfast, while external ownership/power/mode guards remain. No new public exports.

## P0080 smooth capture — operator refinement 2026-10-10
The852841df physical quarter-hour test oscillated after abrupt55C-to-supply+1C braking. Replace ordinary boost/capture discontinuities with a retained capture state: initial55C is allowed, sustained positive power slope or proximity to target starts gradual taper; thereafter correct the existing demand with bounded small steps and derivative damping, without jumping back to55C on power deficit. Trend is filtered and preserved across normal partial FAST refreshes. Temperature protection and degraded-feedback reduction take priority over smoothness. This is an empirical candidate, not a proven FTC model or stability claim. Verify response sequences, slope/noise handling, no repeated boost, existing recovery/restore, ARM artifact and fixed-slot fit. No new ABI or tracked paths.
Changed effect_fast: retain capture state, filter slope, bounded taper and small ongoing correction. effect_init resets new private state; effect_wait preserves trend during ordinary pending refresh. Tests cover acceleration/taper/deficit/temperature precedence.

## P0080 lease renewal during effect adjustment — 2026-10-10
- ctl_submit: expand equal-intent renewal admission to an already-applied EFFECT mission in APPLY (saved and applied==accepted). Only command/accepted/applied sequence and lease timestamps change; current wire/action/regulator state is retained. Reject initial unapplied and changed-intent requests as before; no new public function or ABI.
- tests/test_effect.c renewal_test: independent native model verifies renewal at pre-SET guard and post-SET/readback boundaries, duplicate idempotence, changed-intent rejection, preservation of original settings and lease restoration. Legacy control and startup tests remain authoritative.

## P0080 Hz-leading controller identification — 2026-10-10
Operator authorizes an hour of theory/data/live iteration toward a monotone6kW response, measured supply<=40C. Historical analysis found30–45s lag of rolling thermal power behindHz and a poor universal delta-only model. Trial host law uses35s Hz leading correction110W/Hz and bounded actuator-rate feedback from desired acceleration(error/90s) versus measuredHz acceleration. C candidate uses60s acceleration to suppress staircase alias, suppresses early braking when prediction<target−1.5kW, and freezes downward adjustment whenHz falls near/belowgoal. Initial45C demand matches current host pilot; configured55C remains an upper bound. Ordinary15–59s measurement age holds rather than abrupt reduction; actual/forecast thermal protection remains. New history is module-private; no ABI change. Native host/ARM/OTA tests and physical evidence required, empirical precision limited by0.5C sensors.
effect_fast changes to bounded leading-power/Hz acceleration law; effect_init/effect_wait reset private history. Existing control renewal fix bundled; control thermal fallback changes only15s pending behavior, retainshardstale handling. Tests cover quantizedHz, no early/falling brake, stale hold, thermal priority, mission restoration.

P0080 refinement during host pilot:60sHz slope can retain old acceleration after recent35splateau. Falling recentHz freezes braking up togoal+300W; flat recentHz freezes braking only belowgoal−300W. Progressive thermal commandceiling3950+3*max(0,3950−Tlead10s) replaces ordinary38.5Ccliff; actual>=39.5 or30sprojection>=40 retains protective3950override. Cap alwaysrespected, missionretained, no integral accumulation behindbarrier. Physical40C hostlimit retained. New guards covered by host/ARM tests; empiricalbarrier is not a guarantee of zero physicalovershoot.


## P0080 early startup and fine correction continuation
- effect_pause_demand: add fresh-pair SETTLING startup path and repeated thermal limiting, mark startup requests distinctly from zero-Hz pause requests. No full power-ready claim.
- effect_pending_demand: preserve the private demand kind (0 none,1 pause,2 startup) for control guard qualification. Existing module-local API only.
- effect_verified: mark startup captured only after successful readback, preserving retries/discard behavior.
- effect_fast/effect_init/effect_wait: smaller near-target quiet band and bounded sub-step carry with saturation/pause/gap resets; no additional unbounded integrator.
- pause_demand_ok/control guards: recognize kind2 only with fresh coherent heating data, preserve all existing guard/readback/restore paths. Tests cover absent/aged pairs, native mode/Hz transitions, unsent cancellation and already-sent completion.
- Existing host/native/ARM suites plus extended physical capture harness verify one continuous mission, timestamped quarter-hour and post-capture metrics, strict energy coverage and cleanup.

- build.py/main: select -Oz for mode, retaining -Os elsewhere, because startup plus fine-correction exceeded its fixed flash budget by232 bytes. No linker layout or public ABI change. Exact ARM image and slot-bound checks are required.

Fixed-slot refinement: -Oz produced no size improvement, so retain the original -Os compiler setting. Consolidate effect.c private regulator variables into one private state structure and reset it as a whole in effect_init. This removes duplicated per-variable initialization/address loads without changing public structs, RAM reservation, function signatures or behavior. Verify the complete host/ARM suites and module size.

Private history(), supply_rate() and thermal_ceiling() are shared by startup and normal regulation; they retain the existing35s/60s history and thermal equation. Grouped effect_state replaces separate module globals, with identical external diagnostics and whole-state initialization.

### Entry transition contract follow-up
`ctl_next` / `ctl_tick`: an unsent MODE_FLOW or FLOW action whose coherent feedback becomes temporarily incomplete must yield polling and requalify before write, preserving initial snapshot and lease. The 2026-10-10 physical attempt153111 reached BAD_FEEDBACK before applied; regression reproduction and a focused guard fix are required before the next trial.

### Atomic entry / predictive capture contracts
`effect_entry_demand`: choose a qualified target immediately before initial combined SET, use fresh native operating-mode guard, return0 to defer; preserve original snapshot. After transmission keep the target fixed through mode and target readbacks. `effect_fast`: distinguish current power lead from future actuator-response forecast; suppress new gas during continued measured rise and allow bounded earlier braking. Dedicated atomic-entry tests cover whole transactions; post-entry fixtures intentionally start at target power to isolate subsequent controller behavior.

### thermal_ceiling signed-margin feedback
Replace the fixed3950 override after the observed40.5C boundary breach with a3900 center and signed above-center correction. Retain shared use in atomic entry, early startup and running regulation, and ensure forecast protection can only reduce the result. Tests must assert all three steady offsets and that forecast cannot raise a lower limit.

The shared ceiling is bounded below by 3000 cC before conversion to an unsigned requested temperature. This prevents wraparound for high but admissible supply samples; it does not raise a lower native-pause request.

## Response memory and recovery functions — 2026-10-10
`effect_fast`: retain bounded/decaying positive lead in private state; use forecast-aware plateau guard and projected-power near-target suppression; permit1C recovery steps for fresh underpowered low-demand observations. All actions still pass the unchanged thermal ceiling. Clear retained lead on thermal clipping or evidence inconsistent with continued acceleration. `history` and `effect_wait`: reset private lead with existing history reset/pause. `effect_init`: aggregate initialization resets the added field. No public signatures or telemetry maps change. Tests extend existing predictive and actual-ARM suites. If mode needs size savings, qualify a mode-only build compiler flag and retain exported veneers and module identity behavior.

Final build detail: `build.py:main` now applies `-fno-inline-functions-called-once` only to mode to keep the additional private state/logic within12KiB. All other module binaries are byte-identical to the installed base. Step bounds are applied once after carry, eliminating redundant earlier clamps without relaxing the final bound. Final linked ARM regression coverage passes.

## 2026-10-11 source-aware EFFECT
- effect history: independent timestamp/generation tracks from existing
  tele_snapshot(8 Hz,3 supply), with duplicate/stale/gap filtering.
- effect regulation: one persistent algorithm at every configured cap; soft
  predicted-temperature acceleration constraint plus existing hard ceiling.
- control recovery: preserve restoration on link loss; resume interrupted entry
  only through native guard and combined mode/temperature readback.
- effect_mode_matches: distinguishes interrupted initial entry from an established
  mission, allowing guarded initial retry but rejecting later external mode change.
- source history uses two16-point histories, explicit generation validity (zero
  and wrap are legal),>=5s stored cadence,35/60s trend selection and60s gap reset.
- thermal acceleration ceiling is60mHz/min per centidegree of margin below a
  forecast39C supply, forecast horizon45s plus measured source age. Desired rate
  remains bounded to +/-12Hz/min; the existing hard requested-temperature ceiling
  still dominates. The soft limit is empirical and requires physical validation.

- tools/analyze_source_trial.py: offline typed-source/capture timing analysis,
  separate instantaneous/windowed power series, bracketed energy integration,
  generation-aware source-time view, endpoint coverage and PNG/SVG report.
  No device or transport imports; incomplete evidence remains explicitly partial.

## Predictive envelope continuation — 2026-10-11
- thermal_forecast: supply trend and source age -> conservative60s forecast;
  no negative-slope credit, integer calculation only, no side effects.
- thermal_ceiling: fresh established source trend -> continuous predictive
  requested ceiling; otherwise original conservative formula. Actual hot-supply
  correction, configured cap and unsigned-wrap guard retained.
- effect_fast/startup_target: pass existing independent water history to shared
  envelope; soft acceleration uses same forecast. Source-only stale data must
  not trigger initial upward demand. No public ABI or shared structures change.
- New tests/test_thermal_envelope.c: behavioral regression for flat38C deficit,
  rising/aged source prediction, insufficient history, cooling recovery, stale
  pair/source hold, hot supply and lower configured caps.

User's later thermal correction supersedes the immediate signed actuator clamp:
`bounded_demand` limits any running thermal/power taper to0.5C per decision and
uses min(current,supply+0.5C) as downward floor, then honors configured cap.
`effect_fast` now has an unconditional30s gate; `startup_target` applies the same
bound and30s verified-write delay on established sessions. Signed thermal law
remains the soft goal, not a demand step below actual. No temperature-only abort.
`slope` uses const pointers instead of copying structures; `thermal_forecast`
splits the60s term with exact bounded32-bit arithmetic to fit the fixed slot.
Established-history release also requires a qualified>=20s short slope span.
`build.py`: Mode only adds-flto,-fno-schedule-insns2 and linker-u,memset;
retaining the freestanding support symbol avoids LTO dropping it before generated
structure initialization needs it. Module veneers/layout remain unchanged.
Final Mode12264/12288 bytes, privateRAM1128/4096. Other module flags unchanged.
The unknown-boot diagnostic remains constant1; transient temperature-limited state
is local rather than stored between decisions. Both changes preserve behavior.
The conservative fallback now shares the60s forecast with gain3 (flat38->42),
while qualified history uses gain8; incomplete positive history brakes earlier.

- tools/analyze_adaptive_dual.py: offline dual-trial analysis with independent
  per-device targets, source/capture times and deduplicated observations. Reports
  the strict actual<40C priority separately from power tracking, including time
  exactly40,>=40,>40 and>42C. Exposure is a measurement, never an abort policy.
  Distinguishes raw heat from rolling feedback, complete from partial energy
  coverage, observed compressor pauses from missing data, and verified final
  restoration from a still-running trial. Uses the adjacent offline source-trial
  math module; imports no live transport. --self-test produces marked synthetic
  fixtures including exact40C plateaus and telemetry gaps.


## 2026-10-12 — user-authorized fixed60 candidate
ctl_submit: v2 flow max6000. GET09 decode branch: accept max6000 for verified application/restoration. encode: v2 flow max6000. Existing test_control main and Commands tests cover new boundary and full session restoration. No new runtime functions or ABI.

Compiled verification also extends existing test_modules_arm.py with a build-fixed60 boundary/application/AUTO case; no runtime scope change.


## 2026-10-12 — VP2 fixed60 plateau repeat
Outer workspace update_fixed60_vp2.compose/main reuse the existing atomic OTA/cleanup. VP2Fixed60Trial reverses addressed roles, adds plateau detection and a local timed-stop file; tests check180s boundary,distinct generations,low-frequency exclusion and reset after Hz change. No new firmware behavior beyond tested fixed60 Mode; no ABI change.


## P0080 A3 frequency comparison — 2026-10-12
svc_read: expose two six-word records372/378, retained raw/status and per-code generation/age; svc schedule extends to16/17. cn_read routes372..383 to service; no other arbitration changes. Extend protocol simulation for six exclusive services and verify pending/timeout/stale/zero/high-byte raw behavior. Host runner logs coherent generation-checked records with each existing snapshot.


### Dense A3 follow-up 2026-10-12
svc_start_cycle selects priority indices4,5,4,5 then rotating0..3 when ctl_read256=4,263=2,275=6000. Priority cursor resets outside this mode. advance retains normal next_index. Extend unit and ARM scheduling tests, add standalone ctl_read stubs in pure telemetry tests. Host plateau uses both fresh A3 channels unchanged180s, not GET04 quantization alone.


## 2026-10-12 — more A3/17 via existing diagnostic mailbox
cn_tick queued diagnostic admission: also allow service READY with fast_index>=FAST_COUNT, before starting that untouched service job; preserve existing DONE path and all WAIT/RETRY/CONTROL boundaries. No new runtime functions or public command fields. Add regression to existing test_raw_diagnostic.c and compiled test_modules_arm.py for consecutive same-selector diagnostic jobs separated by a full FAST round and no ordinary A3 insertion; pending retries exclusive; finite host stop resumes background service. Local host runner submits only allowed read diagnostics while controller IDLE, captures pending/completion payloads and verifies curve settings preserved.


## 2026-10-12 — target-only fixed60 function changes
- svc_start_cycle(): chooseindex5(decimal17)onlyforACTIVEfixed60; preserveordinaryqueuecursoroutsideexperimentalcondition. NoABI,newregisterorcontrolgatechanges. Testselection,noneligiblemodes,targetchange,completion/pending/timeout,normalqueueresumption.
- Existinghostcn105andService/ARMtests: validaterealcompiledslotandcross-slotcontrolboundarieswithrepeated17.
- Outerworkspacetargetonlyrunner: extendexistingVP2fixed60runnerwithcoherent378..383sampling,wirependingcapture,completegenerationtimestampsandtarget-basedplateau. Reuseidentity/lease/readback/restoregatefunctions. UpdatercomposesServiceonlyfrominstalled5fc25d43.


## 2026-10-12 — moving-delta function changes
- ctl_submit/manual validator and ctl_reply GET09: allow6500cC, reject6501, preserveall othercontracts.
- modular control_command.encode: manualflow6500, DHW/EFFECTunchanged.
- svc_start_cycle: latch focused17 only while ACTIVE fixed-flow orOFF; retainordinarycursor/TTL/fullFAST/exclusiveretries.
- Outer DeltaTrial command/transition: addressedsequenceguarded fixed-flow/OFF/AUTO, preserveoriginalandnativeverified completion, finallyrestore.
- DeltaTrial observe/retarget: coherentA3generations plusfreshsupply,45Cstop beforeanynewraise, newgenerationand>=0.5Cchange thenonependingwrite.
- DeltaTrial cooling/series: min900s verifiedOFFbetweenfourruns, wait~30C, bounded60minrun/90mincool, phase-specificevidenceandpartialoutcomes.
- Scoped updater composesMode+Service and later restorespreviousknownmodules; unchangedBL2/others asserted.
- Offlineanalysis: per-series actualdelta and bracketedtargetHzchanges vsminutes; separatecommandtiming, firstcoldstart/ramp, publicationuncertainty.
# 2026-10-12 — host delta-series continuation

`load_resume(path)` validates a completed sequentialdelta prefix, original
settings and verifiedboth-device restoration; returns the nextseries and
provenance, with no device traffic. `wait_native_priority()` keepsVP2 in native
AUTO and VP1OFF, logs DHW state until ordinaryheating/idle mode; never issues a
temperature command. `run_stage()` returns a deferred indication for DHW before
stage_start, preserving its strictactive-heating boundary. `run()` dispatches
only remainingseries, reacquires a fullcooling pause afternativeDHW, and bounds
repeateddeferrals. `main()` validates newbaseline againstsavedoriginals and
records segment/combined completion separately. Addofflinecontinuation and
DHW-wait fixtures; firmware/OTA/API surface unchanged.


### Completed delta analysis and ordinary service recovery

Chain analyzer follows explicit resume metadata, reports independent stages,
all completion generations including unchanged values, observed source ages,
publication windows, grid compatibility, startup markers and actual delta.
Integral evaluator applies frozen exits to causal held samples with freshness
coverage and separate clocks; plotter consumes only resulting JSON.

RecoveryTrial rejects control commands. verify_service_recovery requires a new
valid completed generation per ordinary service code27/28/18/19/16/17 with
age<60s, bounded180s, preserved originals and IDLE/saved0/error0 on both pumps.
One recorded initial transition fault can reset success baselines once; it
cannot extend deadline, hide the fault or accept repeated failures. Counter42
is terminal jobs, not successful full queue rounds.


Nondecreasing +10 trial (2026-10-12): MonotoneTrial overrides requested_target
with max(previous accepted target, fresh supply+1000cC). Busy/rejected
commands cannot advance the accepted floor. Command boundary rejects any
FIXED decrease; AUTO restoration remains permitted. Stop at actual45C before
another write; maximum55C. Single-run cooling has no mandatory15min pause.
Offline runner and boundary fixtures passed. Live oscillation remained:
three84→70 drops, zero target decreases,27:26 to45C. See monotone trial report.


## Two-loop follow-up function design
- effect_model_reset/observe/predict/target/read: private RAM affine estimator, independently qualified120s windows; bounded bias/slope updates and pivot preservation; no hardware writes. Tests cover duplicate/stale/transient/temp mismatch and replay.
- effect_fast: replace prior acceleration memory with outer Hz reference, A3/17 admission, bounded temperature actuator and oscillation hold. Tests exercise meaningful changed behavior and existing thermal/ownership contracts.
- effect_retarget: change power/cap without deleting original native snapshot or learned model; reset target trim and pending-free controller demand only. ctl_submit accepts only quiescent ACTIVE same EFFECT mission.
- effect_read/ctl_read: add read-only308..319 diagnostics, retain existing320..351 layout; version distinguishes regulator.

### EFFECT v3 local tracking functions — 2026-10-14

- `effect_retarget`: preserve bounded per-device frequency trim and affine
  model/window; clear planned-reversal/oscillation history and retain only
  compatible actuator-response memory.  Existing physical-plateau range gates
  reject the window if the retarget actually moves the plant.
- `effect_verified`: bind each verified requested-flow change to the latest
  independent A3/17 target so a later decision can tell whether the native
  controller has started responding.
- `effect_fast`: apply different up/down laws, block same-direction command
  stacking for at most60s without A3/17 progress, continue far-above-goal
  braking through a falling target, and give forecast/actual45C regulation a
  faster bounded down path.
- `effect_model_tick`: unchanged qualification and RAM-only coefficient
  learning.  Positive goal trim remains inhibited during thermal/request
  limiting; no flash/EEPROM state is introduced.
- `effect_read`: version3 and extended flags at315; existing phase/reason at
  321/322 report response wait, request ceiling and minimum-output limits in
  addition to thermal limiting.  Existing addresses and word encodings remain.
- effect_init/begin/wait/verified: reset transient learning windows on native interruptions, retain learned coefficients across missions, keep readback cadence; initialize model once at ctl_init/reboot.

## Pair-energy supervisor 1.4.1 functions

- `remaining_energy_command`: pure closed-form reference for current and next
  cumulative deadlines. It subtracts a measured-power response-lag commitment,
  rejects an already unreachable current boundary, applies asymmetric physical
  ramp and capability bounds, compensates learned response gain, and limits one
  accepted command step. It performs no I/O and no candidate search.
- `feedback`: one input-register read at 321--336 per device returns EFFECT
  phase/reason plus qualified short-window power and age.
- `updateCapability`: holds its estimate for invalid/stale telemetry; phase 4
  reason 4 or 15 sets the temporary ceiling to fresh measured power+500 W;
  otherwise it reopens by 500 W per plan.
- `learnGain`: independently learns VP1/VP2 output-to-command gain only after
  180 seconds at an unchanged sent target with fresh phase-3/reason-0 feedback.
- `plan`: executes the remaining-energy formula every 30 seconds but accepts a
  changed actuator target no more often than every 120 seconds. Limiter-driven
  downward changes bypass that dwell. Same-target writes renew the finite lease
  and hit `control.c`'s `equal_intent` branch, which does not retarget/reset the
  local EFFECT model.
- `splitCommand`: floor/ceil 500 W allocation preserves the requested pair sum.
  The extra 500 W follows a meaningfully better learned gain, otherwise the
  lead alternates between accepted odd commands.
- `integrate`: integrates each pump independently and linearly splits an
  interval at an exact quarter boundary before saving the completed quarter.
- `status`: KVS version 2 reports physical wanted power, nominal command,
  actual sent sum, reachable capability, watt shortfall, forecast deadline
  error and both EFFECT limiter states.
- `commandOne`/`commandBoth`/`restoreLoop`: retain the existing eight-word
  EFFECT transport, 180-second lease and verified safe native restoration.
- `tick`: serialize both FC04 reads; when either result is missing or aged 60
  seconds, mark elapsed time unknown, preserve limiter state and hold the exact
  accepted targets. Renew them after 55 seconds without retargeting. Leave the
  planning deadline expired so a complete fresh pair replans immediately;
  require a following fresh endpoint before energy integration resumes.

### Bounded arithmetic and private state
- `effect_math.h:minute_rate`: diagnostic rate using whole seconds and quotient/
  remainder arithmetic; bounds avoid linking a software64-bit divider into Mode.
- `control.c:control_state`: groups previously separate private variables;
  `ctl_init` zeroes the complete state and restores the unavailable-age marker.
  Public exports and module RAM reservation remain unchanged.
- `test_effect_model.c`: independently exercises offset learning, repeated slope
  evidence, pivot compensation, freshness/confound gates and duplicate rejection.
- `test_predictive_candidate.c`: now tests the replacement two-loop frequency law;
  the filename is retained in the existing test target.

## Braking integration and dual quarter trial — 2026-10-14

bounded_demand: accept running lower-margin and time; enforce0.5C/60s decrease. effect_fast: fresh A3 error selects negative braking margin and bounded release near goal; preserve thermal priority. startup_target: positive restart margin, same bounded cadence. No control wire ABI changes. Add focused host brake tests and public ARM expectations for negative thermal margin. New OTA wrapper composes only Mode against each installed image. New dual-quarter runner sends requested power/lease only, never runs the inner regulator on Mac; logs coherent telemetry, A3 generations, model, actual targets, thermal state and per-stage timing; restores both on completion/error.

##45C policy candidate —2026-10-14

User replaces actual40C priority with45C, retaining requested55C. Named compile-time policy with derived approach/release/pause margins. Build12048/12288; Mode-only composed manifests180b7f30/b2e57972. Full historical host regressions explicitly at40C plus production-default45C boundary suite PASS. No live changes in this follow-up; installed40C firmware unchanged. Existing thermal-latch weakness remains documented, not silently treated as fixed. Release `procon/modular/release-effect45-20261014`.

## 2026-10-14: continuous envelope / faster upward response (offline candidate)
Actual supply regulation priority is45C, requested-flow ceiling55C. The current thermal forecast and actuator ceiling replace the90s cooling latch; no cooling-to43C prerequisite remains. The Hz controller continues underneath the thermal envelope, including negative power correction. Positive goal trim is inhibited when constrained; negative correction is allowed. Temperature priority still overrides the power goal and does not commandOFF.

After independent fresh A3/17 feedback, upward slew is at most2C/decision when more than10Hz short,1C when more than6Hz short, otherwise0.5C. Decisions remain at least30s apart; this is a ceiling, not a compulsory boost. Initial demand selection and unchanged-target90s nudge remain. Downward slew remains0.5C per60s. Ordinary braking can reach actual-0.5C/-1C above20Hz; it releases at20Hz or early below24Hz when the observed target is falling. This replaces the fixed25Hz guard.20Hz is an observed operating point, not a universal minimum guarantee.

ABI,12KiB Mode slot, leases, restoration, telemetry freshness and native protections are unchanged. Only Mode is included in device-specific OTA compositions. Synthetic tests establish software behavior, not physical stability or6kW capacity. No installation or live test has been performed for this candidate. Next physical qualification should compare upward4→6kW and downward6→4kW response, temperature priority and low-load pause behavior.

## Final EFFECT/energy v2 function placement — 2026-10-14

- `effect_model_op` and `effect_model_tick` now execute in Service through the
  two private veneers immediately after its public export table. Their callers
  stay in Mode. Public exports and layout ID remain unchanged, but Mode and
  Service are operationally inseparable and must share one OTA commit.
- `effect_fast` distinguishes usable (<60 s) from quick (<15 s) water, native
  and aggregate measurements. Usable older data permits conservative progress;
  it cannot authorize aggressive gas. `EFFECT_SOURCE_STALE` reports loss of
  usable provenance without converting it to a hard mission abort.
- `effect_fast` also reports `EFFECT_MINIMUM_OUTPUT` when fresh A3/17 is at or
  below the observed 20 Hz boundary while measured power still exceeds the
  goal by more than 500 W. This is a control state, not proof of a universal
  compressor minimum.
- `thermal_ceiling`/`bounded_demand` enforce the independent 45 C physical
  priority and the configured request cap. Thermal down-slew is at most 1 C per
  30 s; ordinary down-slew remains 0.5--1 C no more often than 60 s according
  to Hz error. A lower request cap is not defeated by the running demand floor.
- `remaining_energy_command` and `plan` implement current+next deadline control
  in constant space. They do not run the offline four-quarter grid search.
