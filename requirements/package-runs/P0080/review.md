# EFFECT + rolling energy v4 review — 2026-10-16

The firmware update is correctly atomic across Mode, Service and Debug Command.
Mode depends on the private Service model veneers, while Debug Command owns the
C077 import consumed by that model. Both device-specific images preserve BL2,
layout and all unrelated chunks. Live OTA completed on both devices without a
repair branch, followed by valid resident identities and native curve control.

The persistence boundary is deliberately narrow. Saving only bounded gain `a`
in UID-bound Shelly KVS retains slow plant learning across reboot without
mistaking bias or short-lived control state for durable calibration. Firmware
does not call a flash or EEPROM path and falls back to gain 1350 after reboot
until a valid host seed is accepted.

The first runtime validation found a coverage gap rather than a production
control fault: stale feedback correctly suppresses production planning, but it
also suppressed the only 1.5.0 validation self-stop. Transactional rollback
worked. Version 1.5.1 moves only the validation branch ahead of that production
hold after identity, diagnostics, feedback and plan parsing have completed.
The new execution regression reproduces the exact sentinel/age state, proves
self-stop after the model-record allowance and observes zero holding writes.

Live validation of 1.5.1 passed and left exact production Script 7 stopped and
disabled, both plan/status KVS keys absent, serial unchanged, relays off and
both controllers IDLE in native curve mode. This qualifies installation and
the read-only runtime path. Power tracking, four-quarter delivery accuracy and
post-learning gain persistence still require a separately authorized physical
mission.

# P0080 implementation continuation — WARN
User explicitly extends feasibility to implementation, refactoring latest EFFECT firmware and building chunk OTA. Overrides old offline-prototype-only scope for code, not permission to flash or actuate. No live I/O in this implementation run.
Clean upstream synced; current G2 portable source is P72, latest local P76 pause-r2 identified and pinned in procon/modular/baseline.json. New modular candidate stays isolated from legacy procon source. Prior physical fixed-page flash proof is supporting evidence, not OTA validation.
Package delta bootstrap used per memory/08-context-bootstrap-modes.md in this active thread. Latest manifest99 paths not reread unnecessarily. Current package, prior evidence, relevant code and index reviewed.

## Follow-up response memory and recovery — 2026-10-10
WARN: operator explicitly requests further changes to the existing local P0080 controller following the e8fc6d86 experiment. Fetch succeeded; HEAD and origin/main have zero divergence. Existing local P0080 work is intentionally continued under that authorization, without resetting, committing or pushing. This is an offline implementation/build qualification; new physical performance is not inferred from the previous trial. No layout, ABI, register or thermal-envelope changes are intended.

## 2026-10-11 continuation design review (before implementation)
Use existing Drift snapshot ABI rather than expand Common->Mode measurement.
Only Mode OTA; preserve P81 diagnostic modules and resident BL2. Independent
source histories prevent false temporal coherence. Main risk: added braking may
reduce power too early; supervised trace must distinguish thermal limiting from
power tracking. Physical40C is a measured stop criterion, not a guarantee that
thermal inertia cannot overshoot. Native safety and finite lease stay active.

Final candidate verification: host sanitizers pass; actual independently linked
ARM Mode/Drift source-history, entry, thermal, recovery, veneer and snapshot
checks pass; RAM flash writer checks pass; exact P81->candidate OTA1551 mutation
cuts and fake sender pass. BL2 byte-identical. The broader historical test_arm.py
suite is NOT claimed fully passing: it stops in the unchanged MVP validity case
at line302. A targeted rerun against untouched build-p81 reproduces the same
failure (pump availability fixture predates current telemetry). First12 broader
boot/UART/A3 cases passed on candidate. No production change was made to hide
this historical fixture mismatch. Current production behavior is covered by the
passing host integration and direct actual-ELF module suites above.

## 2026-10-11 VP1 installation and physical review — partial tracking success

Mode-only OTA and native Modbus/helper restoration verified. VP1 installed
7136193e; VP2 firmware and heating controls preserved. Completed900s at6kW
target under the55C requested/40C actual envelope, then verified original native
curve and controller ownership/lease cleanup. No observed compressor stop in
120 mission observations; actual supply maximum38C. All source ages<7.41s.

First90% at4:09.7, first100% at11:43.7; final5min short mean5.713kW and
−67.4W/min trend, ending5.411kW within the mission. Sustained6kW was not
achieved. The pre-existing hard ceiling restricts demand to42C at flat38C,
so this trial cannot distinguish plant capacity from the imposed demand limit.
Further tuning is needed; no additional device changes were made after restore.
The unchanged60s data-validity threshold was not exercised by this fresh-data
run; stale/pause recovery evidence remains from offline host/ARM checks.

The final analyzer distinguishes full-window rolling-feedback integration from
partial raw-power coverage; see CHANGELOG for metrics, evidence paths and hash.
Code, reproducible analyzer, package records and existing knowhow are updated.
No claim of adaptive gain identification, perfect tracking or all historical ARM
tests passing. No commit/push performed.

## Predictive envelope continuation review — WARN, 2026-10-11
Fetch successful, HEAD/origin divergence0/0. Existing uncommitted P0080 work and
prior P0089 documentation preserved; the user's explicit continuation authorizes
extending this same work without discarding it or treating it as a sync blocker.
User explicitly authorizes both OTA updates and physical6/5kW test, overriding
the original feasibility-only package boundary for these actions.
Prior experiment proves a binding controller ceiling, not pump capacity. A
continuous predictive ceiling avoids the sharper discontinuity of an on/off
relaxation and gain8 halves quantization sensitivity compared with gain16.
Actual40C remains the external trial guard. Sustained flat readings near39.5
cannot justify releasing signed correction: prior native capture overshot40.5.
No adaptive plant identification or general performance guarantee is claimed.

Latest operator correction supersedes the earlier actual40C trial stop criterion:
temperature has priority over power but neither40C,42C nor time above40C triggers
mission abort. Apply a bounded0.5C/30s taper, prevent further own reductions below
min(current,supply+0.5C), continue feedback and lease, record delivered power.
Native/data/ownership fault paths are distinct and retained. Final Mode size
needed local LTO plus preserved memset; static audit verifies all15 ABI veneers
and no undefined symbols. Final exact-ELF verification is required before OTA.

Final qualification completed before physical deployment: full sanitized host
suite; exported controller/entry/readback/taper/source-hold/restoration scenarios
and module/snapshot tests against both exact ARM artifacts; actual C OTA engine
1551 mutation cuts per device image pair; sender and13 dual-harness checks.
The optimized private helper ABI is intentionally not called by the ARM tests;
public controller paths execute the real linked image, with fine-grained helper
coverage in the host suite. Historical unrelated test_arm.py failure is unchanged.

Mode-only OTA completed on both units on2026-10-11: D1 b39273d4, D2 b8fb9712.
Both CRCs were verified twice, followed by native Modbus verification of both
units after each peer's WAIT expired. Helper source and9600/8N1 mb_client
transport restored. Native curve2, power1, DHW52C and boost0 remained unchanged.
The120s peer WAIT is timer-only, not cancellable; target verification and cleanup
overlap that period. Evidence: update-adaptive-both-20261011T202952Z.
The supervised dual trial follows separately; OTA success is not evidence of
power tracking or thermal-envelope performance.

Final physical review:900s completed after both ACTIVE, then exact native curve
restoration verified for both and all ownership/lease state cleared. Maximum
observed supply39C/39C, no observed in-trial compressor stops/DHW/control errors.
Temperatures have900s supported capture-time interpolation with zero>=40C
exposure. Distinct source-time coverage is899.02s/900s; the missing0.98s is unknown.
This verifies the tested trajectory, not a guarantee between samples or
under other loads. Firmware does not abort on temperature or exposure time.

Tracking remains partial: last5min means4.719/5.568kW against6/5kW, combined
10.287kW. D1's return/flow places6kW close to the thermal boundary; the empirical
envelope is not proven optimal. D2 has residual power overshoot. Shared floor
conditions changed during the test, and apparent opposing movement is not stable
evidence of hunting. Both were already running at entry. All numerical results,
coverage caveats and raw-log hash are in the latest CHANGELOG section. Only
documentation and offline analysis changed during/after the frozen firmware test.

## 2026-10-12 equal5kW repeat — physical tracking/temperature FAIL
No firmware changes. Both authorized5000W commands and renewals were encoded
and observed correctly; both missions completed900s and originals restored.
Last5min means6.190/6.035kW, max actual40.5/39.5C. VP1's initial301s pause is
separate from post-start stops (none). The strict<40C objective failed on VP1;
there was deliberately no temperature-triggered abort. Fresh primary sources
and zero control errors exclude stale telemetry/transport rejection as the
observed cause of the large tracking error. The demand floor blocks continued
taper near/below actual, and the fixed forecast omits remaining actuator slew.
These are control-design limitations to address, not proof of unstable coupling.
See latest CHANGELOG for exact coverage, evidence hash and restored30C baseline.


## 2026-10-12 — user-authorized fixed60 candidate
User explicitly directs firmware edit after the local-dirty sync report; proceed on existing work without discarding or publishing it. P0080 scope: v2 requested flow upper bound60C and GET09 validation60C; EFFECT cap55C and thermal law unchanged. PASS for offline build; physical FTC acceptance remains unverified.


## 2026-10-12 — VP2 fixed60 plateau repeat
VP2 fixed60 repeat authorized by user. PASS with comparison limitation: different initial Hz/thermal/DHW history. Plateau detection is an operational stopping criterion, not proof of absolute maxfrequency. Existing30min/50C bounds retained.


## P0080 A3 frequency comparison — 2026-10-12
WARN: user authorizes repeat VP2 fixed60 with A3/16 and17, peer VP1 OFF. Existing diagnostic path rejects active control; extend regular exclusive service queue. Preserve all prior dirty work; fetch confirms no branch divergence. No concurrent debug/display questions during trial.


### Dense A3 follow-up 2026-10-12
PASS scoped frequency sampling continuation: operator authorizes denser A3 and repeat VP2 trial; retain prior dirty work. Only Service changes, installed Common and Mode unchanged.


## 2026-10-12 — user requests more A3/17 replies/min
WARN: follow-up to authorized sampling work, preserved existing uncommitted P0080/P0089 changes. git fetch succeeded, main has no divergence from origin/main; dirty status is prior ongoing work. Continue scoped work under user's direct request, no reset/stash. No heating target changes are needed. Latest D1c7a0fbcb/D206e8dea7 must be live-verified before OTA.


## 2026-10-12 — authorized fixed60 target-only sampling
WARN: user explicitly requests a new60C trial with~8A3/17 reads/min to distinguish clocks. Previouscurve-onlydiagnostic achieved7.9/min but cannotrunwithinactivecontrol; do notrelaxitsIDLEgate. ContinueexistingP0080dirtyworkauthorizedbysuccessiveuserinstructions;fetchsucceeded,HEADequalsorigin/main,prioruncommittedworkpreserved. ThisiscontinuationusingcompletedbootstrapplusP0080delta,notanewpackagebootstrap. No commit/pushrequested.

Scope: VP2onlyServiceOTAfrom5fc25d43,VP1c7a0fbcbpreserved. ACTIVEfixedflowtarget6000 selects17for everyserviceoperation;ordinaryFASTandretryownershipunchanged. OtherA3backgroundcanexpirehonestlyduringboundedexperiment. TestVP2fixed60whileVP1OFF;stopactual50C,30min,orhighHzplateau180s;restoreboth originalnativecontrols. About8/minisexpectedfromearlierjobtime,notaguarantee. Recordtargetcompletiongenerations,pendingstatus,GET04/temperaturesandtimingintervals;noassumptionoftwoclocks.


### Final review: focused fixed60 A3/17, 2026-10-12

PASS for scoped firmware/tests/OTA and requested physical sampling:161 logged
completion events at8.27/min, VP1 rested, maxsupply45.5C, high plateau stopped the
trial. Both pumps restored to all five original native values and idle controls.
Independent raw-log audit agrees. All15 target changes fit one approximately60s
reported-target rhythm; internal clock count remains unproven. No effect-law
change or evidence of faster opposed small steps in this run.

WARN retained: first ordinaryA3/27 afterrestore exhausted retries, so initial
post-check failed after successfulcontrol restoration. Separate read-only
follow-up confirmed six more cycles without additional failures/exhaustions.
Final outcome explicitly distinguishes these. No simultaneoushardwareagents,
no diagnostic gate relaxation, no new trial during follow-up, no commit/push.


## 2026-10-12 — authorized four moving-delta trials
WARN continuation: user explicitly requests VP2 actual+5/+10/+15/+20C from~30C to45C with15min pauses; clarification requires waiting longer until~30C. VP1 remains resting. Current branch equalsorigin/main after fetch; prior dirty P0080/P0089 work preserved under direct continuation authorization. This is not a new package bootstrap and no commit/push is requested. Existing native safeties unchanged. +20 needs up to65C desired: static FTC20.01 trace supports representation but installedFTC21 must verify native readback; no silent clipping or claim of sustained20C if rejected. Native physical actual stop45C. Service focus will cover ACTIVE fixed-flow/OFF for this bounded experiment; normal profile restored after tests.


### Four-series final analysis and recovery verification

All four physical endpoints reached; final host chain analysis is non-partial.
Review preserves first-segment DHW interruption and both subsequent priority
waits, clock separation, original-state restoration and sample-age uncertainty.
No simultaneous hardware workers. Frozen hypotheses are evaluated against new
series without shifting the exit definition; failed predictions remain visible.
Swedish plot checked against chainJSON and visually inspected. No new tracked
paths in this follow-up; existing file index and unrelated changes preserved.

Post-OTA ordinary service verification requires a new successful generation
for each27/28/18/19/16/17, not register42 alone (it counts terminal jobs including
failures). Bounded180s; at most one first transition failure permits rebaseline,
without extending deadline or retaining earlier successes. Additional faults
fail the check. Both original native states and IDLE/saved0/error0 checked
before/after. Fifteen fake-clock recovery tests passed, including transition
fault, multiple fault rejection, counter reset and final-read fault cases.
Raw uint16 remains uncalibrated; brine-level16 is not rejected as an invented
engineering-range violation. Live result recorded in the final OTA entry.


### Moving-delta profile restored — 2026-10-12 19:45 UTC

All four series reached45C. TemporaryVP2d3cbb1d2 restored through Mode+Service
OTA to prior33143fde, VP1c7a0fbcb preserved. Both verified power1/curve2/DHW5200/
boost0, controlIDLE/saved0/error0/lease0; read curve target3050. Prior native
Modbus restored, helper stopped/source restored, peerWAIT expired. Ordinary
A3 codes27/28/18/19/16/17 each produced a new valid successful generation in
45.025s with no new failure/exhaustion and no transition rebaseline. Thus
post-check passed directly, unlike the earlier fixed60 focus transition.
Evidence: outer effect-learning/restore-delta-sweep-vp2-20261012T194106Z,
recovery.json/outcome.json/cleanup.json. No physical session remains active.
Temporary65C mode/focusedOFF profile is not installed. No commit/push.


### Nondecreasing +10C VP2 trial — 2026-10-12, completed

User removed the mandatory pause before this single run; only cooling to
approximately30C was required. Native DHW finished first. Heating started at
29C with39C target; target=max(previous accepted target, fresh supply+10C).
Reached45C in1645.807s (27:26), versus1594.363s (26:34) in prior +10 series.
Zero commanded or settled target decreases (prior10); A3/17 still repeated
84→70 three times (priorfour). 210 successful samples,7.656/min, no generation
gaps. Removing decreases does not eliminate oscillation; one fewer cycle is
not evidence of improvement in these unreplicated ordered trials. Upward
retargeting remains a possible influence. No new EFFECT algorithm installed.

Both originals restored; VP2 temporaryd3cbb1d2 reverted to33143fde, VP1
c7a0fbcb preserved. Both power1/curve2/DHW5200/boost0, controlIDLE/saved0/
error0/lease0. Native Modbus/helper restored; all six ordinary A3 codes
27/28/18/19/16/17 have new successful generations, no transition rebaseline.
Evidence (outer workspace): effect-learning/monotone-delta10-vp2-20261012T204350Z
and restore-delta-sweep-vp2-20261012T213731Z. Report, comparison plot, frozen
runner and raw events preserved. No commit/push performed.


## Two-loop EFFECT follow-up, 2026-10-13 — WARN
Operator explicitly authorized building, installing both devices and VP1 6 kW/change-of-target live validation, with normal40C priority; experiment50C authorization is not the new normal limit. Operator explicitly resolved the local-dirty sync gate with “Åtgärda och fortsätt”. origin/main and HEAD were equal; all prior changes retained and snapshotted externally at effect-next-sync-review-20261013T122910Z. This is a P0080 follow-up, not a new package number. Use delta-bootstrap per memory/08-context-bootstrap-modes.md. No unrelated P0089 edits or automatic commit/push.
Fixed12KiB Mode has only32 bytes margin in prior build. Replacing the old predictor, not appending another active controller, must fit unchanged slot/ABI. Common and BL2 must be preserved separately per device. Installed ordinary Service exports A3/16,/17 with valid/age/generation; no faster sampling claim.

### Two-loop qualification checkpoint, 2026-10-13

- PASS full host suite including ASan/UBSan; replacement law tested against
  A3 frequency goals rather than retired acceleration-memory behavior.
- PASS actual composed ARM images: public controller admission, thermal0.5C/30s
  taper, aging guards, original restoration, direct6→5kW retarget, diagnostics
  through resident Modbus/Dispatcher/Common; no private LTO symbol dependency.
- Fixed a discovered compatibility gap: VP1 also receives Service with A3/16/17.
  Its initial Mode-only composition failed the ARM cooling/response test because
  the preserved old service returned zeros; the revised composition passes.
- Mode11760/12288bytes, RAM1304/4096bytes. Layout, export order and BL2 preserved.
- Initial installed candidate manifests: D1 0x1482d8c9, D2 0x80471ba2.
  Evidence: workspace P0080/effect-learning/update-adaptive-both-20261013T152939Z.
  Live effect characterization and final restoration are still pending here.

### Live-read preflight correction

The first live preflight sent no controls: D1's preserved Common routes372–383
to the old feedback decoder, returning zeros. Internal Mode diagnostics317/318
showed actual cached A3 data, proving the Service upgrade worked. Added FC04
input300–307 provenance mirrors through ctl_read, which works through both
installed Common versions. Both composed ARM snapshots now test this exact
public Modbus path against svc_read, in addition to raw317/318. Initial images
are retained under build-two-loop-initial-vp1/2; corrected Mode11792bytes.
Corrected manifests D1c6f9308a/D2523cf3e1. This corrective update changes Mode
only on each unit. Input350 retains its pre-existing flag1 semantics.

### Final profile audit (while native restart is waiting)

Compared the real fixed60 baseline disassembly, not just dirty source. The
working tree still carried the earlier temporary65C/manual-OFF A3-focus sweep.
It had entered the initial candidate, although EFFECT itself stayed55C and no
65C command was sent. Production now defaults to manual60C and the prior
fixed60-only service focus. The sweep remains reproducible only with explicit
`--experimental-delta-sweep` (`PROCON_DELTA_SWEEP`); both host profiles are tested.
New production Service is byte-identical to D2's verified33143fde baseline.
D1 will receive that Service; D2 retains it. The watt/Hz EFFECT law is unchanged.
Production Mode11784/12288bytes, RAM1304/4096. Prepared final manifests
D191be47e2/D23b5041a0; install only after the supervised mission is restored.


### Two-loop EFFECT: baseline live failure and corrections — 2026-10-13

The first complete VP1 trial ran6kW then5kW, each15min of observation, with
VP2OFF and180s renewed leases. Native start wait was370.6s; it is excluded from
qualified first-stage figures. The6kW stage reached90% in142.4s, but peaked
at7524W and averaged6664W over its last5min. The5kW stage averaged6681W over
its last5min: target acceptance is verified, target tracking failed. Actual
supply stayed31.5–37.5C. No model updates occurred. Both originals were restored
(power1/curve2/DHW5200/boost0), controlIDLE, no saved ownership/lease/error.
Evidence: outer effect-learning/two-loop-vp1-20261013T171404Z.

Three corrections follow this evidence:
- Replace inherited fixed45C startup with Hz-distance gas: +10/+5/+3/+2C.
- At the Hz goal, continue0.5C taper of excess delta above2C through native
  plateaus, instead of retaining large gas indefinitely. A falling native
  target pauses normal cuts. Corrections retain30s minimum and new-A3 gating.
- A numerical regression reproduces why an asynchronous intermediate stale
  power/skew could erase every learning window. Skip such intermediate reads;
  never learn from them. Freshness/coherence of accepted samples is unchanged;
  link/invalid data and60s gaps reset the window. The outer caller no longer
  destroys the window merely for an aggregate aged15–59s.

All host tests pass with ASan/UBSan; both final composed ARM images pass the
public controller, Modbus diagnostic, restoration and module ABI tests. Mode
11888/12288bytes, RAM1304/4096bytes. Production Service uses the ordinary
fixed60-only focus, not the prior temporary65C/OFF experiment. Final manifests
D1=760ce5a6, D2=dce2e3e4; OTA/live verification still in progress at this entry.
Artifacts and exact source: procon/modular/release-effect-two-loop-20261013.

Do not infer guaranteed5kW tracking from this build. The baseline downstep
stalled near51–52Hz with requested37C and actual37–37.5C; avoiding a native
stop limits further setpoint reduction. The repeated trial must report this
limitation explicitly if it remains. Water-power quantization is approximately
0.63kW per0.5C at18L/min, so decimal power figures are not calibrated precision.


### Calibrated trial and slow-approach refinement

Second run: effect-learning/two-loop-vp1-20261013T183722Z, D1760ce5a6/D2dce2e3e4.
Full6kW15min: first90%255.2s, peak5643W, last5min5381W, final5094W, actual
32–35.5C. Overshoot removed but acquisition remains too slow. Five legitimate
bias updates changed-1090→-809W; gain stayed135W/Hz (no eligible separated
plateaus). A direct5kW replacement preserved coefficients and delivered5016W
on all44 samples over324.4s, actual35.5C, A3/16 45→43Hz, no observed stop.
Bias continued to-817W (seven updates). This5kW segment was deliberately
shortened after five minutes to install another qualified refinement; stop-file
KeyboardInterrupt is operator termination, not a firmware failure. Both originals
were verified restored, IDLE/error0/saved0/lease0.

The remaining slow-approach issue is explicit in the law: repeated downward
setpoint corrections continued even while severalHz short of goal. New law
retains the applied request while >3Hz short unless native target just moved
by a coarse>=5Hz step. An independently unchanged below-goal target for90s
permits a0.5C increment; the timer restarts on movement or increment. No gas
increase without fresh raw sources/new A3, or during thermal/oscillation holds.
Near/above-goal taper, all native guards and original restoration remain.
Host ASan/UBSan and both composed public ARM suites pass, including stalled
frequency/gentle increment and stale-source cases. Mode11936/12288bytes,
RAM1304/4096. Prepared manifests D15903105e/D2f3ed161c, Mode-only per device.
Installation and final repeated physical qualification pending at this entry.

## Completed two-loop deployment and trial — 2026-10-13

Both devices installed and read-back verified: D1 `5903105e`, D2 `f3ed161c`; latest OTA changed Mode only, BL2 preserved. Mode11936/12288bytes, RAM1304/4096bytes. Host ASan/UBSan and both composed ARM suites passed.

Final VP1 trial, VP2 OFF:15min6000W then15min5000W. At6kW, last5min mean6086W (5643–6448W),90% reached3.26min from logged activation including45.82s qualification wait. At5kW, last5min mean6273W (6270–6313W): downward tracking FAILED. The positive demand floor prevented further braking near actual temperature; no protocol failure has been proven. Model offset updated10times to-761W, slope stayed135W/Hz. Maximum actual supply37C; no zero-Hz samples during qualified stages. Thermal-boundary operation was not exercised by this live test.

Both restored and verified power1/mode2, curve target30C, DHW52C, boost0; controller IDLE, saved0, lease0, error0. No active trial remains. See `effect-two-loop-report-2026-10-13.md` and `evidence/effect-two-loop-20261013/final/` for raw events, plot and restoration. Earlier entries are historical checkpoints. No commit or push in this task.

## Brake-boundary live experiment — 2026-10-13

VP1 manual, VP2 OFF.−1C yielded41→32Hz in about4min without pause;−1..−1.5C reached20Hz while running. At actual33C/target31C (−2C),20→0Hz was observed; both restored and verified curve/IDLE/lease0. This brackets a single observed low-frequency stop transition, not a universal guaranteed threshold. No firmware change. See `brake-boundary-report-2026-10-13.md` and its complete provenance, including corrected harness state2 handling and controlled handoff.

## Braking integration and dual quarter trial — 2026-10-14

WARN: operator explicitly authorizes updating both devices and simultaneous15min each2/4/6/4kW. Prior user authority to resolve dirty-tree sync remains; fetch completed, HEAD equals origin/main, existing P0080/P0089 edits backed up in braking-sync-review-20261014. No unrelated edits or commit/push. The dated live braking evidence supports limited negative demand, not a universal pause threshold.2kW may be below continuous output under current conditions. Both share hydraulic load, so physical results must be per-device and combined.

Offline qualification of braking candidate completed: full host suite under ASan/UBSan and actual ARM public controller/routing tests for both composed device images PASS. New focused test covers negative delta floor,60s verified-cut cadence, goal/minimum release and stale gating. Existing thermal/predictive tests were updated for the deliberately slower cut cadence; synthetic startup transient no longer implies a cut after the rise has dissipated. Mode12048/12288,240bytes spare; ABI and unchanged slots preserved. Physical deployment and hour trial still pending final result.

## Dual quarter trial completed — 2026-10-14

Both Mode-only OTA installations verified (0f48da4e/a5a6dc0c);60-minute2/4/6/4kW-per-unit mission completed and both curve restorations verified. Physical tracking PARTIAL: final5min VP1/VP2:2kW→3.06/3.13;4kW→3.99/3.75;6kW→4.38/5.07;4kW-down→3.85/4.19. No observed compressor stop after initial native pause/restart. Thermal latch blocks ordinary power correction and needs redesign; upward slew remains slow;25Hz release limits2kW. See dual-quarters-report-2026-10-14.md, evidence/dual-quarters-20261014, and release-effect-braking-20261014. Source/tests pass, no commit/push.

##45C policy candidate —2026-10-14

User replaces actual40C priority with45C, retaining requested55C. Named compile-time policy with derived approach/release/pause margins. Build12048/12288; Mode-only composed manifests180b7f30/b2e57972. Full historical host regressions explicitly at40C plus production-default45C boundary suite PASS. No live changes in this follow-up; installed40C firmware unchanged. Existing thermal-latch weakness remains documented, not silently treated as fixed. Release `procon/modular/release-effect45-20261014`.

Final45C qualification: both composed ARM images PASS public controller and full routing; release SHA256 verified; git diff whitespace check PASS. No device/RPC writes performed.

## 2026-10-14 pre-implementation review
Temperature envelope must not disable downward power corrections; positive trim remains inhibited under constraints. Fresh source/generation gates retained.20Hz is an observed operating point, not a guaranteed minimum across conditions: falling-target release begins below24Hz. Faster upward slew can excite native minute steps; near-goal slew stays small and physical qualification remains outstanding.

Qualification completed: full host suite with ASan/UBSan PASS, composed ARM VP1 and VP2 PASS, Mode12048/12288bytes, only slot2 changed, git diff --check PASS. Release includes logs, exact source and SHA256 checksums. No live commands sent.

## Combined EFFECT and energy 1.4.1 review — 2026-10-14

Offline result: PASS with a physical-qualification warning. The controller no
longer aborts useful regulation merely because otherwise qualified telemetry is
15--59 seconds old. Only <15-second sources authorize the faster path; <60
seconds remains usable for conservative best effort. Minimum output, the 45 C
actual-supply envelope, the separate requested cap and stale source are now
explicit control states. Thermal reduction is bounded to 1 C/30 s; ordinary
reduction stays slower, so temperature priority does not introduce an abrupt
OFF command.

Moving the affine model to Service resolves Mode's slot pressure without
changing the public layout. It introduces a deliberate private dependency:
Mode 11,928/12,288 and Service 2,728/4,096 must be updated together. The
device-specific compositions change only those two modules and retain BL2.
Mixing either new chunk with its old counterpart is unsupported.

The Shelly 1.4.1 supervisor fixes three field-relevant faults: an odd 500 W
pair request now has an exact floor/ceil split, fresh limiter caps constrain and
redistribute the pair command, and a transient telemetry failure holds/renews
the last accepted command instead of planning from zero. Unknown intervals are
reported and excluded from fabricated energy. Fresh recovery triggers an
immediate replan. Normal retargets dwell 120 seconds; reductions caused by an
active limiter may occur immediately.

This is a constant-time current+next cumulative-deadline controller. It is not
the offline four-quarter MPC. Host sanitizers, final VP1/VP2 ARM images, public
FC04 diagnostics and mock coupled OTA pass. No 1.4.1 Shelly run or combined
firmware live trial has occurred, so tracking quality and physical stability
remain unqualified.

The frozen offline release is
`procon/modular/release-effect-energy-v2-20261014/`. Its `COMPOSITION.json` and
`VERIFICATION.json` bind the two device manifests, atomic Mode+Service pair,
test results and physical-test limitation; `SHA256SUMS` verifies all 128 other
release files.
