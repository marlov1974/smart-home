# P0080 implementation continuation — offline verified candidate

Direct user mandate extends the original feasibility package to a real modular EFFECT/OTA build. No live actions, commit or push in this run. Baseline: locally latest P76 pause-r2 source, pinned in procon/modular/baseline.json; G2 upstream still held older P72 portable firmware at start. Implementation is isolated under procon/modular.

## Measured partition

| Chunk | Base | Reserved B | Built B incl header/veneers | Free B | RAM data+bss B |
|---|---|---:|---:|---:|---:|
| bl2 | 0x08008000 | 8192 | 6624 | 1568 | 856 |
| common | 0x0800A000 | 12288 | 2704 | 9584 | 152 |
| dispatcher | 0x0800D000 | 4096 | 568 | 3528 | 8 |
| mode | 0x0800E000 | 12288 | 9648 | 2640 | 840 |
| drift | 0x08011000 | 4096 | 2456 | 1640 | 360 |
| service | 0x08012000 | 4096 | 1336 | 2760 | 104 |
| debug_command | 0x08013000 | 4096 | 72 | 4024 | 0 |
| debug_telemetry | 0x08014000 | 4096 | 208 | 3888 | 0 |

Manifest adds2048 B. Total reservation54KiB inside the96KiB application footprint. All proposed flash budgets fit without shrinking or replacing real EFFECT functionality. Main stack reservation2304 B, static RAM slots14080 B. Per-slot bounds are enforced by linker; stack reservation is not a measured worst-case stack proof.

Common contains the actual CN105 arbiter; service chunk retains real A3 state/timing, and drift chunk its cache. Debug-command is the existing supervised-envelope adapter (72 B), not an unrestricted RAW implementation. Debug-telemetry contains extracted P76 feedback diagnostics. Low usage is explicitly not claimed to represent features the baseline never had.

## Delivered

Eight independently linked images, stable branch veneers, checked headers and fixed RAM ownership; BL2 validates all modules before initializing/running them. Resident identity/status and repair remain without modules. OTA handles FF/FE system handover, WAIT,115200 transfers, packet CRC, targetUID, old image CRC, selected-slot erase/write, duplicates and final complete-set commit. Original bootloader/BL2 and option bytes excluded from OTA writes.

Mac/Shelly CLI has offline-default plan, explicit live inventory, native handoff gate, staged bounded frames, retries of exact timed-out frames, peerWAIT ordering, UID checks and post-reset image verification. Max252 wire bytes:232 firmware bytes plus8 payload addressing bytes and12 framing bytes. Per-slot update sends its padded reservation, not only used bytes. Initial installation uses the established vendor update path and its full96KiB erase contract.

## Verification

- Eight native P76 suites with ASan/UBSan, including integrated10-minute compressor pauses.
- Existing Python command/telemetry/commissioning tests.
- Full37-case actual ARM image regression: preserved EFFECT/AUTO, service arbitration, addressing, UART behavior.
- Actual ELF module initialization, every export veneer, native maintenance gates, FF/FE response and baud transition, invalid chunk rejection.
- Actual ELF RAM flash writer: RDP1, blocked contexts, bounds, program/erase failures and stuck-busy reset, no option/mass writes.
- Real OTA C with mock flash,523 mutation cuts including manifest doublewords, duplicates, incorrect identity/base, malformed requests and bad image commit.
- Full-set repair and host→fakeShellyRPC→actualOTA C, lostACK retry and duplicateUID refusal.
- Independent service implementation moved32 B: only service image changed; all other chunks byte-identical.

See build logs and verification artifacts; simulation timing is not real hardware timing. The legacy ARM timing model excludes boot checksum time from request scheduling to test application behavior after boot.

## Hardware limits / next handoff

No complete modular image or OTA transfer has been tried on the physical unit yet. First install BL2+all chunks through the known physicalDIP method, confirm native curve/DHW state, then exercise a single-chunk update on one isolated unit. Only after that qualify two-unitWAIT/baud/silence. Native reset restoration remains P76's existing limitation. FlashECC after a torn physical write may require originalbootloader/DIP recovery; no A/B or guaranteed power-loss recovery. CRC is not firmware authentication.

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


## Hz-leading host pilot and autonomous candidate982e160b — 2026-10-10

The operator authorized an hour of analysis, controller changes and physical experiments towards rapid, smooth6kW tracking. Historical smooth-controller evidence showed that its guessed landing-temperature taper continued lowering demand after acceleration had faded or reversed. The first short-lease smooth trial also exposed renewal starvation during APPLY. Both issues are addressed in the new candidate.

A supervised host-controlled pilot ran against installed67ff1a3e, using direct fixed-flow target updates and a45C command ceiling. Evidence: `P0080/effect-learning/rocket-lead-20261010T141602Z`. The requested observation was900s; final samples were909/921s for VP1/VP2. Both were already running at the first observation, so no zero-power start is invented. No observed compressor restart occurred. This run included config/identification holds and used the older abrupt thermal clamp; it is not a fixed-policy autonomous firmware qualification.

|Host pilot metric|VP1|VP2|
|---|---:|---:|
|First observed90% of6kW|304s|393s|
|Last5min rolling power, mean|5.754kW|6.002kW|
|Last5min range|4.644–6.076kW|5.387–6.269kW|
|Last5min observations in5.5–6.5kW|10/13|12/13|
|Maximum actual supply|39C|38.5C|
|Final rolling power|4.644kW|6.172kW|

VP1's late power fall followed the old forced39.5C target ceiling. VP2's44.5→39.5C demand change was also logged at actual38.5C. This supports replacing the discontinuous thermal clamp, while leaving the precise plant dynamics uncertain. Raw sampled heat integration yielded1.095/1.173kWh over844/849s of covered intervals; these partial-coverage estimates must not be presented as complete quarter-hour energy. Temperature/flow quantization and rolling-mean lag remain material. Both restored and read back as power1, curve2, target3050, DHW5200, boost0, controlIDLE/saved0/error0. Helper cleanup verified.

Final candidate `build-effect-rocket`, prefixCRC982e160b, uses private35s Hz lead history and60s acceleration history to avoid confusing native10Hz steps with sustained acceleration. It begins at at most45C, then makes bounded corrections up to configured55C. The guessed landing-temperature taper is removed. Far-below-goal and recent falling/flat-Hz guards suppress inappropriate continued braking. Feedback15..59s old holds ordinary demand; hard-invalid guarded recovery remains. The continuous thermal ceiling is `3950+3*max(0,3950-Tlead10s)`, bounded by the command cap; actual39.5C or30s forecast40C retains a protective39.5C override. Mission/limit reporting remains active under thermal constraint. These gains are empirical.

Lease renewal now accepts a next-sequence equal-intent EFFECT request during an internal APPLY adjustment of an already-applied mission, preserving the pending transaction, readback and original restoration snapshot. Initial/unapplied and changed-intent requests remain BUSY. Exact retransmission never extends a lease. The host must attempt renewal in APPLY as well as ACTIVE.

Only mode changes from67ff1a3e; BL2/layout/ABI are unchanged. Mode11984/12288B, RAM984/4096B. Complete host ASan/UBSan tests, final-image ARM tests and1551 OTA mutation-cut tests passed, including quantized Hz-step behavior, falling/flat-Hz guards, gradual thermal limiting, ordinary aging holds, in-flight renewal/readback and restoration. Installation is in progress; native firmware physical verification is pending at this entry and will be recorded separately. No commit/push. Only existing tracked files changed; no index update required. Knowhow promotion intentionally deferred because controller gains and thermal response are package-specific empirical findings.


### Physical installation982e160b and restart-margin qualification
Both units were OTA-updated mode-only and verified by UID, prefixCRC982e160b, normal native curve readback, advancing CN105 replies and snapshot sequences. Evidence: `P0080/effect-learning/update-rocket-20261010T143423Z`. BL2 remained unchanged. A900s dual6000W native experiment started at14:47:06UTC, with both compressors in observed native pause; it is in progress at this entry.

Source/history review establishes that the0.5C native-pause demand margin is an empirical choice, not a proven FTC restart threshold. The algorithm only raises a target that is below supply+0.5C; it does not lower an existing target as water cools. Current pause retained30.5C while supply fell to29C. Earlier observed off-to-positive spans were about404/441s at30.5C targets with last clear paused supply27/27.5C, and227–300s at32–38C targets with much larger gaps. Sampling and unknown earlier stop times prevent identifying a precise timer or hysteresis. The simulated10-minute-pause test manually restarts the plant independently of target; it proves mission retention, not physical restart sufficiency.


## Autonomous 982e160b physical result — 2026-10-10

Both pumps completed the requested 900 s native 6000 W mission with 180 s leases renewed repeatedly. No control error, lease expiry, further stop after the observed restart, or 40 °C boundary violation was observed. The final paired loop completed at 911 s; its snapshots were captured at 876.85 s (D1) and 897.49 s (D2). All writes, replies, samples, plots and statistics are in `P0080/effect-learning/rocket-native6kw-20261010T144437Z`. The host monitored the run, renewed leases and restored settings; all temperature regulation during this experiment ran in Procon.

| Metric | VP1 | VP2 |
|---|---:|---:|
| First observed running, since confirmed mission | 326.4 s | 424.7 s |
| First observed 45 °C target, since mission | 447.1 s | 542.2 s |
| First 90% / first 95% of 6000 W, since mission | 683.4 s | 779.0 s |
| First 90% / first 95%, since first 45 °C target | 236.2 s | 236.8 s |
| Peak sampled short-mean heat power | 6.061 kW | 5.882 kW |
| Final sampled short-mean heat power | 5.774 kW | 5.446 kW |
| Last 3 min sampled short-mean power, mean | 5.604 kW | 5.498 kW |
| Last 3 min range | 5.507–5.774 kW | 5.015–5.882 kW |
| Last 5 min sampled short-mean power, mean | 5.455 kW | 4.705 kW |
| Maximum observed actual supply | 37.5 °C | 36 °C |

The requested near-exponential curve from mission start was NOT achieved. Native waiting consumed 5.4 / 7.1 minutes, then approximately 121 / 117 s elapsed before the first 45 °C demand. Startup settling retained 30.5 °C while the compressor initially increased and then reduced frequency; this exposes a distinct weakness in startup demand. After the higher demand was applied, both reached 95% within about four minutes and approached the target without the previous large, repeated demand drops. Late power remained roughly 5.5–6 kW, with an unresolved tendency to run below target. The short observation near the target does not prove long-run stability or 99% tracking. Different initial compressor and temperature states make comparison with the running-start host pilot descriptive, rather than controlled A/B evidence.

The last 3 min statistics use the fixed 720–900 s mission window, with four observations for VP1 and five for VP2. The progressive thermal ceiling was observed once on D1 as supply approached 37.5 °C; sustained capacity limiting near 40 °C was not exercised. It remains covered by unit and ARM tests plus this limited physical observation. The complete 15-minute mission survived with renewable 180 s leases and 24 acknowledged equal-intent renewals, but diagnostic captures immediately before renewal all showed ACTIVE. The newly permitted renewal branch during APPLY is therefore proven by host tests and was not separately isolated in this physical run.

Strict integration of raw snapshot heat power covers 876.85 / 897.49 s and estimates 0.66320 / 0.52678 kWh; missing tails were not silently filled. These are partial-coverage, uncalibrated water-side estimates. The user's illustrated exponential reference itself integrates to 1.30011 kWh per unit per quarter-hour, compared with 1.5 kWh for instantaneous, constant 6 kW output. No full-quarter measured energy claim is made here.

Both pumps were restored and verified by readback: power 1, native curve mode 2, target 3050, DHW 5200 and boost 0; control IDLE, saved 0 and error 0. The helper was stopped and disabled, and cleanup was verified. The installed prefix remains 982e160b on both units. No live test process remains.

Offline verification passed the full ASan/UBSan suites, final ARM image tests, 1551 OTA mutation cuts and fake Shelly transfer/cleanup tests. Only existing tracked paths changed; the file index is unchanged. No Git commit or push was performed. Knowhow promotion was considered and intentionally deferred: empirical gains, startup margin and behavior near 40 °C remain project-specific and partly unqualified. The next design issue is explicit temperature-bounded startup demand before a complete power-averaging window, followed by small, persistent correction of the remaining power offset. This has not been implemented or physically validated in this version.

## Early startup and fine correction candidate 784a48ae — 2026-10-10 continuation

The 982e160b physical run exposed approximately two minutes between the first observed compressor restart and the first 45 °C demand, followed by a remaining power deficit near the goal. Candidate `build-effect-startup`, manifest prefix CRC `784a48ae`, addresses those two software behaviors. It does not attempt to shorten Mitsubishi's own restart pause or claim that the previous experiment established its exact duration. OTA and physical validation are in progress at this entry; the candidate's physical response has not yet been qualified.

Fast EFFECT now permits a thermally bounded initial 45 °C demand during SETTLING after the first coherent heating pair: at least one pair, age below 15 s, native heating mode 2 or 7, positive valid compressor Hz and valid supply temperature. The retained power estimate must be nonnegative and more than 150 W below target for the initial increase. This is startup demand, not acceptance of an incomplete rolling window as ready power feedback. Native guard reads and target readback remain in place. The controller marks startup complete only after successful readback, reevaluates the shared thermal ceiling throughout SETTLING, and preserves history as feedback warms up. An unsent adjustment is discarded if qualification is lost; a sent write completes its readback transaction.

The synthetic native scheduler verifies first-pair startup in less than 10 s, measured from the first qualifying heating pair. This does not promise a response within 10 s of mission start. The native zero-Hz pause, potentially about 10 minutes, remains possible; the +0.5 °C pause margin is unchanged. DHW, native ownership, lease expiry, AUTO restoration and the 40 °C actual-supply supervision remain unchanged. Startup demand stays at or below 45 °C; later regulation may use the configured requested-temperature ceiling up to 55 °C, subject to progressive thermal protection.

For fine correction, the quiet band is reduced from 300 W to 150 W, and signed commands smaller than 0.1 °C accumulate until they produce a usable demand step. Carry resets on sign reversal, quiet/no-correction conditions, native pause, a history gap of at least 60 s, or same-direction saturation. This prevents truncation from silently discarding repeated small corrections without introducing an unrestricted power-error integrator. The 35 s Hz lead, 60 s acceleration estimate and nominal 30 s decision interval remain empirical choices. Quantized temperature/flow feedback still limits power precision; a narrower software band is not a measurement-accuracy claim.

Only the mode chunk changes from 982e160b. BL2, flash layout, export veneers, public structures and Modbus schemas remain unchanged. Grouping private regulator variables into one resettable state aggregate saves space while retaining `-Os`. Final mode use is 11824 / 12288 bytes, leaving 464 bytes free; mode RAM is 984 / 4096 bytes. The earlier attempted `-Oz` variant is not used in this artifact.

| Verification | Result |
|---|---|
| Complete host ASan/UBSan suite | Passed |
| First-pair startup and rejected admission cases | Passed; no-pair, age boundary, zero/invalid Hz, wrong mode, invalid supply and already-satisfied power goal covered |
| Guard transition and transaction tests | Passed; unsent cancellation, transition to READY and preservation of sent readback |
| Repeated SETTLING thermal protection | Passed, including reductions at 38 °C and 39.5 °C |
| Fine-carry tests | Passed; accumulation, direction change, quiet band, gap, native pause and saturation |
| AUTO and lease restoration | Passed |
| Actual final ARM image | Passed, including early SETTLING demand, readback and repeated thermal reductions |
| OTA mutation tests | Passed all 1551 cuts |
| Fake Shelly sender | Passed transfer and cleanup tests |
| Physical startup, tracking and sustained thermal limiting | In progress; no success claim yet |

Build metadata is in `procon/modular/build-effect-startup/VERIFICATION.json` and `sizes.json`. The preceding physical result remains dated evidence for 982e160b, not validation of this candidate. Only existing tracked source/test/documentation paths are used; the file index is unchanged. No commit or push was performed for this continuation. General knowhow promotion remains deferred until the empirical behavior is physically verified.

## Failed 784a48ae entry and d64080c7 transition correction — 2026-10-10

The first physical attempt with 784a48ae did not reach an applied EFFECT mission on either pump. Both reported accepted 1, applied 0, control error 8 and BAD_FEEDBACK. The original curve settings were restored and read back, and the helper was stopped/disabled with cleanup verified. Evidence is in `P0080/effect-learning/capture-native6kw-20261010T153111Z`, including failure, restoration, cleanup and raw command/capture logs. This attempt provides no sustained startup, tracking or energy result and supersedes its earlier physical-pending status.

Both final diagnostic records contained three acknowledged writes, nine readbacks and one restoration, consistent with an initial combined MODE_FLOW followed by restoring FLOW and MODE. A focused regression reproduced a defect consistent with the observations: the sampler can retain EF_READY/ready=1 for the current millisecond while freshly accepted native telemetry changes operating mode to 0. Full feedback qualification then fails, but the old controller did not classify that cached READY combination as collection or native waiting; it raised BAD_FEEDBACK before initial application completed. The exact internal call sequence was not directly captured during the physical failure. The offline real-sampler reproduction and a separate control model both failed with the pre-fix implementation and passed with the correction.

Candidate `build-effect-entry`, prefix CRC `d64080c7`, extends `effect_collecting` for fast EFFECT to include cached READY reports that no longer meet `effect_feedback_ok`, only when the reported native mode is already permitted by `native_heat_or_pause`. Unsent actions yield the bus for polling and require native guards again before transmission. Sent actions preserve their SET/readback transaction. The original snapshot is retained, the unapplied initial mission cannot renew itself, and its original finite lease still expires. Native inhibit, external ownership, power-off and unsupported-mode guards are not relaxed. The early startup, thermal ceiling, fine-carry law and existing restoration semantics are unchanged.

Verification passed:

- The complete host ASan/UBSan suite, including 60 combinations of initial transaction stage and feedback transition, original snapshot preservation, single combined SET, both readbacks, finite initial lease, renewal rejection and native guard failures.
- The real sampler/controller cached-READY/new-mode integration regression, with recorded pre-fix failure and post-fix success.
- The actual final ARM image, including cached READY with allowed mode 0 yielding and unsupported native mode 3 still aborting, plus the preceding startup/readback/thermal cases.
- All 1551 OTA mutation cuts and fake Shelly transfer/cleanup tests.

Only mode changes from 784a48ae. It uses 11840 / 12288 bytes, leaving 448 bytes free, and 984 / 4096 bytes of RAM. BL2, layout, exported veneers, public structures, register schemas and `-Os` remain unchanged. Final metadata and logs are in `procon/modular/build-effect-entry`. Physical validation of d64080c7 is pending at this entry; no physical success or reference-curve claim is made. Existing tracked paths only, file index unchanged, no commit or push; generic knowhow promotion remains deferred.

### Signed thermal correction candidate after the 40.5 °C abort

The preceding d64080c7 trial exposed a persistent temperature offset: VP1 held a 39.5 °C request from approximately 758 s, reached actual 40.0 °C around 1025 s, and reached actual 40.5 °C at 1434.8 s. A fixed protective request was therefore insufficient even when the short measured temperature slope was zero. Both original curve states and helper cleanup were verified after the abort. This is a failed physical boundary qualification, not a successful sustained 40 °C limit.

The next candidate combines atomic startup and earlier predictive braking with signed thermal feedback centered on 39.0 °C. Flat actual 39.5 / 40.0 / 40.5 °C produces requested ceilings 38.5 / 38.0 / 37.5 °C. Positive forecast protection can only lower that result; the shared helper is bounded below at 30 °C to prevent unsigned wrap on extreme valid samples. Cooling recovery retains ordinary bounded positive steps. No controller integral, register or ABI field is added.

Focused sanitized host tests `effect-test`, `atomic-entry-test` and `predictive-test` passed. Cases include all three steady offsets, a high valid supply sample, rising forecast that must not raise a lower ceiling, first-pair/atomic readback behavior and bounded recovery while cooling. Equivalent actual-ARM cases were added. Full final build, complete regression/ARM/OTA qualification and physical validation are pending at this entry.

### Final offline qualification of e8fc6d86 — 2026-10-10

`build-effect-thermal` includes atomic MODE_FLOW entry, predictive capture and the signed thermal envelope described above. Only OTA slot 2 (mode) changes from the installed d64080c7 base; all BL2/layout/export interfaces remain unchanged. Mode occupies 12,264 of 12,288 bytes (24 bytes free), with 984 bytes of private RAM. The manifest prefix CRC is `e8fc6d86`.

The complete host suite with ASan/UBSan, final ARM image tests, 1,551 simulated interruption points in the actual C OTA engine and the fake Shelly sender tests pass. SHA256SUMS, source hashes, the exact OTA plan and verification logs are saved beside the final binaries. Two focused regression sources were added for atomic entry and predictive capture; the file index contains 769 tracked paths. Physical deployment and the following bounded trial are recorded separately below; offline passing does not establish physical regulation performance.

### Physical installation of e8fc6d86 — 2026-10-10

`P0080/effect-learning/update-thermal-20261010T164230Z` verifies both known device UIDs running manifest prefix e8fc6d86, advancing CN105 counters, valid snapshots and restored native curve mode. The temporary Shelly helper is stopped after each updater phase. Both original native snapshots were power on, curve mode 2, flow target 3050, DHW target 5200 and boost off. The following 1800-second controlled trial is `capture-native6kw-20261010T165025Z`, mission anchor 16:52:51.349 UTC. VP1 was already at zero Hz before entry, VP2 was at 20 Hz; these differing initial conditions must be preserved in analysis. Trial outcome remains pending in this entry.

### Completed e8fc6d86 physical trial and remaining tracking defect — 2026-10-10

The uninterrupted 1800-second experiment `P0080/effect-learning/capture-native6kw-20261010T165025Z` completed, with observations bracketing both the 900 s and 1800 s integration endpoints. The mission began 16:52:51.349 UTC; endpoint capture work finished at 1843.55 s. Restoration captures are excluded from performance analysis. Both units were verified restored to power on, native curve mode 2, flow target 3050, DHW target 5200, boost off, control IDLE/error 0/saved 0. `cleanup.json` verifies that the Shelly helper stopped. e8fc6d86 remains installed on both devices; no further physical test is running.

| Physical measure | VP1 | VP2 |
|---|---:|---:|
| Maximum observed actual heating supply | 39.5 C | 39.0 C |
| Peak short averaged heat estimate | 6560 W | 6289 W |
| First observed 95% threshold, from mission | 527 s | 194 s |
| First95 after first observed positive Hz | 286 s | Already running before mission |
| Last5 min time-weighted short heat | 4741 W | 4557 W |
| Last5 min observed short heat range | 4315–4954 W | 4354–4780 W |
| Last5 min trend | +105 W/min | +35 W/min |
| First15 min raw hydraulic energy estimate | 0.931 kWh | 1.376 kWh |
| Post-start compressor stop episodes | 0 | 0 |
| Observed control error codes | 0 | 0 |

The entry and temperature corrections passed this bounded physical test: VP2 entered EFFECT without a new compressor stop; VP1 retained its mission through a preexisting pause and increased demand promptly after heating resumed. The previous 40.5 C failure did not recur. These observations do not establish an absolute temperature guarantee between samples or under all future loads.

The overall reference-curve goal is **not complete**. VP1 still overshot and the final5-minute means were below6kW. The first15-minute total was2.307kWh, compared with2.600kWh for the two reference rise curves and3.000kWh for instantaneous flat2x6kW. These are uncalibrated water-model estimates with quantized temperatures and varying flow. The strict paired both95 diagnostic is false, but the closest pair was6560/5696W read20.5s apart; a4W threshold difference is below meaningful resolution and is not evidence that simultaneous95% was physically impossible. Sustained tracking, rather than this threshold artifact, is the substantive limitation.

VP1's first brake occurred near42Hz, but the verified request held44.8C through the subsequent frequency plateau before later52/62Hz responses. Decision counters advanced while adjustments did not. This supports a limitation in the current Hz-rate predictor: after the measured rate becomes flat it can forget delayed native response while a large temperature demand remains. Exact native integral behavior is not proven by the asynchronous observations. A native-demand state that persists through a plateau remains a modeling task.

Slow release from thermal limiting is separately demonstrated. VP1's last in-mission observation was38.0C supply/33.0C return at14L/min, giving conditional hydraulic capacity6.340kW at39.5C and6.827kW at40C, while actual short output was4.876kW. It had regained room for6kW, but did not recover promptly. Its last5 minutes contained no observed temperature-limited phase, so that deficit cannot all be called unavoidable. VP2 ended at38.5C/34.5C and15L/min, with conditional capacities5.225/5.748kW: here hydraulic capacity, deliberate temperature reserve and recovery dynamics all contribute.

There was no observed start/stop cycling. Smaller power fluctuations remain, and a short test cannot establish long-term stability. VP2 held42Hz throughout the last5 minutes while its water-model power varied. The new thermal feedback uses conservative temperature headroom; it should not be described as extracting the maximum possible heat at exactly40C.

Final plot and full statistics: `capture-full.png`, `capture-full.svg`, `capture-analysis.json` beside the raw `events.jsonl`, `rpc.jsonl`, `original-settings.json`, `outcome.json`, `restoration.json` and `cleanup.json`. The final plot was visually reviewed. Final source and firmware remain local in this checkout; no commit or push was performed for this continuation.

## Response memory and demand recovery candidate 7adaecf1 — 2026-10-10

Implemented the operator-requested follow-up to e8fc6d86. The positive Hz-rate forecast now retains a bounded1500W memory, decaying10W/s. A short flat-Hz interval no longer immediately removes the lead estimate. Observed deceleration, demand less than2C above actual, thermal clipping, native waiting and history discontinuity clear the retained lead. This remains an empirical forecast, not identification of Mitsubishi's internal integral law.

Rising estimated power suppresses extra gas only when its30-second projection approaches the goal (within150W). A persistent deficit therefore continues to influence demand. With both measured and predicted power more than750W below target, positive correction and demand less than2C above actual, the actuator may rise1C per qualified decision; otherwise its positive bound remains0.5C. The unchanged signed thermal envelope is applied last. No rejected/clipped command accumulates as future demand, and there is no repeated jump to45/55C after startup. Freshness, pause, ownership, lease and AUTO restoration contracts are preserved.

Qualification: complete ASan/UBSan host suite PASS; final ARM image PASS including retained-response decay, plateau behavior, recovery during modest power rise, thermal priority and all prior entry/restore/module checks;1551 interrupted-update cases PASS; fake Shelly sender PASS. The new predictive regression fails against the prior source at the flat-Hz comparison, and passes against the new source. Sampled-input shadow replay over the prior30-minute log changes15/40 VP1 proposals and7/48 VP2 proposals. In late VP1 observations near4.9kW, previously blocked positive proposals become bounded1C corrections. Replay holds historical measurements/targets fixed and acknowledges hypothetical writes immediately, so it is not a closed-loop simulation and establishes no new physical performance.

The mode image occupies12280/12288 bytes (8 free), with992 bytes of private RAM. The initial build exceeded the slot; a mode-only `-fno-inline-functions-called-once` setting and removal of duplicate pre/post step clamps allow it to fit. Final ARM tests verify the resulting code and veneers. Other module bytes, BL2, layout and public ABI remain unchanged; the exact OTA plan changes only slot2 from e8fc6d86 to7adaecf1. Artifacts, hashes, source fingerprints and logs are in `procon/modular/build-effect-response`.

This candidate is BUILT AND OFFLINE-VERIFIED, NOT INSTALLED. No device access or live control was performed for this follow-up. Both devices were last verified on e8fc6d86 in native curve mode after the preceding experiment. Physical response and tuning still require a bounded live trial; no claim that the reference curve has now been achieved. Existing tracked source/test/docs paths only; repository file index unchanged. No commit/push. Knowhow promotion intentionally deferred because these gains remain specific empirical hypotheses.


### Installed response-memory controller 7adaecf1 — 2026-10-10

Explicitly authorized OTA installation completed on D1/VP1 and D2/VP2. Evidence: `P0080/effect-learning/update-response-20261010T200545Z` (outcome verified_both=true; all four helper cleanup checks passed). Only mode slot 2 changed; BL2 and other modules were preserved. Known device UIDs and manifest prefix 7adaecf1 were verified on both, with advancing CN105 reply counters and snapshots. Both remain power on, native curve mode 2, flow target 3050, DHW target 5200, boost off, and control IDLE/error 0/saved 0. Final compressor readings were 20 Hz and 22 Hz. No heating-control trial or setpoint changes were performed during installation. Effect-control tracking improvements remain physically unvalidated; prior offline test results still apply. The generic live trial identity gate now expects 7adaecf1.
