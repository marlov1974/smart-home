# P0080 implementation continuation

## 2026-10-16 — EFFECT + energy v4 installed and validated

- Installed the atomic Mode+Service+Debug Command update on both devices:
  VP1 `4bf657aa -> 57ee1885`, VP2 `e11851e8 -> fd001ec7`, slots 2/4/5.
  All OTA replies were successful; no frame retry or repair image was needed.
- Added the UID-bound C077 import for only the long-term kW-to-Hz gain. The
  value is RAM-only in Procon and persistent only in Shelly KVS; bias, trim and
  transient controller state remain volatile.
- Added strict rolling four-quarter KVS plans, bounded debt and cross-pump
  energy allocation in Shelly. No plan means no control.
- Live validation found that 1.5.0 could wait forever when post-flash power
  feedback was still unqualified. Transactional rollback restored the complete
  prior script, absent KVS keys and unchanged serial configuration.
- Fixed that validation-only path in Shelly 1.5.1 and added an end-to-end stale
  startup regression. The second live validation reached `phase=validated`,
  stopped before any control write and installed exact production Script 7
  stopped/disabled. Modbus 9600 8N1, relays off, native heat-curve operation and
  IDLE controllers were verified afterward.
- No physical energy-delivery trial was run. See
  `effect-energy-v4-installation-2026-10-16.md` and its linked evidence.

## 2026-10-14 — EFFECT + energy 1.4.1 installed

- Atomically installed Mode and Service in OTA slots 2 and 4 on both Procon
  devices. Verified manifests are VP1 `4bf657aa` and VP2 `e11851e8`.
- Verified serial Modbus restoration and preserved native power, heat-curve,
  flow-target, DHW-target and boost settings on both devices.
- Installed the 15,420-byte Shelly Script 7 version 1.4.1 source with SHA-256
  `f5278ee41f8058d82e8e54014729931fdfa00e26a8aa4c2a437386a1a6bfac11`;
  the script is stopped and disabled.
- No live EFFECT or energy trial was started. See
  `effect-energy-v2-installation-2026-10-14.md` and the linked evidence.

## 2026-10-14 — offline pair-energy supervisor 1.4.1

- Replaced the fixed offline trajectory and `+/-3 kW` correction with a
  constant-time remaining-energy/response-lag/current-and-next-deadline law.
- Added observed pair ramp/reachability bounds, per-device limiter capability,
  separate stable response-gain estimates, 120-second changed-target dwell and
  best-effort shortfall/forecast reporting.
- Seeded reachability conservatively from attempt 11 at +2.0/-1.25 kW per five
  minutes for the pair, rather than the earlier optimistic +8/-4 kW assumptions.
- Fixed odd 500 W pair splits so the two sent targets exactly equal the nominal
  pair command; attempt 11 had 111 +500 W mismatches. Added the actual sent sum
  to KVS status.
- Split trapezoidal energy at the exact 900-second boundary and retained
  independent freshness qualification for both pumps.
- A missing or at-least-60-second-old power sample now marks the interval
  unknown and holds the existing pair command. An established command is still
  renewed at the 55-second lease margin; the first fresh pair replans
  immediately without restarting the script. A Node execution test covers one
  failed Modbus feedback read, renewal, unknown accounting and recovery.
- Audited attempt 11: quarter 4 was temperature limited in 27/29 samples and
  averaged 10.517 kW, explaining its 2.628 kWh result; 4 kWh was unreachable
  under the observed envelope.
- Added pure reference math, attempt-11 extraction/replay and focused tests.
  All 41 energy tests and JavaScript syntax validation pass. Against the actual
  sent attempt-11 trajectory, model replay cuts absolute quarter error
  3197.695->2820.398 Wh and maximum quarter error 1080.779->950.106 Wh; this is
  offline evidence, not a live result.
- No firmware, Shelly installation or live device setting changed.

## 2026-10-14 — four-quarter energy-mode design

Converted the completed dual 2/4/6/4/2/6 kW trial into a concrete two-level
energy architecture. Shelly owns pair allocation; each Procon can execute an
assigned four-quarter energy plan through the existing EFFECT controller.
Measured power is integrated for energy and native ramps are modeled only for
forecasting. Low pair demand uses asymmetric one-pump scheduling instead of two
unstable 2 kW requests. The proposed executor fits in Common plus Dispatcher and
does not require BL2/layout changes; Mode has only 240 bytes free. No firmware or
live setting was changed in this design step. See
`energy-mode-design-2026-10-14.md`.

Requirement refinement: quarter kWh targets apply to combined VP1+VP2 delivery;
there is no fixed per-device share. The initial per-device model uses5min
zero-output startup, +4kW/5min ramp-up and -2kW/5min ramp-down. The optimizer may
move recovery and ramping between pumps and across quarter boundaries. Energy
error over all four quarters is primary, calm/COP-efficient delivery secondary,
and infeasibility always produces continuing best effort rather than abort.

Read-only Shelly capacity check: approximately109kB system RAM free (97kB
recorded minimum),77,824B filesystem free and25,200B per stopped script VM.
Existing slot7 is a compact disabled four-block optimizer, but its array-based
patterns are not suitable for the new runtime. The pair MPC therefore uses only
scalar state, serialized Modbus and a bounded candidate calculation. Arrays,
`split`, retained trajectories and large object/JSON searches are explicitly
excluded.

Live runtime qualification found two additional Shelly limits. A complete
37-candidate/four-quarter search (4440 model steps in one callback) hit the VM
instruction/stack guard before sending a control command. Splitting it across
many short timers avoided that guard but exhausted timer/RPC resources; a later
attempt saturated the Shelly CPU and made its HTTP endpoint unavailable. The
Procon180s leases remain the independent control fallback and Script7 autostart
was disabled before every attempt. The replacement evaluates only a1.5kW step
down and a1.5kW step up from the current command: at most240 scalar model steps,
no planner timer and no retained path. Offline replay of this repeated local
search delivers16000.8Wh against16000Wh in the fitted model. Physical
qualification remains pending. Failed runtime attempts are evidence, not
successful field trials.

COP responsibility refinement: L4 owns long-horizon COP when choosing
kWh/quarter. Shelly does not estimate COP; after energy error it prefers steady
combined power and divides load whenever both units can stay above their learned
continuous floors. Static reference allocation now selects3+3kW at6kW pair
demand while retaining4+OFF at4kW.

COP ownership correction: L4 alone measures/learns system COP and chooses the
day/week quarter energies, including3+3kW/16h versus2+2kW/24h. Shelly does not
calculate COP or use a COP map. It only minimizes four-quarter delivery error,
keeps total power calm and divides power between pumps subject to their physical
states; forwarding raw telemetry does not change that boundary.

Status superseded by the physical 1.3.1 qualification below.

### Constant-time Shelly executor and physical energy trial

The bounded two-candidate runtime still consumed about 98 percent CPU in a
one-shot device check. Replaced runtime simulation with an offline-derived
scalar reference trajectory plus a constant-time, clipped cumulative-energy
correction. No arrays or candidate paths run on Shelly.

The autonomous 105-minute physical plan delivered 16.151 kWh of covered
measured pair energy against 16.000 kWh (+0.94%). Quarter results were
1.124/2.553/2.957/2.628/2.460/2.352/2.077 kWh. CPU was 0/2/6 percent
minimum/median/maximum. Initial incomplete telemetry coverage totaled 321s and
was not invented as energy. Both units restored and verified in curve mode with
no lease or control error. See `shelly-energy-trajectory-report-2026-10-14.md`
and evidence `shelly-energy-trajectory-20261014-attempt11`.

Added procon/modular: latest P76 EFFECT code partitioned into fixed independent chunks; resident BL2 and selected-chunk OTA; Mac/Shelly sender; regression, protocol and real-ELF tests; build and first-install artifacts. Existing legacy procon code remains separate. No live actions or production activation. No commit/push performed.

Contracts: module ABI1/layout fingerprint, per-slot RAM, manifest-last commit, residentFC04/FC16 raw384, FF enter/FE wait, bounded addresslessP8 OTA protocol. Documented all-or-nothing activation and physical recovery limitations.

Read implementation-report.md, procon/modular/README.md and build/sizes.json first. Original feasibility evidence in the earlier local P0080 checkout is historical and is not replaced by this implementation report. Hardware flash proof came from MVP3 flash-r3 and is not equivalent to modular OTA proof.

Repository file index updated for the new candidate/source/evidence paths. Project-specific function catalog updated; generic knowhow promotion intentionally skipped because physical shared-bus behavior remains unvalidated.

## Frozen telemetry follow-up

Direct user build request: added consistent read-only snapshot, host reader and
native/ARM/OTA tests. Drift and Dispatcher revision2, same ABI/layout, all other
chunks identical. Original release remains installed baseline; release-snapshot
is offline candidate. See snapshot-design.md and snapshot-report.md. No live I/O
in this follow-up. Repository index updated for new source/tests/release files.

## Physical snapshot OTA

Authorized OTA completed with manual host-session recovery after late COMMIT ACK, no physical intervention. New snapshot verified three times. Host wait fixed/tested. Protocol1 whole-manifest CRC identity defect discovered; BL2 correction remains pending. See snapshot-live-report.md.

Knowhow promoted to memory/knowhow/procon-manifest-crc.md (CRC identity and receive-window lesson). Repository index updated.

## BL2 protocol2

Operator authorized original-bootloader replacement. Built resident/host fingerprint fix and protocol2 mismatch gates; feature chunks unchanged. Tests passed. See bl2-v2-design.md and bl2-v2-report.md. Physical normal boot remains pending.

BL2 v2 full transfer completed18:45:03 UTC:223/223 ACKs, cleanup verified, awaiting operator normal boot. Repository index updated; existing CRC knowhow entry updated.

Normal boot verified: protocol2, prefixCRC d9dd3c62, full-set valid, snapshot1/2/3, CN105 counters advancing without errors. Helper cleanup verified. Physical protocol2 OTA still not rerun. No new tracked paths; index unchanged.

Second connected Procon BL2-only transfer:28/28 packets,6584 bytes, cleanup verified. Address2 planned via DIP01000110; awaiting operator normal boot and UID read before full-set OTA. No tracked paths added, index unchanged. Existing first-install knowhow retained; no new generic finding.

D2 full-set protocol2 OTA succeeded199/199 with D1 acknowledged WAIT900s. Unique UID registered in report; address2 verified, snapshot and CN105 checks passed. WAIT autoexpiry not yet physically verified. Existing docs updated, no tracked paths changed.

D1 WAIT expiry physically verified2026-10-09 19:35:51–19:36:01 UTC: address1 sameUID, mode0, fullsetvalid1, correct prefixCRC, compressor26Hz valid, CN105 replies402→403, uptime2942→2952, errors0/UARTerrors0. No reset during observation. Read-only FC04; helper cleanup verified. Evidence P0080/d1-after-wait-20261009T193549Z.
# Direct fixed-flow replacement — 2026-10-10

Status: built and offline verified; NOT physically installed. Operator-requested continuation after15/20/20-minute identification sequence. ctl_submit/ctl_reply now accept flow-only FIXED replacement in an active session, revalidate native guards, preserve the initial original snapshot, send FLOW only and require target readback before applied advances. AUTO/expiry/failure restore the initial native state. Pending replacement/cross-mode/DHW changes remain BUSY; retries remain idempotent.

Changed existing control.c, test_control.c, test_modules_arm.py, design.md, functions.md, README.md and function catalog. Existing tracked paths only; REPOSITORY_FILES.md unchanged. Local generated candidate procon/modular/build-direct-flow is ignored, not published. Sync had no divergent commits; existing P0080 working changes preserved, no merge/reset/commit/push.

Tests: complete native ASan/UBSan suite including direct-target cases; actual modular ARM direct replacements/AUTO and snapshot/ABI; actual OTA engine1551 mutation cuts; fake Shelly host transfer/lost ACK/UID/cleanup. Actual ARM runner required execution outside sandbox after signal132 in sandbox. git diff --check passed. Only mode.bin differs from release-bl2-v2; BL2/other6 feature chunks identical. Mode10056/12288 bytes,RAM840/4096. Same layout3833993797; new prefixCRC c9d5de0b versus installed d9dd3c62. OTA56 frames, mode slot only. See build-direct-flow/VERIFICATION.json and ota-plan.json. No BL2 update needed.

Live identification completed32.5/32/38C with VP2off, final curve/power restoration verified on both. The required AUTO transitions caused stops, so down/up observations include restart behavior.38C reached62Hz, late water heat approximately7.94kW;32C late46Hz,5.96kW. Read local P0080/effect-learning/DOWN-UP-RESULT.md and raw evidence for exact timing. A helper-coded one-hour stop interrupted final readback; later read-only verification confirmed prior D2AUTOseq65 applied. Cleanup verified. Generic knowhow promotion intentionally skipped: control coefficients remain local operating-point estimates and the timeout is an explicit helper constant, not a new platform limit.
# Direct fixed-flow OTA on both units — 2026-10-10

Operator explicitly authorized updating both units. D1 and D2 each accepted56/56 OTA frames for mode slot only, BL2 unchanged. Known UIDs gated before handoff. Peer WAIT300s acknowledged before each transfer and expiry verified before further access. Final prefixCRC c9d5de0b on both, valid1/mode0, native curve2/controlIDLE/saved0, fresh26Hz and advancing CN105 replies/snapshot sequences on each. Every helper cleanup verified; Shelly relays remain off. No heating target writes or functional direct-target trial during installation. Local evidence P0080/effect-learning/update-both-20261010T044120Z. Existing tracked paths only; file index unchanged. No commit/push. No new generic knowhow beyond the established addressed handoff/identity checks.

## P0080 brine pump A3 extension (2026-10-10)
OCH722A service manual p30 identifies decimal018 output step0..10 and019 RPM0..9999. A3 support is a wire-mapping candidate pending physical observations, not a confirmed flow sensor. Schedule27,28,18,19 with a full FAST round between service operations; original retry ownership/limits retained. Snapshot schema1 remains20 fields: index11 step, index10 running derived ONLY from valid in-range RPM>0. ZeroRPM is valid stopped feedback, never inferred from missing data or step0. Controller feedback still needs physical correlation for the hydraulic test.
FC04 zero-based87..92 (018) and93..98 (019): retained raw, protocol-valid flag, age_seconds, last status, completion generation, ever-completed. Raw/protocol-valid do not perform engineering range checks; snapshot does. Age TTL60s, link-down invalidates all four services, no stale value becomes valid zero. Temperature and pump sources are asynchronous; a stopped test must require fresh repeated RPM samples and actual water-pump stop feedback. No new pump commands. Only drift/service chunks differ from installed direct-flow; BL2/layout/ABI/control unchanged.

Native ASan/UBSan and actual ARM cross-slot tests passed. OTA C engine1037 mutation cuts, host fake-RPC update/lost-ACK/cleanup passed. Existing tracked paths only; index unchanged. OTA proceeding under operator hydraulic-test task. Knowhow promotion deferred until physical mapping is checked.

Physical deployment completed on D1/D2: prefixCRC3f41636b, UID verified, normal curve power1, valid CN10526Hz, advancing snapshots/counters. Both WAIT periods expired and all four helper cleanup records verified. A3/018 D1 raw10, D2 raw16; A3/019 D1 changed3810->3780, D2 raw3810. D2 level remains range-invalid, raw retained; no guessed scaling. Firmware test passed, hydraulic circulation conclusion still pending.

## Hydraulic checks in both directions — 2026-10-10
VP2-off/VP1-heating and VP1-off/VP2-heating completed. Qualified stopped feedback (fresh RPM0, water pump0, compressor0) held187s and183s respectively. Off-branch water flow0L/min in both; reverse-flow sensitivity unvalidated. Both off-branch brine temperatures settled near2/3C; no brine flow sensor, so bypass unresolved. Both settings restorations and helper cleanups verified; no forced heating target needed. Evidence: workspace P0080/effect-learning/hydraulic-off2-20261010T052949Z and hydraulic-reverse-20261010T055830Z. No tracked paths added/moved, index unchanged. Knowhow promotion intentionally deferred: display-interference hypothesis and brine mapping/flow interpretation need further validation.

## EFFECT freshness and bus refresh — 2026-10-10

Offline candidate only; no OTA or pump writes in this change. Operator explicitly requested that values younger than one minute count as fresh. Direct telemetry, compressor compatibility registers and EFFECT source/last-pair admission now accept age <60000ms; age >=60000ms is stale. A known lost link still invalidates immediately. Native control readback guards retain their independent timing; measurement freshness does not authorize stale write guards. Temperature/flow pairing still requires <=2000ms acquisition skew, distinct generations and a heating-mode observation after the pair. Short-window warmup pauses adjustments without aborting an established session; it does not permit initial EFFECT admission or a new power adjustment without qualified feedback. Lease expiry and hard invalid/DHW/zero-flow guards remain.

Integrated real CN105/sampler/controller regression reproduced the former entry failure:220ms replies, six A3 attempts, accepted1/applied0, Hz reaches10000ms during entry and BAD_FEEDBACK restores the curve. CONTROL now allows complete FAST refresh rounds between owned transactions, with proactive refresh at6s Hz age; no interruption of owned A3/CONTROL frames. Refresh completion remains owned when partial feedback suspends APPLY. RESTORE is not gated on successful GET04 refresh.

Validation: complete host ASan/UBSan suite passed, including59999/60000ms boundaries, warmup recovery, real scheduler entry with220/500ms replies and varied timing, actual adjustment, stale Hz/DHW/zero-flow/link-loss faults and restoration. Actual built ARM module/veneer/pump/direct-target tests passed. OTA C engine passed3607 mutation cuts; fake Shelly host transfer/lost ACK/identity/cleanup passed. No physical validation of this candidate yet.

Candidate: procon/modular/build-effect-refresh. Common2816/12288, mode10072/12288, drift2736/4096 bytes. Only these three chunks change versus build-brine-pump; BL2 unchanged, layout/ABI unchanged. Existing local P0080 changes preserved; no commit/push. File index unchanged because existing tracked sources/docs were updated. Generic knowhow promotion deferred pending physical validation; this is currently a project-specific scheduling correction.

# P0080 dual6kW trial — 2026-10-10

Both units installed and verified at prefixCRC9da1db61. BL2 unchanged. D1 initial seq24 reply was truncated (25/44bytes); resume arrived after120s inactivity timeout. Full-set recovery through intact BL2 succeeded, followed by ordinary three-slot update ofD2. All identities, manifests, advancing native replies and helper cleanup verified. Uploader local wrapper now retries identical CRC-invalid/truncated reply frames; firmware duplicate handling was already tested. Physical cause of the one truncated reply is unknown.

Operator-authorized native EFFECT6000W each, maximum requested38C, supervised180s leases renewed during the run. Both applied confirmed; duration1800.87s.49 complete paired host observations, plus command/control logs. Both remained active throughout, no native stop/start during the trial, no hard-feedback abort; pending/ready alternated without aborting. Both ended at36Hz. All commands and responses retained in local rpc.jsonl/events.jsonl.

|Last10min|VP1|VP2|
|---|---:|---:|
|Mean qualified rolling heat power|4.123kW|3.629kW|
|Range|4.005–4.297kW|3.344–3.931kW|
|Standard deviation|0.084kW|0.238kW|
|Samples with ready feedback|14|14|
|Maximum actual supply over trial|34.5C|34.5C|

Six-kW tracking failed: both reached latched EFFECT_CUMULATIVE_CAP (reason6), after five1C increases from30.5C to35.5C. Actual temperatures were well below40C. After this latch no further up-regulation occurred, despite target6000W. No clear alternating control oscillation: target only increased, then held; frequency rose and largely held. This does not establish stability of an unrestricted regulator. Thermal power is derived from quantized temperature/flow, not calibrated electrical measurement. Approximate integration of sampled rolling heat power is1.84+1.59=3.43kWh, versus6kWh for continuous6kW each over30min. This is an estimate, not a validated energy counter; sampling and moving averaging affect it.

Both restored and read back: power1, curve mode2, flow target3050, DHW5200, boost0; controlIDLE/saved0/error0, one verified restore each. Native operating mode0 immediately after restoration is consistent with removing the elevated heating demand. Helper stopped/disabled, serial runtime reset to115200, relays remain off. No live process left running.

Operator clarified future control: actual supply ceiling40C is separate from demand setpoint up to55C. Fast high initial demand must be reduced as power approaches target, with trend/lag braking and temperature protection. Remove/replace the cumulative+5C latch. Future house optimizer2kWh heat per15min means8kW mean total, requiring integration of delivered energy and remaining-energy/remaining-time allocation. These changes and softer stale-data fallback are documented requirements, NOT implemented or installed by this trial.

No Git commit/push. Existing tracked package report/changelog updated, no tracked path additions. General knowhow promotion considered: retain the transfer incident as package evidence until repeated/root cause known; no unsupported Shelly defect claim.

Local evidence: P0080/effect-learning/dual6kw-20261010T103106Z and recover-install-effect-20261010T100944Z.

## Fast demand candidate 2026-10-10
Operator authorized fast-law build, OTA and15min dual6000W trial. PrefixCRC6137dc5e, mode10736/12288 bytes; only mode slot changes from9da1db61, BL2/ABI unchanged. Cap>4000 selects fast law with command ceiling5500; <=4000 retains legacy behavior for compatibility. Actual supply>=4000 aborts/restores in fast mode;>=3800 or positive30s trend projecting3900 brakes demand. Large deficit can request55C promptly; approaching target removes boost to supply+1C,15s decisions then adjust. Measurement age>=15s cannot sustain a new55C decision; existing hard stale60s/link/lease paths still apply. Native pause promptly drops boost and keeps mild demand. The old+5C and unresponsive latches do not constrain the fast branch. Tests: native ASan/UBSan suite, real wire scheduler with55C and faults, fast-law unit boundaries/temperature/pause/aging, host encoder5500/5501, actual built ARM boost/brake,1551 C OTA mutation cuts and fake RPC sender success/lostACK/cleanup. Physical performance not claimed until new trial. Known local changes preserved; no commit/push; existing tracked paths only, index unchanged. Readback decoder now permits55C; legacy v2 command limit remains45C. Uploader uses180s peerWAIT for one-slot update and retries exact packets on malformed responses.

## Current persistent fast candidate — 2026-10-10 (supersedes intermediate fast-limit descriptions)
Candidate prefix852841df; mode11448/12288 bytes. Only mode differs from installed intermediate6137dc5e; BL2/ABI unchanged. Uninstalled intermediatebc31ad62 was superseded before the physical trial. Fast missions (cap>40C, up to55C) retain mission/snapshot/lease across stale/invalid/zero-flow feedback, naturalDHW and communication/read timeouts. They suppress increases, lower an existing boost to39.5C when native heating guards can be verified, resynchronize native readback after link recovery, and resume when feedback qualifies. Native pause no longer has20min abort in fast mode. Legacy low-cap behavior unchanged. AUTO, lease expiry and explicit external ownership/power/mode/inhibit guards remain respected; the controller never forces power-on or overrides Mitsubishi safety logic. Readback mismatch remains an explicit control fault, not treated as successful delivery.
Thermal limiting engages at38C or positive30s projection39C, clamps requested temperature39.5C and disengages below37C with forecast<38C. Actual40C does not end the mission. Measured actual temperature above40C is still a violation of the supervised test boundary, not a commanded higher ceiling. Firmware reduces demand while retaining mission; physical overshoot and native minimum power cannot be ruled out by simulation. Existing phase LIMITED/reason TEMPERATURE_CAP plus requested/instant/short/slow power expose unmet demand and current achieved output, not a calibrated maximum-capacity estimate.
Native ASan/UBSan regressions and integrated real CN105/sampler/controller recovery cases (temporary lostHz, DHW, zero flow and total link loss) passed. Actual ARM boost/brake and module ABI tests passed. OTA engine1551 mutation cuts and fake Shelly duplicate/retry/cleanup tests passed. Live installer uses120s peerWAIT for one56-frame module update and35s remaining-margin gate. No commit/push; existing tracked paths only. Package-specific recovery evidence retained; general physical response/efficiency conclusions await live trial.

## Persistent fast physical trial and smooth capture candidate — 2026-10-10
852841df was installed and identity/CRC/CN105 verified on both D1/VP1 and D2/VP2. The authorized6000W each trial ran934.70s between paired sample boundaries (900s requested). Neither compressor stopped nor EFFECT mission aborted during the test. Normal ready/pending refreshes were tolerated. Both restored to power1, curve2, target3050, DHW5200, boost0, controlIDLE/saved0/error0. Helper stopped/disabled and cleanup verified; no live process remains.

Tracking FAILED: VP1/VP2 last-five-minute sampled rolling powers averaged5.164/4.708kW, ranges4.079–6.300/3.692–5.899kW. Actual supply maxima38/37C. Repeated55C-to34.5–38.5C demand drops caused marked power dips followed by renewed boost. This is evidence against the abrupt capture strategy; it does not prove a calibrated plant transfer function. Temperature-limited9kW operation was not tested.

Trapezoidal integration of ready/pending retained rolling heat power over the first900s estimates1.222+1.050=2.273kWh versus3kWh target. Pending values admitted only with last accepted pair age<60s. Temperature/flow quantization, smoothing and asynchronous reads limit accuracy; this is not a calibrated energy meter.26 paired observations plus full command/response evidence at P0080/effect-learning/fast-dual6kw-20261010T114328Z.

Operator described a rubber-band response:55C until clear acceleration, then progressively lower demand toward equilibrium. New smooth candidate replaces repeated boost/drop with retained capture state; filtered positive slope sustained30s or proximity/prediction of target triggers capture. Ordinary taper is0.5–2C per decision (at least15s plus readback), followed by corrections up to0.5C; no deficit-triggered jump back to55C. Normal pending FAST refresh preserves trend. Thermal and stale-data protection can reduce faster, and persistent mission/restore logic remains. The landing-demand estimate and gains are empirical and need live validation.

Smooth candidate prefix67ff1a3e, mode11624/12288 bytes; only mode changes, BL2 and ABI unchanged. Complete ASan/UBSan host suite, built ARM module/direct-control/taper tests,1551 OTA mutation cuts and fake Shelly transfer/cleanup passed. Initial OTA test used an obsolete local backend library; rebuilt against current OTA source and correct layout, then all checks passed. Header revisions matched installed baseline before final plan; final plan only slot2(mode). Candidate is NOT installed. D1/D2 remain852841df in restored curve mode. No commit/push. No tracked paths added/removed; index unchanged. Knowhow promotion intentionally deferred: package-specific empirical response remains in this report until repeated validation.

## Smooth controller installed and physically tested — 2026-10-10
Both D1/VP1 and D2/VP2 now run prefix67ff1a3e. Mode-only OTA, original identities checked, peerWAIT120s respected, both manifests/native curve state and advancing CN105/snapshot counters verified. Evidence: P0080/effect-learning/update-smooth-20261010T124105Z.

First trial smooth-dual6kw-20261010T125652Z aborted: D1 error7/lease expiry. Frequent APPLY states starved host renewal, which only attempted renewals when a captured control state was ACTIVE. Firmware currently accepts equal-intent renewal only in ACTIVE; this is an unresolved short-lease/in-flight renewal limitation, not a thermal cutoff. Both restored. For the bounded repeat only, host lease was extended from180s to1800s to cover startup and900s observation. This is a test workaround, not a firmware renewal fix. AUTO restoration and actual-supply>40C supervised stop remained.

Repeat smooth-dual6kw-20261010T130226Z completed932.15s to final paired-sample boundary (900s requested),26 paired observations. Both began in native pause, retained mission, restarted without a new start command, then passed through startup/settling and acceleration. The mandatory native pause and roughly26Hz startup plateau consumed much of this quarter; do not directly compare its energy against the previous running-start trial.

Demand descended from55C through incremental intermediate values; no repeat jump to55C after capture. Both reached approximately6kW, then fell again. Last5min rolling-power averages: VP1 5.167kW (3.737–6.250), VP2 5.372kW (4.458–6.409); each50% of these eight observations within5.5–6.5kW. Maximum measured supply36.5/35.5C. Final paired sample4.056/4.458kW. Tracking stability FAILED despite successful taper and mission retention. No40C violation, no mission abort during repeat. One acceleration/capture cycle only; long-run oscillation frequency/stability cannot be concluded. Working hypothesis: taper continues too far after acceleration fades; next tuning should reduce ongoing braking as slope turns down, avoiding a new full-boost jump. This remains an empirical hypothesis.

First900s trapezoidal integration of raw snapshot water-side heat power, with zero for confirmed stopped compressor, estimates0.753+0.698=1.451kWh versus3kWh requested. Complete900s coverage by this method, but quantization/sampling and uncalibrated flow/temperature limit accuracy. Rolling-average integration has incomplete startup coverage and is not presented as total energy. Evidence includes analysis.json, energy-tracking.json and raw-energy.json.

Both restored and read back: power1, mode2(curve), flow3050, DHW5200, boost0, controlIDLE/error0/saved0. Helper stopped/disabled, cleanup verified, no live process remains. Native operating_mode0 just after restoration. Firmware remains67ff1a3e. Existing tracked documentation updated, no added/removed/moved tracked paths or index changes. No commit/push. Knowhow promotion deliberately deferred: empirical controller tuning remains package-specific; short-lease renewal limitation is explicitly retained here for the next controller change.


## Hz-leading regulator and in-flight lease renewal — 2026-10-10

Host pilot on67ff1a3e completed900s with direct targets: last5min means5.754/6.002kW; actual maxima39/38.5C. VP1 fell late after the old thermal clamp, so sustained tracking is not claimed. Both restored and helper cleanup verified. Evidence: `P0080/effect-learning/rocket-lead-20261010T141602Z`.

Built candidate982e160b:35s Hz lead/60s acceleration, initial45C with gradual corrections up to configured55C, recent-Hz braking guards, continuous thermal ceiling and15..59s feedback hold. Same-intent lease renewals preserve an already-applied EFFECT mission through internal APPLY transactions. Initial/unapplied/changed-intent rules and exact retry semantics remain.

Mode-only update,11984/12288B, RAM984/4096B; BL2/ABI unchanged. Full host ASan/UBSan, final-image ARM and1551 OTA mutation cuts passed. Deployment in progress; native physical trial pending at this entry. Existing tracked files only, index unchanged; no commit/push. Knowhow promotion deferred pending repeated physical validation of empirical gains.


### 982e160b installed / autonomous quarter-hour result

- Both D1/VP1 and D2/VP2 were verified after mode-only OTA; BL2 is unchanged.
- The native 6000 W mission on each pump completed with renewable 180 s leases. Both were restored to curve target 3050, DHW 5200 and boost 0; helper cleanup was verified.
- Both first reached 95% about 236 s after the first 45 °C demand. From mission start, this took 683 / 779 s because of native pause and startup delay. Final power was 5.774 / 5.446 kW. The requested reference curve was NOT met. Maximum actual supply was 37.5 / 36 °C.
- Brief operation near the target improved without the previous large demand drops. Startup delay, the remaining power deficit, limited observation near the target and the lack of sustained qualification at 40 °C remain unresolved. See the implementation report and local evidence `rocket-native6kw-20261010T144437Z`.
- No new tracked paths or file-index changes; no commit or push. General knowhow promotion was intentionally deferred.

## Early startup and fine correction candidate 784a48ae — 2026-10-10

- Added thermally bounded startup demand during fast SETTLING after the first coherent heating pair younger than 15 s, with native heating mode, positive valid Hz and valid supply. Initial demand is at most 45 °C and is withheld if power is already within 150 W of target or higher. Native guards/readback remain mandatory; repeated thermal reductions continue during settling.
- Preserved readback for sent commands and cancel unsent startup adjustments if qualification is lost. Startup is marked complete only after verified demand. Fast SETTLING preserves history and the decision timer; native pause still resets them.
- Reduced the quiet band to 150 W and added signed sub-0.1-°C command carry. Reset conditions cover sign reversal, quiet/no correction, native pause, a 60 s history gap and same-direction saturation.
- The native test completes within 10 s after the first qualifying heating pair, not within 10 s of mission start. A native restart pause of about 10 minutes may still occur. The zero-Hz pause margin, DHW handling, lease/AUTO restoration, configured 55 °C maximum demand and actual 40 °C supervision are unchanged.
- Grouped private regulator state to keep the existing `-Os` build within the fixed slot: mode 11824 / 12288 bytes, RAM 984 / 4096 bytes. Only mode changes from 982e160b; BL2, layout, exports and public schemas are unchanged.
- Passed the full host ASan/UBSan suite, actual final ARM startup/readback/thermal tests, all 1551 OTA mutation cuts and fake Shelly transfer/cleanup tests. OTA and physical validation are in progress; improved physical startup or tracking is not yet claimed.
- Updated existing project documentation only, without new tracked paths, file-index changes, commit or push. Generic knowhow promotion remains deferred pending physical validation.

## Entry-transition correction d64080c7 — 2026-10-10

- Physical 784a48ae entry failed on both pumps before `applied` advanced: error 8 / BAD_FEEDBACK. Both original curve settings and helper cleanup were verified. No sustained power-control result exists for that attempt.
- Reproduced a same-millisecond race between cached READY feedback and newly accepted native mode 0, in both the control model and real sampler/controller integration. Pre-fix tests fail; corrected tests pass.
- Fast EFFECT now treats an unqualified cached READY report as collection only for already-permitted native modes. Unsent actions yield and requalify guards; sent SET/readback state, original snapshot and bounded initial lease are retained. Native inhibit, ownership, power and unsupported-mode protections remain unchanged.
- Retained early startup, fine-carry and thermal behavior. Only mode changes: 11840 / 12288 bytes, RAM 984 / 4096 bytes, unchanged BL2/ABI/schema and `-Os`.
- Passed full host ASan/UBSan, 60 entry-transition combinations, real sampler/controller reproduction, actual final ARM transition tests, all 1551 OTA mutation cuts and fake Shelly transfer/cleanup. Physical validation of d64080c7 remains pending at this entry.
- Existing tracked files only; no file-index change, new tracked path, commit or push. Generic knowhow promotion remains deferred.

### Thermal correction after the physical boundary breach

- Recorded the d64080c7 test failure: actual VP1 supply reached 40.5 °C despite a persistent 39.5 °C request; both curves and helper cleanup were restored.
- Replaced the static thermal floor with signed proportional feedback centered on 39.0 °C, shared across atomic entry, first-pair startup and running regulation. Forecast protection cannot raise a lower ceiling; extreme inputs cannot wrap the unsigned request.
- Passed the three focused sanitized host suites and added corresponding actual-ARM checks. Final build, full qualification and physical validation remain pending; no new success claim or ABI change.

- Final candidate e8fc6d86: atomic EFFECT entry, predictive braking and signed thermal ceiling; full host/ARM/OTA qualification passed. Added atomic-entry and predictive regression sources and refreshed the 769-path repository index. Mode remains within 12 KiB, with 24 bytes free. Deployment and physical qualification tracked separately.

- Installed e8fc6d86 on D1/D2 and completed the bounded30-minute physical test. Observed actual maxima39.5/39.0C; no poststart stops, no control errors, curve restoration and helper cleanup verified. Marked full tracking qualification incomplete: plateau prediction and slow recovery after thermal limiting remain; final5-minute means4.741/4.557kW. Added measured final results and explicit capacity/reserve distinction to the report and public behavior docs.

## Response memory and demand recovery candidate 7adaecf1 — 2026-10-10

Implemented the operator-requested follow-up to e8fc6d86. The positive Hz-rate forecast now retains a bounded1500W memory, decaying10W/s. A short flat-Hz interval no longer immediately removes the lead estimate. Observed deceleration, demand less than2C above actual, thermal clipping, native waiting and history discontinuity clear the retained lead. This remains an empirical forecast, not identification of Mitsubishi's internal integral law.

Rising estimated power suppresses extra gas only when its30-second projection approaches the goal (within150W). A persistent deficit therefore continues to influence demand. With both measured and predicted power more than750W below target, positive correction and demand less than2C above actual, the actuator may rise1C per qualified decision; otherwise its positive bound remains0.5C. The unchanged signed thermal envelope is applied last. No rejected/clipped command accumulates as future demand, and there is no repeated jump to45/55C after startup. Freshness, pause, ownership, lease and AUTO restoration contracts are preserved.

Qualification: complete ASan/UBSan host suite PASS; final ARM image PASS including retained-response decay, plateau behavior, recovery during modest power rise, thermal priority and all prior entry/restore/module checks;1551 interrupted-update cases PASS; fake Shelly sender PASS. The new predictive regression fails against the prior source at the flat-Hz comparison, and passes against the new source. Sampled-input shadow replay over the prior30-minute log changes15/40 VP1 proposals and7/48 VP2 proposals. In late VP1 observations near4.9kW, previously blocked positive proposals become bounded1C corrections. Replay holds historical measurements/targets fixed and acknowledges hypothetical writes immediately, so it is not a closed-loop simulation and establishes no new physical performance.

The mode image occupies12280/12288 bytes (8 free), with992 bytes of private RAM. The initial build exceeded the slot; a mode-only `-fno-inline-functions-called-once` setting and removal of duplicate pre/post step clamps allow it to fit. Final ARM tests verify the resulting code and veneers. Other module bytes, BL2, layout and public ABI remain unchanged; the exact OTA plan changes only slot2 from e8fc6d86 to7adaecf1. Artifacts, hashes, source fingerprints and logs are in `procon/modular/build-effect-response`.

This candidate is BUILT AND OFFLINE-VERIFIED, NOT INSTALLED. No device access or live control was performed for this follow-up. Both devices were last verified on e8fc6d86 in native curve mode after the preceding experiment. Physical response and tuning still require a bounded live trial; no claim that the reference curve has now been achieved. Existing tracked source/test/docs paths only; repository file index unchanged. No commit/push. Knowhow promotion intentionally deferred because these gains remain specific empirical hypotheses.


2026-10-10: Installed response-memory controller 7adaecf1 on both known Procon devices through mode-only OTA. Identity, advancing telemetry, native curve operation and helper cleanup verified; effect-control performance trial pending. Evidence: P0080/effect-learning/update-response-20261010T200545Z.

## 2026-10-11 — source-aware persistent EFFECT (VP1 follow-up)
User-authorized implementation and VP1 live trial. Hz and supply trends now use
independent source generation and sample time from the existing Drift snapshot
ABI. Duplicate polls do not manufacture history. Data aged15–59s cannot increase
the request, including the old29.5->30C floor corner case. Adds a soft predicted
supply constraint on desired Hz acceleration ahead of the existing hard thermal
ceiling. All configured demand caps now use the same persistent EFFECT behavior;
removed old cumulative/unresponsive and20min native-pause abort paths. Lease,
native guards and restoration remain. Link loss during restoration no longer
restarts EFFECT; interrupted initial combined entry resumes with guards/readback.

Candidate `build-effect-source`: prefixCRC7136193e, Mode12280/12288 flash,
1128/4096 private RAM. ABI/layout unchanged. Only OTA slot2 changes from installed
VP1 build-p81/71b30837; BL2 and all other chunks are byte-identical. VP2 remains
7adaecf1. Reproduce using build.py --out build-effect-source --revision 2
--change-slot common,dispatcher,mode,drift,service.

Verification: complete sanitized host suite; compiled ARM module/source-history
and snapshot tests; RAM flash writer checks; actual OTA engine1551 mutation cuts,
full-set repair, corruption rejection; fake Shelly sender/lost ACK and helper
checks. Snapshot's older40s stale fixture updated to the existing60s TTL.
Live installation and the supervised15min VP1 trial completed; results follow.
Rebuild using `make effect-source` from procon/modular; tests use this exact output directory.

Physical result: installed7136193e on VP1 only; VP2 remains7adaecf1. The900s
mission reached90% of6kW at249.682s,95% at525.763s and100% at703.655s, using
the qualified rolling water-side heat estimate. Peak short mean6.091kW;
last5min time-weighted mean5.713kW, range5.411–6.091kW and trend−67.4W/min.
Last observation within the mission:5.411kW,46Hz, supply38.0C, return32.5C,
flow14L/min and requested42.0C. No observed in-trial compressor stops or DHW;
maximum actual supply38.0C. Source ages stayed below7.41s.

Thus safe uninterrupted operation was demonstrated for this trial, but sustained
6kW tracking was NOT achieved. The existing hard demand ceiling reaches42C at
flat actual38C and restricted demand late in the run. This is controller
conservatism, not evidence that the heat pump cannot deliver6kW. Separately tune
the soft acceleration constraint and hard envelope before any further trial;
retain the user's actual40C limit. This run does not identify a new plant model.

VP1 restoration verified: native curve2, target30.5C, power1, DHW52C, boost0;
controller idle, lease0, saved/touched0. VP2 native control was untouched and
remained on its curve. Shelly helper restored and native Modbus verified after
OTA. Peer WAIT300 caused an unnecessary serial verification delay; the user
correctly noted that verified VP1 readiness need not wait for VP2. That updater
scheduling change is documented, not implemented in this continuation.

Evidence (private workspace):
`P0080/effect-learning/update-source-vp1-20261011T193307Z/` and
`P0080/effect-learning/source-trial-vp1-20261011T194239Z/`.
Trial events SHA256:
`34b938c9a425cd3a015228f368b5c1c21c0b50be074ccb1ddb0e5958da3b686a`.
The reproducible offline analyzer is
`procon/modular/tools/analyze_source_trial.py`. Final plots were visually checked.
The900s rolling-mean integral is1.2071kWh, an integral of lagged feedback rather
than a calibrated energy meter. Raw-power integration covers only810.2s because
seven invalid/incoherent snapshots leave gaps; its1.1042kWh is not quarter-hour
energy. Existing knowhow was updated; no commit or push in this continuation.

## 2026-10-11 — predictive thermal priority, dual6/5kW follow-up
Operator explicitly authorizes implementing the follow-up, OTA both units and
testing VP1 at6kW / VP2 at5kW. Later clarifications override the old thermal stop:
keep actual below40C with higher priority than power, but regulate overshoot down
gently and continue the mission. Neither40C,42C nor an exposure timer aborts the
trial. Native safeguards, ownership, data-failure paths and lease remain.

Current candidate uses source-age-aware60s prediction and a continuous thermal
demand goal. Qualified water history uses positive margin gain8; incomplete
history uses conservative gain3 with the same horizon. No negative-slope credit.
All normal running decreases are bounded0.5C per30s, including SETTLING recovery,
with downward floor=min(current verified demand,actual+0.5C). The floor never
chases a hot actual temperature upward. Configured cap remains55C in the trial.
This is empirical control, not a recovered native law or guaranteed no-stop plant.

Final artifact: Mode12264/12288 bytes,1128/4096 privateRAM, SHA256
`f30e451dfdba09e32d2c7eabfe024850028e1d4c4d7d3487fa3fbffb997e43e2`.
D1 manifest `b39273d4`; D2 `b8fb9712`. Only slot2 differs from each installed
baseline; D1 retains P81 diagnostics, D2 retains its original Common/Dispatcher.
BL2 and other chunks are byte-identical to their respective baselines.
Mode-only LTO/noschedule-insns2/retained memset fits the fixed12KiB slot.

Offline qualification before deployment: complete ASan/UBSan host suite,
actual public ARM controller paths plus veneer/init/snapshot/corrupt-slot tests
on BOTH artifacts,1551 actual-C OTA mutation cuts per artifact pair, sender/lost
ACK/cleanup checks,13 dual harness tests. LTO eliminates private helper symbols,
so private-ABI ARM probes are explicitly skipped for optimized builds; their
fine-grained behavior remains host-tested, and new exported ctl_* ARM scenarios
verify entry/readback, hot taper/cadence/positive margin, cooling, source-only
staleness and exact AUTO restoration. No aliasing of constprop helper ABIs.
The unrelated historical test_arm.py fixture mismatch remains previously noted.

Read-only preflight: both native curves2, target30.5C, power1, DHW52C, boost0;
VP1 observed0Hz and VP2 20Hz. Deployment and physical outcome follow below.

Physical completion: Mode-only OTA verified both new manifests, native9600/8N1
Modbus and prior helper restoration. Each Mode transfer used56 acknowledged
frames and about30s of transfer time; peer WAIT120s expires independently.
The subsequent dual mission started20:36:32UTC, with both already running20Hz,
and covered900s after both ACTIVE. No cold-start performance claim.

| Metric | VP1, target6kW | VP2, target5kW |
| --- | --- | --- |
| Maximum observed actual supply |39.0C|39.0C|
| Time>=40C on supported interpolated record |0s|0s|
| Observed compressor stops during mission |0|0|
| Peak qualified short mean |5.863kW|5.781kW|
| Last5min time-weighted short mean |4.719kW|5.568kW|
| Last5min short-mean range |4.389–5.181kW|5.355–5.781kW|
| Last5min trend |−0.151kW/min|−0.062kW/min|
| First90% /95% /100% of power target |262/360/not reached s|216/235/246s|

The temperature objective held for this trial, and the mission did not give up.
Sustained6/5kW tracking was NOT achieved. D1 was thermally limited in all30
last5min observations; D2 remained above5kW both within and outside that phase.
Phase and delayed short mean are not simultaneous causes and effects. The
sum of time-aligned short means averaged10.287kW in the last5min, range
9.750–10.800kW and trend−0.205kW/min. Neither pump entered DHW during the trial.

Both share the floor circuit, but measured branch conditions differ. At the final
bracketing sample D1 return34C/14Lmin would require about40.15C supply for6kW;
D2 return33.5C/15Lmin would require about38.29C for5kW. These are instantaneous
uncalibrated water-model estimates, not fixed capacity limits; flow, return and
coarse sensor resolution change the result. D1's empirical envelope can also be
conservative. D2's remaining overshoot cannot be explained by its temperature
ceiling alone. No repeated hunting/cycling was established: last5min power
correlation+0.65 falls to−0.19 after linear detrending, with asynchronous and
overlapping measurement windows. A shared load is not proof of unstable control.

Full900s integral of qualified short means:2.3269kWh, compared with2.750kWh for
instantaneous flat target delivery. This is lagged estimated water-side feedback,
not a calibrated energy meter. Raw water-model coverage is only819.45/780.98s;
no full-quarter raw energy total is claimed. Final bracketing observations were
D1 at904.100s:4.693kW,40Hz,39/34C,14Lmin,request40.43C; D2 at906.308s:
5.486kW,46Hz,38.5/33.5C,15Lmin,request41.42C. These are after the900s endpoint,
before AUTO; the analyzer separately reports the last in-window observations.

Restoration verified on BOTH: native curve2, target30.5C, power1, DHW52C,
boost0, controller IDLE/error0, lease0 and saved/touched0. No thermal/timer
abort occurred and no control errors were observed. The new Mode remains installed.

Evidence(private workspace): `P0080/effect-learning/update-adaptive-both-20261011T202952Z/`
and `P0080/effect-learning/adaptive-dual-20261011T203607Z/`.
Final events SHA256:`cc054956fd3613b91ce7253f03227432406861c9331f2db228c7fba8087e550d`.
Reproduce analysis with `procon/modular/tools/analyze_adaptive_dual.py LOG_DIRECTORY`
(requires matplotlib and its adjacent offline source-trial helper). The analyzer
has no live transport imports. PNG/SVG plots were visually checked; synthetic
fixtures verify strict40C equality, gaps, aggregate timing and correlation limits.
Package docs, function map, file index and existing knowhow updated; no commit/push.

## 2026-10-12 — repeat with both pumps at5kW
Operator requested a new5/5kW trial. No firmware build, OTA or regulator change.
Installed manifests remain D1 b39273d4/D2 b8fb9712. The supervised harness now
accepts explicit --vp1-w/--vp2-w (5000 or6000), retaining prior defaults; both
initial packets and renewals at5000W were verified offline, as were two-device
restoration and900s endpoint handling. Physical command:
`python3 P0080/effect-learning/adaptive_dual_trial.py --execute --seconds 900 --vp1-w 5000 --vp2-w 5000`.

Current preflight found curve2/target30.0C, power1, DHW52C, boost0 on both;
these settings supersede the prior run's30.5C restoration baseline. Both Hz were0
at preflight. VP2 started during entry, before both ACTIVE at04:52:05UTC;
VP1 first showed positive Hz at300.93s. Its initial pause is not a post-start
compressor stop. A native restart delay is plausible but not identified exactly.

| Metric | VP1, target5kW | VP2, target5kW |
| --- | --- | --- |
| Qualified short-mean peak |6.456kW|7.005kW|
| Last5min time-weighted short mean |6.190kW|6.035kW|
| Last5min short-mean range |5.735–6.456kW|5.791–6.395kW|
| Last5min trend |−0.132kW/min|−0.088kW/min|
| Maximum observed actual supply |40.5C|39.5C|
| Observed post-start compressor stops |0|0|

The run completed900s, but neither sustained5/5kW tracking nor VP1's strict<40C
objective passed. Last5min combined time-aligned short mean12.225kW versus10kW
requested. VP1 reached40C at about692s and40.5C in the final in-window snapshot
at898.79s. Supported capture-time interpolation gives207.66s >=40C, including
10.66s >40C; this is interpolation, not direct timing of threshold crossings.
Distinct source-time estimates are209.76/11.56s respectively. VP2 had no>=40C
observations. There was no temperature/timer abort, native safety override or
in-trial control error. All primary source ages stayed below8.26s.

VP2 exceeded6kW before VP1's compressor started, so the large overshoot cannot
be explained solely by two simultaneously active power loops. Frequency plateaus
were followed by another increase: e.g. VP2 42->52->62Hz after briefly reaching
its power goal. The applied request declined gradually45->39C, yet delivery
remained high. At the end VP2 still ran48Hz with actual39.5C/request39C; being
at or slightly below actual did not force an immediate stop in this observation.
That is not evidence for a universally safe native stop margin.

Code review explains a remaining control-authority restriction: bounded_demand's
floor=min(current_request,actual+0.5C) forbids any further decrease once current
is at/below that margin. This pinned VP1 at40.5C while actual reached40.5C and
VP2 at39C while actual was39.5C. It prevents chasing temperature upward, but can
also prevent continued gentle braking. The0.5C/30s slew and fixed60s forecast
do not account for several minutes of request unwinding. Earlier taper and a
better-qualified lower-demand boundary are next design questions; no such change
was implemented or flashed during this repeat. Different start/return conditions
mean this is not a controlled A/B comparison with the previous6/5kW test.

Full-quarter energy is NOT reported: qualified power is absent during native
pause/startup, and raw water-model coverage is842.07/851.13s, not900s. Last5min
power integration has full300s coverage on both. Estimates are uncalibrated
water-side heat, with quantized sensors and delayed overlapping short means.

Both original curves restored and verified: mode2,target30.0C,power1,DHW52C,
boost0; controllerIDLE/error0,lease0,saved/touched0. No firmware changes or
additional live writes after restoration. Evidence:
`P0080/effect-learning/adaptive-dual-20261012T045141Z/`.
Events SHA256:`888e9643e73634a3a2b537705d560153ff48230df2281fb9dc6303cae03b0d98`.
Portable adaptive analyzer produced JSON/PNG/SVG, plot visually verified.
No commit or push in this continuation.


## 2026-10-12 — fixed-flow60C firmware candidate

Explicit user direction to change firmware after sync warning authorizes this focused local continuation. v2 flow commands (fixed-flow/targets), host encoder and GET09 readback now permit6000cC;6001 rejected. EFFECT maximum5500 and thermal policy unchanged. Host ASan/UBSan regression suite passed, including full6000 application/AUTO and lease-expiry restoration, and Python encoder boundary. Actual compiled ARM snapshot/public-controller suite passed; fixed60 ARM boundary/application/restoration additionally checked. Only Mode and manifest differ from build-effect-adaptive; BL2 and every other chunk byte-identical. Mode12256/12288bytes. Mode SHA2567de8d37529782f9567185065d778586b45a68e774090a3a93a62fef113b953da. Candidate:procon/modular/build-fixed60/. No installation or live commands in this firmware-edit turn; physical FTC acceptance and requested30min/50C experiment remain pending. No commit/push. No new tracked paths; file index unchanged.

Build environment recovery: prior /tmp compiler headers and Python packages were missing. Re-downloaded pinned Arm14.3 archive, verified SHA25630f4d08b219190a37cded6aa796f4549504902c53cfc3c7e044a8490b6eba1f7, extracted separately; fresh isolated pyelftools0.33/Unicorn2.1.4 environment. Sandbox JIT failed; approved outside-sandbox test passed. Knowhow promotion skipped: environment repair and range adjustment are package-specific, not a new control-law finding.


## 2026-10-12 — fixed60 installed on VP1, experiment authorized

Mode-only OTA completed and both devices verified on native Modbus/curve. D1 manifestc7a0fbcb; D2b8fb9712 unchanged. OTA actual-C1551 mutation-cut checks passed before deployment. Preflight D1curve30C,D2curve30.5C,both power1,DHW52C,boost0,20Hz. Evidence outer workspace P0080/effect-learning/update-fixed60-20261012T063109Z/. Shelly transport/helper source restored, peer WAIT expired, CN105 counter advances. User-authorized experiment next: VP1fixed60C,VP2OFF,stop at actual>=50C or1800s from command start,180s leases renewed each60s,finally AUTO restore both. No EFFECT controller in this experiment.


## 2026-10-12 — fixed60 response trial, operator-ended

VP1 fixed60C with VP2 power OFF/0Hz throughout active samples. Both were already20Hz before isolation; this is NOT a compressor-cold-start experiment. Timer began06:36:37UTC, fixed60 fully verified18.68s later. Last active sample1483.90s (24m43.9s); user requested early termination, SIGTERM dispatched, finally restored both. The scheduled1800s/50C endpoint was not reached. Transport approval/process-control overhead means do not claim an exact60s delay from user's early-stop request. Native readbacks at end: power1,curve2,target30.5C,DHW52C,boost0,both controllerIDLE,error0,saved0,lease0. VP2 native mode1 after restoration: DHW priority resumed naturally. VP1 controller snapshot captured30.5C on entry (curve moved from preflight30C); restoration matches the actual saved snapshot.

### Response and approximation

First observations relative to request:20Hz at2.8s;30 at68.8;32 at129.4;40 at134.7;42 at192.5;52 at205.9;62 at255.8;70 at312.5;84 at330.2;76 at372.7;70 at377.5;84 at441.0;92 at499.0;94 at613.6;96 at677.0;98 at736.7;100 at794.9;102 at859.5;104 at917.8 through last1483.9. Short32/42/70/76 values include transitions, not necessarily commanded steady levels. Polling approximately4–6s and source ages mean these are observation times, not exact internal scheduler edges.

Initial major steps roughly10Hz/min, followed by transient84->70 reduction and recovery. At94..104 the five successive intervals are63.5,59.6,58.2,64.6,58.3s (mean60.85s), with exactly+2Hz.92 held114.6s before94.104 held at least566.1s (9m26s), despite remaining target delta16.5->14.5C: strong evidence for active saturation in this run, not proof of absolute device maximum. A provisional prediction model therefore needs minute-scale plateaus, state-dependent step sizes, transient native limitation and a104Hz observed cap; flatHz alone cannot justify retaining large demand near the power goal. This single fixed target cannot identify an independent delta->Hz-step function because elapsed time, frequency and temperature change together. Lower-delta repeat would discriminate saturation/rate limiting from static delta dependence.

Brine around temporary reduction:3/1C at first84Hz,3/0C before84->76->70, then3/1C before recovery84. Later94..104 ran with2/-1C, so a simple fixed0C outlet threshold does not explain the dip. Dynamic refrigerant/pressure/startup limits remain possibilities; no internal limiter flag was observed/proven. A3 brine has integer-degree quantization and roughly30s refresh; no invented exact crossing times. Maximum actual supply46C, final45.5C,return35.5C. During HOLD every requested target was6000; controllerACK count stayed2 after initial application, so repeated lease renewals did not inject additional SET commands. Native regulation generated the frequency staircase. Power remains an uncalibrated water-side model; preserve invalid gaps.

Evidence outer workspace:P0080/effect-learning/fixed60-20261012T063531Z/ (raw events,transport,restoration,outcome,analysis,timeseries,PNG/SVG). eventsSHA256:50394c8ef829113487fd5e119cd6d66066371dac729f29233e32a36d11f76a96. Intentional stop remains in failure.json as KeyboardInterrupt; outcome marks operator end and verified restoration. No active trial/script resource remains. Firmware D1c7a0fbcb,D2b8fb9712. No commit/push. Existing tracked docs updated only; workspace runners/analysis are outside Git repo, generated build ignored. Knowhow promoted below.


### Two-clock hypothesis follow-up (offline only)

User proposes separately gated coarse~10Hz and fine2Hz mechanisms. Re-examined raw Hz sample timestamps using snapshot-header midpoint minus source age (rather than host receipt). The isolated+2 changes occur at upper observation bounds123.99,187.77,610.08,673.88,734.25,791.63,854.95,914.33s. Assigning minute indices2,3,10,11,12,13,14,15 yields an illustrative least-squares period60.729s and phase4.071s, residuals-1.54,+1.51,-1.28,+1.79,+1.44,-1.92,+0.68,-0.67s. This is NOT independently established clock precision: transition brackets are6.4–8.4s wide and integer cycle assignment assumes unobserved/suppressed fine steps in intervening minutes. Nevertheless early30->32 and40->42 align with the later94..104 progression, so two interleaved mechanisms are a useful hypothesis rather than merely an early/late mode switch.

Important alternatives: we observe reported actual Hz, not an independent requested-Hz signal.32->40 follows within one fresh-read interval;42->52 follows after an intermediate fresh42 read, roughly7–21s after the+2 transition. These could also be transient actual-frequency ramping toward a larger request, or a single periodic rule with multiple constraints. Simple additive model fails30+2+10=42 whereas next observed plateau40. Large excursions +14/-8/-6 also preclude assigning every delta to an independent exact10Hz contribution. Evidence supports minute-scale fine schedule and additional coarse/transient behavior, but does not prove two independently phased timers or their gating/safety rules. No new physical commands.


## 2026-10-12 — VP2 fixed60 repeat COMPLETE

D2 Mode-only OTA fromb8fb9712 toccc91f0d completed; D1c7a0fbcb preserved. Composed D2 artifact preserves all its previous non-Mode modules and BL2. C OTA1551 mutation cuts and actual ARM public/controller/snapshot suite passed. Evidence outer workspace:update-fixed60-vp2-20261012T091300Z/. Native transport restored and both CN105 counters advanced. No new permanent native settings.

Physical trial:fixed60-vp2-20261012T091859Z/. VP1OFF/power0/Hz0 verified during trial. VP2 began at22Hz, initially30.5C supply/28.5C return; not a cold start. Constant60C HOLD readbacks, only initial2 SET ACKs, lease renewals introduced no new native SETs. Ended automatically at973.254s after183s at104Hz; reason high_frequency_plateau_180s. Host stop condition required>=90Hz for180s and10distinct Hz source generations, plus retained50C/1800s bounds. Maximum supply43.5C, final43.5/34C,flow19l/min,water-model12.574kW; power is uncalibrated/quantized and invalid gaps retained. Brine2/-1C at end. No Hz decrease or compressor stop in active samples. Both verified restored:VP1power1,curve2,target30C,DHW52C,boost0;VP2power1,curve2,target30.5C,DHW52C,boost0;controllersIDLE/error0/saved0/lease0. VP1 nativeDHW priority resumed after restoration. No active task/script left.

### Comparing the steps

VP2 first-observed Hz sequence(seconds):22@2.4;32@68.4;34@126.6;42@134.4;44@181.2;52@189.2;54@242.1;62@250.6;72@306.9;84@314.7;92@367.7;94@515.9;96@607.1;98@619.3;100@672.4;102@729.5;104@790.3 through973.3. Thus32->34->42,42->44->52,52->54->62 are three repeated(+2,+8) decompositions of+10, with7.8–8.5s between first-observed intermediate and next value. Strengthens ramp/intermediate interpretation but does not prove requested-Hz timing. Cannot count every observed+2 as an independent fine-controller event. VP1 62->70->84 and VP2 62->72->84 share total+22 with different intermediate values. Both84->92 are+8; still possibly a clamp/stage boundary, not identified. VP2 did NOT reproduce VP1's84->70backoff.104 reached13m10s versus15m18s onVP1; supports common active cap, not absolute maximum proof.

Small-step timing differs:VP2 92held148.2s;94held91.2s;96held12.2s;98held53.1s;100held57.1s;102held60.8s. A universal uninterrupted61s+2clock is NOT established by the VP1 fit. Separate conditional clocks remain possible, but one mixed rule plus actual-Hz slew/limitations is not ruled out. Current measurement lacks independent requested-Hz channel.

Brine-in clarification:VP1 first4->3C at247.7s,3->2C at639.1s;VP2 at306.9s and619.3s. AtVP1backoff372.7..377.5s, inlet remained3C; no resolved abrupt inlet-temperature drop. Fresh-source brackets of inlet4->3:VP1(214.8,245.4]s;VP2(276.0,305.0]s. These are1C quantized threshold crossings, not evidence for an actual1Cfall in30s. Outlet1->0 observedVP1~343s,VP2~345s, then recovered1C on both (VP1~400s at70Hz;VP2~432s at92Hz). Similar outlet dip without VP2Hz reduction weakens a simple outlet-temperature or outlet-slope-alone trigger. Cannot exclude internal refrigerant/pressure/transient constraints or sub-degree faster observations unavailable here.

Events SHA256:82773387e5c1daa16b7014c3d22c76df774a8fa4e59323fbdc6baa6c98229ed2. Artifacts:events,transport,original-settings,restoration,outcome,analysis,timeseries,per-pump PNG/SVG and comparison PNG/SVG; plot visually checked. No commit/push. No new tracked paths; outer workspace scripts/artifacts remain outside Git checkout. Existing package/knowhow docs updated. Previous dirty work preserved.


2026-10-12 A3 frequency comparison preparation: extended exclusive service queue with16/17 and input372..383 records; Common routes unused words to Service. Host sanitizer regressions pass after adapting four-code test fixture to six codes. Compiled ARM composite validates distinct70/92 records, status/generation/TTL and existing controller restore behavior. Only VP2 Common+Service planned; all other chunks byte-identical to installed fixed60-vp2, manifest cf60109d. Operator authorizes repeat60C/50C-stop/30min/plateau test, VP1 resting. No new tracked paths for this continuation; file index unchanged. Raw runner/build artifacts local.

Completed VP2 Common+Service OTA, manifest cf60109d (VP1 preserved c7a0fbcb); native transport restored9600/8N1. Live evidence: outer-workspace P0080/effect-learning/update-frequency-vp2-20261012T101700Z and frequency-vp2-20261012T102151Z. Trial1223.615s,306 primary samples, target60C, peerVP1OFF; automatic high-frequency plateau180s stop; maximum flow46C. GET04 held104 for180.33s, A3/16 and17 both103 in repeated fresh replies. Each A3 yielded28 new in-trial completions (generations6..33, no gaps), median reply interval~44s; successful status2. No parser/UART errors, handshake count1; GET04 replies32->201. No additional native target SET after entry (ACK2). Restored both power1/curve2,DHW52,boost0; both controllersIDLE,error0,saved0,lease0. D1 curve target evolved30->30.5 naturally; no old-target overwrite.

Findings: GET04 plateaus52/62/86/92/94/98/102/104 corresponded to A3 raw51/61/85/91/93/97/101/103. A3 also changed93->94,97->98,101->102 without GET04 change. Strong evidence for coarser GET04 quantization, not an exact decoder proof. A3/17 changed61 while GET04 still52 (~20s before GET04first62); A3/16 reported84 while a later received GET04still70. Distinguish FTC reply freshness from source acquisition. GET04 observed92->86 at505.37s, back92 at569.06s (~63.7s); A3actual andtarget91->85->91. Flow remained~40C during this dip. Cause unknown; no claim that earlier unobserved dip is retrospectively proven. Brinein was2C at downstep, outlet0C; coarse/asynchronous channels do not prove protective cause. Pure10Hz/2Hz-timer deductions from GET04 now need revision; fine1Hz changes can be hidden. A3 named actual is not an independent physical speed measurement. Raw events SHA2566744f9a749a41695be30c56cabb23c29e85fb67d3bae91def67bf9ce0d6703c7. CSV, JSON and visually checked PNG/SVG comparison retained alongside rawlog. Knowhow updated; no new tracked paths, no commit/push.

Dense frequency follow-up: Service-only candidate manifest06e8dea7,1520/4096bytes; all other chunks byte-identical to installed cf60109d. Host ASan/UBSan suite passed. Actual ARM composite passed priority sequence including pending/retry cadence, ordinary queue after exit, existing ABI/restore/controller tests. Conditional priority limited to ACTIVE fixed-flow6000; no EFFECT changes. Live trial authorized by operator; runner plateau now checks both A3values stable180s with at least6distinct completions each. Background services may age out; no fake freshness. Existing tracked files only, file index unchanged.


## 2026-10-12 — dense A3 VP2 comparison COMPLETE

Service-only OTA06e8dea7 installed onD2, all other D2 chunks and BL2 byte-identical to cf60109d. D1c7a0fbcb unchanged. Host ASan/UBSan and actual ARM priority sequence, retry timing, exit to normal queue, ABI/controller/restore regressions passed. Service1520/4096bytes. No EFFECT changes. Existing tracked files only; no new tracked paths for this continuation, REPOSITORY_FILES unchanged by it. No commit/push.

Physical experiment12:11:26–12:34:48UTC,1401.591s (23m22),334 active primary samples. VP2 fixed60C; VP1OFF verified in333 peer samples. Unlike prior run, VP2 started at0Hz and waited before starting: first A3target35 at292.4s, first actual27 at309.2s. The prestart delay is observed, but no native lockout timer or thermal cold-start condition is established. Stop: both A3values103 stable180.073s,11/10 distinct completions during plateau. GET04=104. Actual supply maximum45.5C, final45.5/36C,flow19l/min. Final modeled water power12.574kW is uncalibrated, not a precise calorimeter result. No detected frequency decrease or compressor stop after start.

Restoration verified for both: nativepower1,curve2,target30.5C,DHW52C,boost0; controllersIDLE,error0,saved0,lease0. VP1 resumed nativeDHW priority. No active trial remains. Final firmware: D1c7a0fbcb, D206e8dea7.

### Resolution and communication

Only new completed generations count as new A3 samples. A3/16:77 in-trial completions,generations6..82,median interval18.21s,range12.18..24.62s. A3/17:76,generations6..81,median17.09s,range12.19..23.73s. Previous ordinary six-code trial median~44s per channel: approximately2.4–2.6x denser. Interval estimates use host midpoint minus integer completion age, not physical acquisition time. Service channels remain asynchronous. Last wire pending status does not invalidate a retained successful raw sample. No missing completion generations.

CN105 GET04 replies32->225; parser/UART errors0,handshakes1unchanged. Service accepted responses183->1300,failures0,exhausted0. HOLD nativeSET ACKcount stays2; lease renewals do not rewrite the target. Thus the steps were produced under a constant verified60C target. Background brine now refreshes roughly140–150s, can expire its60s TTL, and must not be treated as continuously fresh; graph explicitly contains these gaps. This priority is limited to ACTIVE fixed-flow6000 and exits in AUTO; it is not the normal EFFECT sampling policy.

### Observed steps (first host observation, seconds after test request)

| A3/17 target | First seen s | A3/16 same value first seen s |
|---:|---:|---:|
|35|292.4|318.8|
|42|364.4|376.8|
|52|489.9|498.1|
|62|539.2|556.0|
|84|611.7|624.7|
|85|670.1|661.9|
|95|903.9|920.1|
|97|962.3|970.4|
|99|1087.0|1103.2|
|101|1145.2|1153.7|
|103|1221.2|1213.1|

A3/16 also exposed27 at309.2s and63 at603.5s. Reversed observation order for85/103 illustrates asynchronous query scheduling: these columns cannot be subtracted to claim physical motor lag. A3/17 first-observed increments after35: +7,+10,+10,+22,+1,+10,+2,+2,+2,+2. They are differences between samples, not proof every increment is one internal decision; intermediate targets shorter than~24s could be missed.

The target62 was already observed while GET04 remained52; GET04 then passed54 before62. Target52 was observed while GET04=44; target84 while GET04=64. This supports the interpretation that some earlier GET04 +2/+8 splits are transition/caching observations on the way to an already higher target, not proof of separate +2 and+8 controller decisions. A3actual63 and target84->85 show resolution below GET04's2Hz encoding. Conversely95->97->99->101->103 also exists in target telemetry, so not every observed2Hz sequence is merely GET04 quantization.

Target42 persisted between first-observed changes for125.5s,85 for233.8s,97 for124.7s. Later99->101 took58.2s;101->10376.0s (query-phase uncertainty). A conditional/minute-scale progression remains plausible; unconditional +2 each minute or a universal fixed10Hz staircase is not demonstrated. Unlike previous run's91->85->91, this run had no sampled decline, only a long85 plateau. Do not equate that plateau with a proved protection flag. The target95 change occurs about10min after the observed compressor start, useful for a startup-timer hypothesis, not proof of its cause or exact phase.

Evidence in outer workspace:P0080/effect-learning/update-frequency-dense-vp2-20261012T120656Z and frequency-dense-vp2-20261012T120957Z. Raw events SHA256:4e97b883de04d243451578fc54d256477fe4b60cd568831ff3b03e08f42d2a10. Derived frequency.csv,frequency-analysis.json,dense-summary.json,PNG/SVG and restoration/outcome retained alongside raw RPC traffic. PNG visually checked; brine gaps preserved. Reusable asynchronous-sampling and intermediate-step lesson promoted to procon-async-mapping knowhow; function catalog updated.


### 2026-10-12 — offline synthesis: one-minute grid is compatible with dense target transitions

User requested a deeper synthesis; no live device calls or firmware changes. Dense trial A3/17 target changes after the initial35 can ALL be placed on one60s grid using observation intervals from last old successful completion to first new completion. For targets42,52,62,84,85,95,97,99,101,103 choose tick indices1,3,4,5,6,10,11,13,14,15. Their interval intersection allows a common phase296.481..299.153s after the fixed60 request; phase298 gives edges358,478,538,598,658,898,958,1078,1138,1198s, each within its corresponding interval. Thus first-seen spacings125/234/125s are compatible with2/4/2 cycles plus sampling uncertainty. The prior statement that unconditional one-minute increments are not established still holds; it should not be read as rejecting a conditional one-minute evaluation clock.

This is a fitted timing hypothesis, not recovered source code or proof of physical event times. Tick indices were assigned after observation; completion time is not acquisition time, unknown peer caching/job latency can shift the phase, and the initial0->35 start is outside this grid. The simpler current working model is one approximately minute-paced evaluation with state-dependent eligibility and increment/clamping, followed by actual-Hz slew and coarse status reporting. Two independent additive10Hz/2Hz clocks are not required by current evidence, but are not excluded.

Second lag: while actualA3=85, early665..725s modeled water power mean8.956kW grew to10.494kW at840..900s. Reported flow stayed19l/min; supply mean38.03->40.18C and return31.27->32.25C. These are uncalibrated,0.5C-quantized water-side estimates, not exact power measurements. They demonstrate continued thermal response under flat reported frequency, not a causal partition among heat-exchanger storage, refrigerant conditions and sensor delay. A Hz-to-W proportionality alone is insufficient during transitions.

Current effect.c forecasts from GET04-based history and bounded decaying response_lead; it does not consumeA3/17. Dense findings motivate observing already-requested Hz plus a thermal settling estimate and elapsed plateau/start phase, rather than interpreting flatGET04 as equilibrium. Do not assume A3/17 captures demand blocked by native constraints: equalactual/target still permits a later target step. The missing identification is target-Hz response to a controlled reduction of positive supply-temperature error, including the no-stop equilibrium band. No further maximum-demand run alone can identify that braking map.

Timing qualification: with the same assigned tick indices, periods approximately59.701..60.636s also fit the reply intervals. A minute-paced publication/transfer of target telemetry is an alternative to a regulator evaluation clock; current data does not localize the clock. Unchanged target at a tick does not prove evaluation was skipped.


### Operator hypothesis: coarse/fine tracking of a moving Hz reference

Operator proposes a delta-dependent linear Hz trajectory followed by coarse +/-10Hz and faster +/-1Hz corrections; opposing corrections could yield net8Hz and a changed reference could cause the observed dip through timing order. Retain as a hypothesis, not a firmware finding. Actual target steps near10 and1–2 are observed; faster opposing1Hz corrections and an explicit planned future trajectory are not. Previous A3target91->85->91 proves a target reduction, but all three first target observations had reported flow40C/target60C, so a sudden delta decrease at the event is not resolved (sub-degree or unsampled changes remain possible). Same VP2 also held85 for~234s in the dense trial before rising95 with no sampled dip, making a temporary state-dependent limit an alternative. The repeated85 is a clue, not an identified limiter.

A receding planned trajectory and a delta-dependent per-tick increment can produce indistinguishable ramps here. Recomputing a trajectory anchored at startup can lower its current reference when delta falls; merely reducing the slope of a continuously anchored trajectory does not itself move the reference downward, although coarse tracking can overshoot. A dip alone is not proof of a software bug. A controlled decrease of still-positive temperature error at two phases of the apparent minute cadence, with prioritized targetA3/17 and primary-temperature monitoring, would test faster opposed corrections and timing sensitivity. Sampling/publication cadence must still be distinguished from internal decision cadence. No new physical trial or code change performed.


## 2026-10-12 — focused A3/17 cadence preparation
User asked for more A3/17 per minute. Current paired-priority schedule gives17~40% of operations. Diagnostic mailbox previously forced an extra ordinary A3 job between successive host diagnostics. Common's queued-admission now also accepts serviceREADY after completeFAST; no preemption of activeA3, no retry/cadence/lease/control changes. Existing diagnosticIDLE-only restriction remains, so the initial live qualification is curve-mode reads, not a new heating experiment. No persistent sampling profile.

Candidate composite86d693a9 changes Common only fromD206e8dea7. Common4304/12288B (+16); allotherchunks/BL2 unchanged. Full hostASan/UBSan suite and actual final ARM execution passed, including queued boundary, partialFAST, activeA3pending/timeout, existingcontrol/application/restore/ABI tests. Newtestcases in existing test_raw_diagnostic.c and test_modules_arm.py. No newtrackedpaths, indexunchangedforcontinuation. No commit/push. Outerworkspace updater and finite180s probe captureRPC/evidence, enforce pending format0/checksum before completion, drain and verify full ordinaryqueue recovery.


## 2026-10-12 — focused A3/17 cadence physically qualified

VP2 completed 24 separate diagnostic17 jobs in a 180-second window, all with
checksum-valid BUSY/format0 → DONE/format2. All raw results were20Hz. Mean observed
completion spacing7.583s, median7.471s, range5.011–11.767s, equivalent7.912jobs/min.
This is about2.4times the preceding paired-frequency trial's approximately3.3/min.
These are distinct FTC job cycles; they do not establish underboard acquisition
age or the native target-publication rate. The longest gap includes an already
started ordinary service job. Host polling delay also contributes to intervals.

Normal GET04/temperature generations continued advancing; maximum observed age
6.957s/7.411s respectively. Supply31.0–31.5C, return29.5C, frequency20Hz. There were
no new parser/UART/handshake or service failure/exhaustion counts. After stopping
submissions, six ordinary service cycles completed (16→22) and brine/pump data
became valid again. Both pumps retained power1, curve2, target3050, DHW5200, boost0,
with controller state/saved/error0. No heating-control writes in this test.

Initial Common-only86d693a9 installation succeeded, but the first mailbox read
failed because preserved D2 Dispatcher584B predates P0081. No diagnostic was
submitted in that failed probe. Corrected5fc25d43 installs existing Dispatcher672B
in a separate Dispatcher-only OTA, preserving all other installed chunks/BL2.
Actual ARM test now traverses BL2/Dispatcher/Common read600/616 and write600,
checks raw response and rejects diagnostic envelopes at control300. Corrected
composite passes; original composite fails specifically with Modbus exception2.
VP2 installed5fc25d43; VP1 unchangedc7a0fbcb; Shelly restored mb_client9600/8N1.

Qualification is IDLE/curve-only because the diagnostic mailbox intentionally
blocks admission during active control. Active fixed60 still uses the prior
Service schedule16,17,16,17,B; EFFECT is unchanged. A future target-focused control
trial should prioritize17 within Service, preserving control/lease/restore
admission, rather than relaxing diagnosticIDLE. No such additional change or
heating experiment was performed here.

Evidence (outer workspace):
`P0080/effect-learning/frequency-target-probe-20261012T135306Z/` contains report,
24 completion rows,291 mailbox observations,rawRPCs and result.json.
Events SHA256 `4dec994c04ef4b893302b2071512aac0ba553dd9ecfd0a3889d778c1a4d92b99`.
OTA evidence `update-frequency-target-vp2-20261012T135033Z/`; earlierCommonOTA
`update-frequency-target-vp2-20261012T133647Z/`; rejectedread evidence
`frequency-target-probe-20261012T134023Z/`. Full hostASan/UBSan and actualARM
controller/restore/ABI regressions passed. Independent raw-log audit agreed with
all24 pending/completion chains and final recovery. No commit/push this turn.


## 2026-10-12 — fixed60 with eight A3/17 replies per minute

User-authorized VP2 trial completed: Service-only OTA from5fc25d43 to33143fde;
VP1c7a0fbcb and every other installed VP2 slot/BL2 unchanged. Service1472/4096B.
ACTIVE fixed-flow/applied6000 selects17 at each service-operation boundary.
Full eight-query FAST rounds, exclusive1s retries/max10 and normal TTL remain.
Ordinary27/28/18/19/16/17 cursor is preserved and resumed after exit. Diagnostic
IDLE gate, control/lease/restore and EFFECT are unchanged. Target-only sampling
pauses A3/16/brine; their validity expires honestly rather than faking freshness.

Before transfer: full Makefile.baseline host-test ASan/UBSan suite passed, as did
actual ARM tests of final build-frequency-focus-vp2. Tests cover eight successive
focused jobs with six attempts and complete FAST separation, strict profile
gates, in-flight exit, retry exhaustion and ordinary-cursor recovery. Integrated
fixed60/controller/AUTO paths and existing public Modbus600/616/300 arbitration,
ABI/corrupt-slot and control regressions pass. Source changes are service.c plus
existing test_telemetry.c/test_cn105.c/test_modules_arm.py. No new tracked paths;
existing unrelated dirty work is preserved, repository index unchanged.

VP1 OFF; VP2 already20Hz at entry, verified60C for1169.973s. Automatic stop after
high plateau182.951s with25 fresh target generations: A3/17=103,GET04=104Hz.
Total experiment1185.477s including entry. Max measured supply45.5C;50C and30min
limits not reached. Both restored power1/curve2/flow3050/DHW5200/boost0, with
state/error/saved/touched/lease0. No in-trial parser/UART/service failures or
reconnects. Primary telemetry maxage8.399s.211 hold captures retain nativeACK2
and readbacks6 despite lease renewals, excluding repeated nativeSET as cause of
the observed minute rhythm.

161 coherent completion events, no generation gaps within that series; observed
mean7.252s/median6.434s,8.274perminute,range4.447..11.532s. Every full minute after
verified setpoint contains8or9 completions. A final full capture sees one more
completion after the last focused poll; it is not counted in the161 analyzed
events. Strict simultaneous pending/wire matching was not captured for4 events
(84/118/141/162); raw status0 on the prior generation and multiple accepted
responses establish additional pending evidence, without claiming coherent full
pending chains for those cases.

Target sequence20,30,40,51,61,84,85,91,92,93,95,97,99,101,102,103. All15 transitions
fit one60s observation grid; first8 phase-fit predicts the later7 without refit.
Whole-run sensitivity55..65s in0.05s steps admits tested periods59.90..60.30s.
Both1/2Hz and larger steps share that rhythm; no observed negative/off-grid
small steps. This constrains reported target publication, not proven internal
regulator/acquisition timing. Hidden faster opposed changes remain possible.
GET04 sometimes passes intermediate values toward an already larger A3 target
(e.g. target40 whileGET0430->32->40), so a coarse+2/+8 split need not mean two
opposed controllers. Net61->84 within~8s is not proof of one+23 internal decision.
Supply dipped~38->36.5C nearminute7 while target85->91, without an observedtarget
reduction; A3actual/brine were not sampled and cannot identify its physical cause.

Initial post-restore check raised because first ordinaryA3/27 exhausted pending
budget; controls had already restored. Do not call cycles205->211 six successful
reads. Separate read-only follow-up verified six more cycles222->228 withfailure0
and exhausted1 unchanged, normalbrine/pump validity and exact original settings.
Outcome records both the initial check failure and successful follow-up. No
additional heating command or altered retry budget was used to obtain recovery.

Evidence outerworkspace: frequency-focus-vp2-20261012T142017Z (report, rawRPC,
events, originals, restoration/recovery/outcome, timingJSON/Markdown, PNG/SVG).
OTA update-frequency-focus-vp2-20261012T141452Z. Runners/analyzer/plot beside them.
EventsSHA256841d74a58d9e9f3f6363e4e442a85804ccb85514e5c180911fc9c5223866b619.
RPCSHA256ec5480ee0f29965c7dded39f07695900a7222d0cc20663fbdded9b929541dea8.
Independent disk audit confirms cadence/grid/restoration. No commit/push.


## 2026-10-12 — moving-delta experiment installed, physical series in progress

User requests actual+5/+10/+15/+20C, start~30C, stop45C, minimum15minOFF
betweenruns and waitlonger to~30C ifneeded. VP1rested. TemporaryVP2d3cbb1d2
installed from33143fde viaMode+Serviceonly; BL2/otherchunks byteidentical.
Mode12264/12288B, Service1464/4096B. Manual65C readback/command/encoder bounds
are consistent; DHW60/EFFECT55 unchanged. Servicefocus ACTIVEfixed-flow/OFF.
FullASan/UBSan/Pythonhostsuite andactualfinalARMcomposite pass, including
midA3retarget/arbitration,6500/6501,originalpreservation,lease/AUTOrestore,
profilegates andnormalresume. Hostrunner fixturespass: pending/duplicate-source
write suppression,45Cstop-before-write,earlyentrylimit,no falseappliedevent,
900sverified-OFFpause andfailedretarget invokesfinallyrestore. Analyzer synthetic
full/partial/gap/no-change/context tests pass. No newtrackedpaths,indexunchanged.

OTA evidence outerworkspaceupdate-delta-sweep-vp2-20261012T153914Z. Verified
bothoriginalcurve settings andnative9600/8N1afterOTA; VP1c7a0fbcbunchanged.
Activeexperimentouterworkspace delta-sweep-vp2-20261012T154311Z. Firstseries
entered atactual30.0,target35.0 afterOFF, Hz0nativepause retained. Continuous
retargeting logs sourcegeneration/age,request/nativeapplieddelta andA3completion
intervals. Primarymonitoring<20s; noA3completionfor60s endsinrestore, whileone
exhaustedcycle alone doesnot abortifrecentcompleteddataremain. No minute-paced
SETschedule. Series60minbound/cooling90minbound giveexplicitpartial evidence
ifendpointcannotbereached. Physicalresults/normal-profile-restoration pending.


## 2026-10-12 — all four moving-delta series completed

VP2 actual+5/+10/+15/+20C each reached45C. Applied-to-stop durations
2363.144/1594.363/1546.710/1282.298s; A3/17 completions280/190/192/160,
7.109/7.150/7.448/7.487 per minute, no missing completion generations.
Seven/four/zero/zero84->70 reversals. +15 sequence0,48,58,68,84,85,95,98,101,102,103;
+20 sequence0,48,58,68,84,85,95,103. All start with first positive48 after
273/277/282/274s and approximately3min at48; +15/+20 both hold85 about4min.
All9/6 positive-running transitions in +15/+20 fit a60s publication grid.
+10 retains one independently audited off-grid84->70; do not claim a universal
exact timer or infer two internal clocks. GET04 is not exact target telemetry.

Initial segment delta-sweep-vp2-20261012T154311Z completed only series1 and
restored before series2 when nativeDHW selected. Explicit resume chain
links delta-sweep-vp2-20261012T164844Z; it waited out DHW and repeated full
verifiedOFF/cooling intervals. A second DHW deferral before series3 likewise
sent no heating target and required a fresh15minOFF interval. VP1 heldOFF;
all heating starts waited at least15minOFF and supply<=30.5C. Circulation
subsequently lowered actual readings to28/27.5/27/29C, so starts are not
thermally identical. Actual stop45C was checked before further increases.
Maximum native readback in +20 was64.5C;65C remained an offline boundary test.
Both original power1/curve2/DHW5200/boost0 verified restored19:40:31UTC,
controlIDLE/saved0/error0 and no lease. Prior-profile OTA recovery is recorded
separately below; do not equate control restoration with firmware restoration.

Prospectively locked integral-exit models failed on series3/4: from application
159.6–162.8/210.5–213.0Cmin versus180–200 band; from first positiveA3
88.9–92.1/118.9–121.5 versus150–165 band. Not evidence against all integral
control, but no single tested degree-minute threshold explains84-band exit.
Exploratory+4Hz prediction at+20 received no support:95->103 directly reached
the observed ceiling, with no unsaturated upper fine-step sequence. A clipped
+10 is possible, not proven. Keep initial predictions alongside outcomes.

Separate nativeDHW18:00:43–18:18:51UTC (AUTO/IDLE, no VP2commands) also
showed84->70, then65,59,54,49,44. Host moving-temperature SETs therefore
not necessary for that reduction; same cause for heating reversals unproven.
Normal servicequeue supplied fresh brine3/1C near it, but acquisition times
and coarse resolution do not establish a sudden brine-triggered protection.

Offline tools: analyze_delta_sweep.py --chain, evaluate_delta_hypotheses.py,
analyze_native_dhw_side.py, plot_delta_comparison.py. Synthetic fixtures passed;
final Swedish plot visually inspected. Full local report/evidence in resumed
segment, raw first-series provenance retained. Findings promoted to existing
async mapping knowhow. No commit/push; unrelated existing dirty work preserved.


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


### Correction: first-series pause versus between-series pauses

The old four-run script used cool(0) before series1; its pause_verified and
cooling_complete timestamps were15:44:15UTC with minimum_seconds0 and
verified off interval0.000246s. It did NOT enforce15min before that first
series. The required >=15min intervals between subsequent series were enforced.
Earlier wording saying all starts had a verified15min pause was too broad.
The first-series actual prior stopped duration is not established by this event.
Do not infer a20min restart lockout from all four startup delays. A separate
startup preparation delay remains possible. The new nondecreasing+10 trial
explicitly enforces900s before its only series. No timing threshold is changed
to test restart hypotheses in this run.


## Authorized nondecreasing +10 comparison — in progress

User explicitly requests repeated+10 without downward target changes. One
VP2 mission reuses delta-sweep Mode+Service d3cbb1d2 for equal A3/17 cadence.
VP1c7a0fbcb unchanged. Temporary profile installed and originals/native transport
verified; outer update-delta-sweep-vp2-20261012T202746Z. Live mission:
monotone-delta10-vp2-20261012T203853Z, host session62693. Originals newly read:
power1/curve2/target3100/DHW5200/boost0; do not restore older3050 as fixed target.
Only host target rule changes: max(previous accepted target, actual+1000cC).
Separate command boundary rejects any decreasing heating target; AUTO restore
remains allowed at exit. Stopactual45C, max60min, startsupply<=30.5C and full
900s verifiedOFF before sole run. NativeDHW priority and ownership guards retained.
Base runner adds an overridable target method with unchanged default behavior;
base fixtures and real stage-loop monotone fixtures passed. Sources frozen and
hashed in evidence. No new EFFECT code, no bus-parallel worker, no commit/push.
Physical result, both restoration and prior-profile OTA remain pending.


User clarification supersedes initial900s pause: pause was intended for cooling
between runs, not mandatory before the only new run. First setup203853Z was
stopped before any heating stage; both originals verified restored. Host now
uses cool(0): verifyOFF and supply<=30.5C, no forced15min waiting. Monotone
rule and45Cstop unchanged; fixture suite passed again after this change.


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

## Completed two-loop deployment and trial — 2026-10-13

Both devices installed and read-back verified: D1 `5903105e`, D2 `f3ed161c`; latest OTA changed Mode only, BL2 preserved. Mode11936/12288bytes, RAM1304/4096bytes. Host ASan/UBSan and both composed ARM suites passed.

Final VP1 trial, VP2 OFF:15min6000W then15min5000W. At6kW, last5min mean6086W (5643–6448W),90% reached3.26min from logged activation including45.82s qualification wait. At5kW, last5min mean6273W (6270–6313W): downward tracking FAILED. The positive demand floor prevented further braking near actual temperature; no protocol failure has been proven. Model offset updated10times to-761W, slope stayed135W/Hz. Maximum actual supply37C; no zero-Hz samples during qualified stages. Thermal-boundary operation was not exercised by this live test.

Both restored and verified power1/mode2, curve target30C, DHW52C, boost0; controller IDLE, saved0, lease0, error0. No active trial remains. See `effect-two-loop-report-2026-10-13.md` and `evidence/effect-two-loop-20261013/final/` for raw events, plot and restoration. Earlier entries are historical checkpoints. No commit or push in this task.

## Brake-boundary live experiment — 2026-10-13

VP1 manual, VP2 OFF.−1C yielded41→32Hz in about4min without pause;−1..−1.5C reached20Hz while running. At actual33C/target31C (−2C),20→0Hz was observed; both restored and verified curve/IDLE/lease0. This brackets a single observed low-frequency stop transition, not a universal guaranteed threshold. No firmware change. See `brake-boundary-report-2026-10-13.md` and its complete provenance, including corrected harness state2 handling and controlled handoff.

## Dual quarter trial completed — 2026-10-14

Both Mode-only OTA installations verified (0f48da4e/a5a6dc0c);60-minute2/4/6/4kW-per-unit mission completed and both curve restorations verified. Physical tracking PARTIAL: final5min VP1/VP2:2kW→3.06/3.13;4kW→3.99/3.75;6kW→4.38/5.07;4kW-down→3.85/4.19. No observed compressor stop after initial native pause/restart. Thermal latch blocks ordinary power correction and needs redesign; upward slew remains slow;25Hz release limits2kW. See dual-quarters-report-2026-10-14.md, evidence/dual-quarters-20261014, and release-effect-braking-20261014. Source/tests pass, no commit/push.

Repository index: preserved prior working-tree edits. No tracked paths were added/removed/moved in this uncommitted follow-up; new evidence/release/knowhow paths remain untracked pending a requested repository sync. Existing function and memory indexes updated. Git diff whitespace check PASS. Release and evidence SHA256 verification PASS; final restoration assertions PASS.

##45C policy candidate —2026-10-14

User replaces actual40C priority with45C, retaining requested55C. Named compile-time policy with derived approach/release/pause margins. Build12048/12288; Mode-only composed manifests180b7f30/b2e57972. Full historical host regressions explicitly at40C plus production-default45C boundary suite PASS. No live changes in this follow-up; installed40C firmware unchanged. Existing thermal-latch weakness remains documented, not silently treated as fixed. Release `procon/modular/release-effect45-20261014`.

## 2026-10-14: continuous envelope / faster upward response (offline candidate)
Actual supply regulation priority is45C, requested-flow ceiling55C. The current thermal forecast and actuator ceiling replace the90s cooling latch; no cooling-to43C prerequisite remains. The Hz controller continues underneath the thermal envelope, including negative power correction. Positive goal trim is inhibited when constrained; negative correction is allowed. Temperature priority still overrides the power goal and does not commandOFF.

After independent fresh A3/17 feedback, upward slew is at most2C/decision when more than10Hz short,1C when more than6Hz short, otherwise0.5C. Decisions remain at least30s apart; this is a ceiling, not a compulsory boost. Initial demand selection and unchanged-target90s nudge remain. Downward slew remains0.5C per60s. Ordinary braking can reach actual-0.5C/-1C above20Hz; it releases at20Hz or early below24Hz when the observed target is falling. This replaces the fixed25Hz guard.20Hz is an observed operating point, not a universal minimum guarantee.

ABI,12KiB Mode slot, leases, restoration, telemetry freshness and native protections are unchanged. Only Mode is included in device-specific OTA compositions. Synthetic tests establish software behavior, not physical stability or6kW capacity. No installation or live test has been performed for this candidate. Next physical qualification should compare upward4→6kW and downward6→4kW response, temperature priority and low-load pause behavior.
## 2026-10-14 — dual six-quarter live qualification

- Installed Mode-only continuous-envelope firmware on VP1/VP2 (`9580f1d1` /
  `3f6ef793`) and ran 2, 4, 6, 4, 2, 6 kW per pump for 15 minutes each.
- Verified restoration to heat curve mode on both devices.
- Demonstrated non-linear, device-dependent ramps; neither +2 kW nor -1 kW per
  2.5 minutes is a safe planning assumption.
- No actual supply sample exceeded 43.0 C; requested supply reached 47.5 C and
  no thermal-limited sample occurred.
- Added `dual-six-quarters-report-2026-10-14.md` and retained raw evidence,
  summary and plots under the trial directory.

## 2026-10-14 — Shelly pair-energy executor

- Added the scalar, array-free Shelly planner/executor for the pair plan
  `1.5/2/2.5/4/2.5/2/1.5 kWh` per quarter. Only the Modbus RPC's required
  transient word payloads and returned register values use protocol arrays.
- The first field attempt was stopped and restored after proving that its debt
  reset at each boundary. The corrected implementation uses cumulative target
  energy and completed the full 105-minute run.
- Delivered 16.981 kWh against 16.000 kWh (+0.981 kWh, +6.13%). After four
  quarters it was 9.973 kWh against 10.000 kWh, demonstrating useful cumulative
  recovery. Downward physical response at the 3+3 kW command floor caused the
  final surplus.
- Fixed the final-quarter display calculation after the field run; total energy
  and live control were unaffected. The corrected 7,484-byte source is installed
  byte-identically in Script 7, stopped and disabled.
- Both devices were verified restored to power on, heat-curve mode, DHW 52 C,
  boost off, controller IDLE and no saved ownership. See
  `shelly-energy-report-2026-10-14.md` and `evidence/shelly-energy-20261014/`.
- Policy clarification after the field result: retain both running pumps at the
  3+3kW pair floor and report surplus instead of stopping one for exact tracking.
  Single-pump operation has about1C lower observed brine temperature and worse
  COP; L4 compensates any resulting house-energy/temperature error later.
- Added scalar four-quarter MPC candidate. It evaluates6--24kW in0.5kW steps,
  holds each candidate for five simulated minutes and uses the field-fitted
  330s startup /30W/s up /3W/s down pair model. Counterfactual replay predicts
  +10Wh final error versus+1407Wh for the old controller; this is not yet a
  physical result. Backtest provenance is
  `evidence/shelly-energy-20261014/mpc-backtest.json`.

## 2026-10-14 — combined EFFECT and energy 1.4.1 offline candidate

- The EFFECT affine model moved from the full Mode chunk into Service. Mode
  calls it through private veneers at `0x08012069` and `0x0801206d`; the public
  slot layout/ABI remains `3833993797`. Mode and Service are therefore one
  inseparable update. They must be staged and committed together.
- Final sizes are Mode 11,928/12,288 bytes and Service 2,728/4,096 bytes. The
  device-specific compositions preserve BL2 and every other installed chunk:
  VP1 `9580f1d1` -> `4bf657aa`, VP2 `3f6ef793` -> `e11851e8`; OTA changes only
  Mode and Service (OTA slot indices 2 and 4).
- EFFECT accepts qualified source data up to, but not including, 60 seconds
  old. Data below 15 seconds may use the faster response law; data aged
  15--59 seconds continues bounded best-effort control and cannot authorize an
  aggressive increase. A real minimum-output state, requested-temperature-cap
  state and stale-source state now survive into phase/reason diagnostics.
- The physical actual-supply priority remains 45 C and is separate from the
  requested-flow cap (up to 55 C). Thermal braking may reduce at most 1 C per
  30 seconds; ordinary downward control remains gentler. Cooling restores
  thermal headroom without a sticky latch, and a requested cap can never be
  raised by the compressor-preserving demand floor.
- Shelly executor 1.4.1 is constant-time and array-free. It controls the
  current and following cumulative-energy deadlines, applies conservative
  response-lag/ramp/capability bounds, observes 120-second normal target dwell,
  and sends an exact floor/ceil split whose per-device targets sum to the pair
  request. Limiter feedback redistributes work within fresh per-device caps and
  reports unreachable energy instead of winding up.
- Missing or >=60-second feedback no longer becomes an invented 0 W sample.
  The affected interval is counted as unknown, the accepted target and last
  limiter state are held, and an established target is renewed before its
  180-second lease expires. The first complete fresh pair replans immediately;
  normal integration resumes only on the following fresh interval.
- The runtime controller is deliberately current+next deadline control, not
  the full four-quarter grid MPC explored offline. Host sanitizer tests, both
  device ARM compositions, FC04 321--336 mailbox tests and mock OTA tests pass.
  No installation or physical qualification has been performed for this
  combined candidate.
- Frozen release: `procon/modular/release-effect-energy-v2-20261014/`. It
  contains both device-specific compositions, source, Shelly 1.4.1, 128 checked
  file hashes and machine-readable composition/verification records. Final
  gates passed: 41 energy tests, 37 full ARM cases, both public device-image ARM
  paths, flash-RAM guards and 2,065 mock-OTA mutation cuts per device.

## 2026-10-15 — EFFECT + energy 1.4.1 live qualification

- Completed the full seven-quarter plan. Accounted valid energy was 15,511 Wh
  against 16,000 Wh, with 2,610 s deliberately marked unknown rather than
  treating unavailable device feedback as zero production.
- VP2 entered native DHW priority across most of quarters 4 and 5. The session
  held ownership and resumed automatically when fresh heating feedback returned.
- Cumulative recovery worked, but quarter 7 exposed two defects: the fixed
  five-minute committed-energy forecast overestimated future output during
  active down-commanding, and VP1's thermal down-regulation continued into a
  native zero-Hz pause.
- Both pumps were restored to heat curve and controller IDLE. A separate
  postflight verified Script 7 stopped/disabled, Modbus 9600 8N1 and both relay
  outputs off. See `effect-energy-v2-live-report-2026-10-15.md` and
  `evidence/effect-energy-v2-live-20261015T033119Z/`.

## 2026-10-15 — EFFECT + energy 1.4.2 offline v3 candidate

- Corrected the native-pause path exposed by the v2 field run. WAIT_NATIVE now
  retains a bounded restart-safe request up to 44.5 C and no longer reuses the
  old 39.5 C degraded-feedback fallback. Snapshot, ownership, lease and normal
  restoration semantics remain active.
- Energy executor 1.4.2 replaces constant-peak lag credit with a trapezoidal
  projection toward the accepted command, treats thermal limitation as no
  guaranteed end power, and permits one bounded +1 kW collapse-recovery step
  followed by a 120-second cooldown.
- Composed a Mode-only update over installed v2: VP1 `4bf657aa` -> `d23f69c6`
  and VP2 `e11851e8` -> `78d16f84`, OTA slot 2 only. Service remains
  byte-identical at SHA-256 `c271160d402f8b6f43483d5834045fafe391854cf1dcc444bb561ef591b20b18`.
- Frozen offline package: `procon/modular/release-effect-energy-v3-20261015/`.
  It contains complete device images, Shelly 1.4.2, both Node regressions,
  Mode-only composer, exact source archive and machine-readable composition.
  No v3 installation or physical qualification is claimed.
