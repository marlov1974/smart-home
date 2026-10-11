# P0080 function design
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
