# P0080 modular firmware and OTA

Source: procon/modular. build.py owns fixed flash/RAM layout, header/export ABI and artifacts. ota.c owns complete-manifest validation, module initialization and stop-and-wait protocol state. flash.c owns guarded RAM flash operations. bl2.c owns startup/system routing/WAIT and baud changes. Common maintenance_ready refuses non-native or active control state. tools/ota.py plans changed chunks; tools/shelly_ota.py performs explicit supervised transfer and cleanup.

Inputs/outputs/side effects and tests: see requirements/package-runs/P0080/functions.md and implementation-report.md. User-facing operating contract: procon/modular/README.md. No live execution performed in this implementation run.

## P0080 frozen telemetry follow-up

Drift tele_read now serves raw400..527, capturing with private capture() on400.
One six-word record stores value/status/age_ms/generation together, with sequence
and link flag in the header. Dispatcher modbus_reply routes validated reads
directly through the existing tele_read veneer; other routing is unchanged.
Python read_snapshot(callback) verifies sequence after all blocks, validates
records and retries boundedly on another reader's capture. No actuator commands.
See procon/modular/README.md and package snapshot-report.md for wire contract,
measured two-chunk update and caveats.

## P0080 BL2 protocol2

Resident normal()/ota_handle() now use prefix56 manifest CRC for version
identity instead of fixed-residue whole-manifest CRC. Status and P8 wire version
are2. Host frame/decode/status/plan/transfer match these semantics and refuse
protocol1. Build metadata includes ota_protocol2. Same ABI and feature binaries.
See bl2-v2-design/report package evidence and current modular README.
# P0080 direct fixed-flow candidate

Deployment update2026-10-10: c9d5de0b is installed on D1 and D2 and verified in native curve operation. The previous installed d9dd3c62 references below are historical. Direct target replacement is ARM/native-test verified; physical setpoint-response qualification remains outstanding.

In build-direct-flow, ctl_submit accepts a next-sequence v2 flow-only FIXED command while an existing flow-only FIXED session is ACTIVE. ctl_reply obtains fresh native26/09/28 guards, retains the initial restoration snapshot and emits FLOW only. applied advances on readback; different pending targets remain BUSY. Same-sequence retries do not renew a lease. AUTO, expiry and failed replacement retain existing restoration semantics. No mode/power write is part of target replacement. Combined DHW/session-mode changes still require a separate session. Capability is identified by candidate manifest prefixCRC c9d5de0b; installed d9dd3c62 does not support it. Same ABI/layout, no new exports, mode slot only, not yet physically installed.

## P0080 brine pump A3 extension (2026-10-10)
OCH722A service manual p30 identifies decimal018 output step0..10 and019 RPM0..9999. A3 support is a wire-mapping candidate pending physical observations, not a confirmed flow sensor. Schedule27,28,18,19 with a full FAST round between service operations; original retry ownership/limits retained. Snapshot schema1 remains20 fields: index11 step, index10 running derived ONLY from valid in-range RPM>0. ZeroRPM is valid stopped feedback, never inferred from missing data or step0. Controller feedback still needs physical correlation for the hydraulic test.
FC04 zero-based87..92 (018) and93..98 (019): retained raw, protocol-valid flag, age_seconds, last status, completion generation, ever-completed. Raw/protocol-valid do not perform engineering range checks; snapshot does. Age TTL60s, link-down invalidates all four services, no stale value becomes valid zero. Temperature and pump sources are asynchronous; a stopped test must require fresh repeated RPM samples and actual water-pump stop feedback. No new pump commands. Only drift/service chunks differ from installed direct-flow; BL2/layout/ABI/control unchanged.

2026-10-10 offline EFFECT candidate: common refreshes FAST between control transactions, drift uses60s measurement TTL, mode treats warmup as collection and accepts qualified feedback younger than60s. Three-slot update, unchanged BL2/ABI. See P0080 implementation report; not yet physically installed.

## Fast demand candidate 2026-10-10
Operator authorized fast-law build, OTA and15min dual6000W trial. PrefixCRC6137dc5e, mode10736/12288 bytes; only mode slot changes from9da1db61, BL2/ABI unchanged. Cap>4000 selects fast law with command ceiling5500; <=4000 retains legacy behavior for compatibility. Actual supply>=4000 aborts/restores in fast mode;>=3800 or positive30s trend projecting3900 brakes demand. Large deficit can request55C promptly; approaching target removes boost to supply+1C,15s decisions then adjust. Measurement age>=15s cannot sustain a new55C decision; existing hard stale60s/link/lease paths still apply. Native pause promptly drops boost and keeps mild demand. The old+5C and unresponsive latches do not constrain the fast branch. Tests: native ASan/UBSan suite, real wire scheduler with55C and faults, fast-law unit boundaries/temperature/pause/aging, host encoder5500/5501, actual built ARM boost/brake,1551 C OTA mutation cuts and fake RPC sender success/lostACK/cleanup. Physical performance not claimed until new trial. Known local changes preserved; no commit/push; existing tracked paths only, index unchanged. Readback decoder now permits55C; legacy v2 command limit remains45C. Uploader uses180s peerWAIT for one-slot update and retries exact packets on malformed responses.

## Current persistent fast candidate — 2026-10-10 (supersedes intermediate fast-limit descriptions)
Candidate prefix852841df; mode11448/12288 bytes. Only mode differs from installed intermediate6137dc5e; BL2/ABI unchanged. Uninstalled intermediatebc31ad62 was superseded before the physical trial. Fast missions (cap>40C, up to55C) retain mission/snapshot/lease across stale/invalid/zero-flow feedback, naturalDHW and communication/read timeouts. They suppress increases, lower an existing boost to39.5C when native heating guards can be verified, resynchronize native readback after link recovery, and resume when feedback qualifies. Native pause no longer has20min abort in fast mode. Legacy low-cap behavior unchanged. AUTO, lease expiry and explicit external ownership/power/mode/inhibit guards remain respected; the controller never forces power-on or overrides Mitsubishi safety logic. Readback mismatch remains an explicit control fault, not treated as successful delivery.
Thermal limiting engages at38C or positive30s projection39C, clamps requested temperature39.5C and disengages below37C with forecast<38C. Actual40C does not end the mission. Measured actual temperature above40C is still a violation of the supervised test boundary, not a commanded higher ceiling. Firmware reduces demand while retaining mission; physical overshoot and native minimum power cannot be ruled out by simulation. Existing phase LIMITED/reason TEMPERATURE_CAP plus requested/instant/short/slow power expose unmet demand and current achieved output, not a calibrated maximum-capacity estimate.
Native ASan/UBSan regressions and integrated real CN105/sampler/controller recovery cases (temporary lostHz, DHW, zero flow and total link loss) passed. Actual ARM boost/brake and module ABI tests passed. OTA engine1551 mutation cuts and fake Shelly duplicate/retry/cleanup tests passed. Live installer uses120s peerWAIT for one56-frame module update and35s remaining-margin gate. No commit/push; existing tracked paths only. Package-specific recovery evidence retained; general physical response/efficiency conclusions await live trial.

### P0080 smooth capture candidate 67ff1a3e

P0080 follow-up: `ctl_submit` permits equal-intent next-sequence EFFECT lease renewal during an internal APPLY adjustment only when the saved mission was already applied (`applied==accepted`). Renewal preserves the pending SET/readback, original settings and regulator state. Exact packet retries do not extend the lease; initial unapplied and changed-intent requests remain BUSY. Offline native tests cover guard/readback boundaries and restoration; this describes the new candidate, not firmware67ff1a3e currently installed.
Installed baseline852841df completed the physical dual6kW trial without mission abort, but tracking oscillated. Both units restored to curve mode. New uninstalled build-effect-smooth retains capture after startup acceleration, limits ordinary taper to2C and trim to0.5C per >=15s decision, and preserves slope across normal pending refreshes. Thermal/degraded-feedback reductions take precedence. Mode11624/12288, mode-only OTA, BL2/ABI unchanged. Host/ARM/OTA tests passed; live stability not established. Details and evidence: requirements/package-runs/P0080/implementation-report.md.


## P0080 Hz-leading regulator candidate982e160b — 2026-10-10

This section supersedes the earlier fast/smooth controller descriptions. `effect_fast` now uses a16-point private history, sampled no faster than5s: approximately35s of Hz change anticipates the delayed water-side power mean, while approximately60s estimates frequency acceleration. Nominal decisions are30s apart. Initial running demand is at most45C; subsequent small corrections can use the configured cap, up to55C. There is no guessed landing-temperature taper. Far-below-target, recent falling-Hz and below-target flat-Hz guards prevent continued braking from an older positive trend. `effect_wait` resets history through native pause/recovery; no new public fields or ABI.

The requested-temperature ceiling decreases continuously as actual supply approaches39.5C, using a10s positive-temperature forecast. Actual39.5C or a30s forecast of40C invokes the protective39.5C demand ceiling. Ordinary15..59s-old feedback holds demand; hard-invalid feedback retains existing guarded recovery. `ctl_tick` no longer invokes the hard fallback merely because a normal partial pair is15s old.

`ctl_submit` permits equal-intent next-sequence EFFECT renewal in ACTIVE or during an internal APPLY action when the saved mission was already applied. It preserves pending wire/readback state and the original restoration snapshot. Initial application and changed intent remain BUSY; identical packet retry never renews. An advanced mission sequence during renewal is not confirmation that the current internal temperature adjustment has finished.

Mode11984/12288B, RAM984/4096B; only mode changes from67ff1a3e, BL2/layout/ABI unchanged. Complete host ASan/UBSan, final-image ARM and1551 OTA mutation-cut tests passed. Deployment is in progress; physical native-regulation validation remains pending at this entry. See the package implementation report for later installation/test evidence.

## P0080 early startup and fractional correction: 784a48ae — 2026-10-10

This entry supersedes the startup and small-correction details for 982e160b. `effect_pause_demand` can propose thermally bounded startup demand during fast SETTLING after one coherent pair younger than 15 s, with native heating mode, valid positive Hz and valid supply. Initial demand is at most 45 °C and is not increased when retained power is already within 150 W of the goal or higher. It reuses the same private history and thermal-ceiling helpers as ready-feedback regulation, so temperature protection continues throughout settling.

`effect_pending_demand` has private values 0 (none), 1 (native pause demand), and 2 (startup demand). `pause_demand_ok` rechecks kind 2 admission while guards are being read and accepts a transition into fully qualified READY feedback. Loss of admission discards an unsent action; an already-sent SET retains its readback. `effect_verified` marks early startup complete only on successful target readback. `effect_wait` no longer repeatedly resets fast SETTLING history or the decision timer; native WAIT still resets startup/history state. These are private interfaces, not additions to the module export ABI or public register schema.

`effect_fast` uses a 150 W quiet band. Signed sub-0.1-°C corrections are retained in private `fine_carry` until a command step is available, then consumed. Quiet/no correction, sign change, native WAIT, history gaps of at least 60 s and same-direction saturation clear carry. The private `effect_state` aggregate is reset as a whole, retaining explicit boot-unknown initialization. This keeps the existing `-Os` build within the fixed mode allocation without changing public structures or layout.

The native first-pair startup regression completes within 10 s in its synthetic scheduler. That interval starts at the first qualified heating pair, not mission acceptance; no physical timing guarantee or bypass of the possible 10-minute native pause is implied. Tests also cover invalid admission, guard transitions, sent readback, repeated thermal reductions, AUTO/lease restoration and fractional-correction resets. Full host ASan/UBSan, actual final ARM image startup/readback/thermal tests, 1551 OTA mutation cuts and fake Shelly transfer/cleanup passed. Mode is 11824 / 12288 bytes, RAM 984 / 4096 bytes; only mode differs from 982e160b. OTA and physical validation are in progress at this entry. Physical tracking and generic knowhow promotion remain pending.

## P0080 cached READY / fresh native-mode transition: d64080c7 — 2026-10-10

Physical initial entry with 784a48ae aborted on both devices before `applied` advanced, with error 8 / BAD_FEEDBACK; both were restored. A real sampler/controller regression reproduced the failure when `effect_feedback_tick` retained cached READY while a newer telemetry observation changed native mode to 0 within the same scheduler millisecond.

In `build-effect-entry`, `effect_collecting` additionally recognizes fast-session cached READY that fails `effect_feedback_ok`, restricted to existing `native_heat_or_pause` modes. Existing `ctl_tick` suspension and `ctl_next` guard requalification then defer unsent work without deleting the action or original snapshot. Already-sent SET/readback transactions retain their phase. Unsupported native modes and native power/ownership/inhibit failures remain faults. Initial unapplied missions cannot extend their lease through an equal-intent renewal; bounded expiry and restoration remain unchanged.

Prefix CRC d64080c7 changes only mode: 11840 / 12288 bytes, RAM 984 / 4096 bytes. The full host ASan/UBSan suite, 60 entry-transition combinations, real sampler/controller pre-fix failure and post-fix pass, actual final ARM transition tests, 1551 OTA mutation cuts and fake Shelly transfer/cleanup passed. No ABI/schema/BL2 change. Physical validation remains pending at this entry. The earlier startup/fine-correction contracts remain; this is an entry-race correction, not a new regulator law.

## 2026-10-10 thermal correction after the physical boundary breach

The later physical test observed 40.5 °C actual supply on VP1 while its requested temperature remained 39.5 °C. The previous fixed protective request could not correct the persistent actual-to-requested offset. Both units were restored to their original curve state and the test helper was stopped. The new candidate therefore replaces that fixed thermal floor with continuous signed feedback around 39.0 °C.

In centidegrees, let `lead = supply + max(temperature_rate_per_minute, 0)/6` and `margin = 3900 - lead`. The candidate ceiling is `3900 + (margin > 0 ? 3*margin : margin)`. A positive 30 s forecast reaching 4000 may only reduce that result to at most 3900, never raise a lower result. The final ceiling is bounded to 3000 through the configured command cap; the lower bound prevents unsigned conversion of an extreme negative result. At flat measured supply of 39.5, 40.0 and 40.5 °C, requested ceilings are respectively 38.5, 38.0 and 37.5 °C. This is a ceiling, so it does not raise an existing lower request.

Atomic mode entry, first-pair startup and ready-feedback regulation share this helper. Cooling releases the ceiling but does not replay startup or saved upward corrections: ordinary positive changes remain at most 0.5 °C per decision. Phase LIMITED / reason TEMPERATURE_CAP continues to expose an active constraint. No new register, cross-module ABI or integral state is introduced. Native guards, lease and restoration semantics remain unchanged. The measured 40 °C trial boundary is unchanged; this empirical correction still requires physical validation and does not guarantee zero overshoot.

### Physical status after e8fc6d86 trial — 2026-10-10

Both units run e8fc6d86. A30-minute dual6kW-request trial completed with observed maxima39.5/39.0C, no poststart compressor stops and verified AUTO/curve restoration. Initial entry and thermal protection improved, but sustained6kW tracking is not qualified: last5-minute means were4.741/4.557kW and VP1 recovered slowly after thermal headroom returned. See the final dated section in `requirements/package-runs/P0080/implementation-report.md`; do not interpret temperature limiting as proof that all power deficit is physically unavoidable.

### Uninstalled response-memory candidate7adaecf1

Offline-qualified P0080 follow-up retains a bounded, decaying acceleration forecast over short frequency plateaus and strengthens low-demand recovery after limiting. Positive steps may reach1C only with measured and predicted deficit>750W and requested-minus-actual<2C; otherwise0.5C. The thermal envelope remains unchanged and applies last. Full host/ARM/OTA tests pass, but no new physical performance is claimed. Devices remain on e8fc6d86. See the dated implementation-report section and `procon/modular/build-effect-response/VERIFICATION.json`.
