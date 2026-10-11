# P0080 implementation continuation

Status: implementation and offline verification complete; hardware qualification pending.

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
