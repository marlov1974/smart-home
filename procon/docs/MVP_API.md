# P0072 r1 — read-only MVP API version 1

Experimental firmware. Operator flash and physical validation pending. Input0=888, input1=72, input68=1 (revision within package), input69=1 (API), input70=1 (bit0 telemetry; all control capability bits zero), input71=4 (control unavailable). FC04 only, slave1, 9600 8N1, max16 words/read. FC06/FC16 and every other function return exception1; broadcasts ignored. No SET frames, no pump commands, no persistence. Reboot resumes reading without changing Mitsubishi settings. Command sequence/ack/lease implementation remains deferred; there is no claimed AUTO fallback in this build because it never takes control.

Legacy0–67 retain P0071 addresses. Input39 owner2 now means any FAST GET; input42 counts individual service operations, not a pair. Input32 state4 means one operation DONE. Reserved72–99 read0. API address map is zero-based, independent of vendor H/I names.

For zero-based field index i below:
- inputs100+2*i and101+2*i contain signed32 high word then low word; transport words big-endian;
- input140+i status: 0 never,1 valid/fresh,2 stale/disconnected/time-skew,3 range/encoding rejected,4 unavailable;
- input160+i age in seconds, saturating65535; never/unavailable65535; derived age is oldest input;
- input180+i update generation, wrapping16bits; derived generation sum of constituents (compressor state copies Hz).

Invalid values encode INT32_MIN (0x80000000), not zero. Status1 means accepted protocol value, not proven sensor identity/calibration. Multiple Modbus reads are not atomic: bracket with generation AND status reads (helper does). A counter wrap during an entire long capture cannot prove coherence; intended captures last seconds. Raw buffers retain latest matched response, even range-rejected data. A physical stopped compressor/zero flow remain valid zero.

|i|Value|Units/meaning|Source|
|--:|---|---|---|
|0|Brine inlet TH32 candidate|0.01 C, source whole-degree resolution|A3/27 signed LE bytes4–5|
|1|Brine outlet TH34 candidate|0.01 C, source whole-degree resolution|A3/28 signed LE bytes4–5|
|2|Brine delta|inlet minus outlet,0.01 C|derived, asynchronous service samples|
|3|Heating supply|0.01 C|GET0C BE bytes1–2|
|4|Heating return|0.01 C|GET0C BE bytes4–5|
|5|Heating delta|supply minus return,0.01 C|same GET0C response|
|6|Primary flow|0.01 L/min, source whole L/min|GET14 byte12 times100|
|7|Delivered water heat|signed W, positive heating|formula below|
|8|Compressor frequency|Hz|GET04 byte1|
|9|Compressor running|Hz greater than0, inferred boolean|derived from valid Hz, not independent run bit|
|10|Brine pump running|P0080 A3/019 RPM-derived boolean|valid only from fresh in-range reported RPM; A3 hardware correlation ongoing|
|11|Brine pump step|P0080 A3/018 output step0..10|commanded output, not measured flow; see P0080 extension below|
|12|Primary water pump running|0/1, reference-backed candidate|GET15 byte1|
|13|Primary water pump level|reference-backed candidate0–5, not measured RPM|GET15 byte2 lookup, see PUMPS|
|14|DHW tank|0.01 C|GET0C BE bytes7–8|
|15|Outdoor|0.01 C, whole-degree reference decoder|GET0B floor(byte11/2)-40, then times100|
|16|Current reported Zone1 flow target|0.01 C|GET09 BE bytes5–6; curve behavior requires hardware comparison|
|17|Current reported DHW target|0.01 C|GET26 BE bytes8–9|
|18|Actual operating mode|raw Mitsubishi enum0–7, NOT requested control mode|GET26 byte4|
|19|Electric heater state|bit0 booster1,bit1 booster2,bit2 booster2plus,bit3 immersion|GET14 bytes2–5, each must be0/1|

Operating enum:0 off,1 DHW,2 heating,3 cooling,4 zero-V,5 frost protection,6 legionella,7 heating eco, from pinned reference header. It does not encode the requested OFF/AUTO/FIXED_FLOW/DHW abstraction. Raw GET26 also retains system power at3 and control modes at6/7 for investigation.

New direct mappings are based on F1p reference7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5, EcodanDecoder.cpp Process0x04/09/0B/0C/14/15/26 and EcodanDecoder.h enums. Local source was inspected at this exact commit. Prior Geodan A1M observations corroborate these quantities' existence but do not prove our clean decoder. Brine has P0071 completed raw5 and operator display"5" single-point evidence; identity across channels/negative range still needs correlation.

## Schedule and freshness

FAST queries04,0C,14,0B,09,15,26, one attempt each; then one exclusive A3 operation. Round robin service table27,28: FAST→27(all retries)→FAST→28(all retries). Ten service attempts max,1000ms start-to-start minimum;800ms reply timeout,1000ms TX queue timeout,50ms turnaround. No normal query/connect between service retries. Connection recovery only at operation boundary; finite failures advance to the other service on next cycle. Missing FAST response does not halt cycle. Existing UART and watchdog loops remain unchanged.

The EFFECT-refresh candidate expires compressor and other direct FAST measurements at60s; brine remains60s; disconnect invalidates cached direct/service samples. Raw data survives for diagnosis. The candidate proactively refreshes FAST between control transactions. Installed pump firmware still uses the older10s Hz/30s direct TTL until updated. Brine delta can mix samples acquired several seconds apart; it is not a simultaneous high-resolution measurement.

Conservative accepted ranges: brine -40..80C; flow/return/tank and targets0..100C; outdoor -40..80C; flow0..200L/min; boolean0/1; operating0..7; pump lookup exact. These are parser plausibility bounds, NOT writable target limits. Missing sentinels/range failures cannot produce valid thermal power.

## Heat calculation

`W = trunc(flow_cL_min * delta_cC * 418 / 60000)` using signed64 intermediate, signed32 output. Assumes water density1kg/L and heat capacity4180J/(kg K). No glycol correction; this is water-side power, not brine-side power. Positive supply-return gives positive heat, negative gives negative cooling. Zero flow/delta gives valid0 if sources are valid. Invalid/stale source or acquisition skew>2000ms between GET0C and GET14 gives invalid power. Candidate TTL60s still permits an aging cached power estimate; consumers should check exposed age for their own cadence requirements.

20L/min and5.00K yields6966W (integer truncation). Whole-L/min source quantization and unverified temperature accuracy limit precision despite the W unit. No COP, electrical measurement, energy integration, autonomous stress testing or closed-loop power control.

## Raw evidence and operator readback

Inputs200–255 hold seven16-byte matched FAST payloads,8 words each in schedule order04,0C,14,0B,09,15,26. Each raw word low byte first. Completion payloads A3 remain52–67. Use generations/status to establish new data rather than zero-filled buffers.

After operator flash:
`python3 procon/tools/read_mvp.py --samples 10 --interval 2 --output <new-file.jsonl>`
The helper only invokes MbRtuClient.ReadInputRegisters. Interval is minimum sample-group period; serial transactions can take longer. Correlate physical flow/return/DHW/outdoor/flow/Hz/targets, brine completions, error counters and LED. Do not test control until a later actuating revision has explicit verified semantics and telemetry passes. Hardware attempts used for this revision:0/3.

## P0072 r2 update

Revision2 adds supervised, reference-backed control commands with snapshot/readback/runtime lease restoration. See [control API](CONTROL_API.md). Earlier r1 read-only statements remain historical. No hardware control validation or reboot restoration is claimed.

Revision3 adds GET28 as the eighth FAST query and input283–298 diagnostics without changing the20-value map or raw200–255. Identity68=3. See [CONTROL_API](CONTROL_API.md).

## P0080 brine pump A3 extension (2026-10-10)
OCH722A service manual p30 identifies decimal018 output step0..10 and019 RPM0..9999. A3 support is a wire-mapping candidate pending physical observations, not a confirmed flow sensor. Schedule27,28,18,19 with a full FAST round between service operations; original retry ownership/limits retained. Snapshot schema1 remains20 fields: index11 step, index10 running derived ONLY from valid in-range RPM>0. ZeroRPM is valid stopped feedback, never inferred from missing data or step0. Controller feedback still needs physical correlation for the hydraulic test.
FC04 zero-based87..92 (018) and93..98 (019): retained raw, protocol-valid flag, age_seconds, last status, completion generation, ever-completed. Raw/protocol-valid do not perform engineering range checks; snapshot does. Age TTL60s, link-down invalidates all four services, no stale value becomes valid zero. Temperature and pump sources are asynchronous; a stopped test must require fresh repeated RPM samples and actual water-pump stop feedback. No new pump commands. Only drift/service chunks differ from installed direct-flow; BL2/layout/ABI/control unchanged.

## Fast demand candidate 2026-10-10
Operator authorized fast-law build, OTA and15min dual6000W trial. PrefixCRC6137dc5e, mode10736/12288 bytes; only mode slot changes from9da1db61, BL2/ABI unchanged. Cap>4000 selects fast law with command ceiling5500; <=4000 retains legacy behavior for compatibility. Actual supply>=4000 aborts/restores in fast mode;>=3800 or positive30s trend projecting3900 brakes demand. Large deficit can request55C promptly; approaching target removes boost to supply+1C,15s decisions then adjust. Measurement age>=15s cannot sustain a new55C decision; existing hard stale60s/link/lease paths still apply. Native pause promptly drops boost and keeps mild demand. The old+5C and unresponsive latches do not constrain the fast branch. Tests: native ASan/UBSan suite, real wire scheduler with55C and faults, fast-law unit boundaries/temperature/pause/aging, host encoder5500/5501, actual built ARM boost/brake,1551 C OTA mutation cuts and fake RPC sender success/lostACK/cleanup. Physical performance not claimed until new trial. Known local changes preserved; no commit/push; existing tracked paths only, index unchanged. Readback decoder now permits55C; legacy v2 command limit remains45C. Uploader uses180s peerWAIT for one-slot update and retries exact packets on malformed responses.

## Current persistent fast candidate — 2026-10-10 (supersedes intermediate fast-limit descriptions)
Candidate prefix852841df; mode11448/12288 bytes. Only mode differs from installed intermediate6137dc5e; BL2/ABI unchanged. Uninstalled intermediatebc31ad62 was superseded before the physical trial. Fast missions (cap>40C, up to55C) retain mission/snapshot/lease across stale/invalid/zero-flow feedback, naturalDHW and communication/read timeouts. They suppress increases, lower an existing boost to39.5C when native heating guards can be verified, resynchronize native readback after link recovery, and resume when feedback qualifies. Native pause no longer has20min abort in fast mode. Legacy low-cap behavior unchanged. AUTO, lease expiry and explicit external ownership/power/mode/inhibit guards remain respected; the controller never forces power-on or overrides Mitsubishi safety logic. Readback mismatch remains an explicit control fault, not treated as successful delivery.
Thermal limiting engages at38C or positive30s projection39C, clamps requested temperature39.5C and disengages below37C with forecast<38C. Actual40C does not end the mission. Measured actual temperature above40C is still a violation of the supervised test boundary, not a commanded higher ceiling. Firmware reduces demand while retaining mission; physical overshoot and native minimum power cannot be ruled out by simulation. Existing phase LIMITED/reason TEMPERATURE_CAP plus requested/instant/short/slow power expose unmet demand and current achieved output, not a calibrated maximum-capacity estimate.
Native ASan/UBSan regressions and integrated real CN105/sampler/controller recovery cases (temporary lostHz, DHW, zero flow and total link loss) passed. Actual ARM boost/brake and module ABI tests passed. OTA engine1551 mutation cuts and fake Shelly duplicate/retry/cleanup tests passed. Live installer uses120s peerWAIT for one56-frame module update and35s remaining-margin gate. No commit/push; existing tracked paths only. Package-specific recovery evidence retained; general physical response/efficiency conclusions await live trial.

### P0080 smooth capture candidate 67ff1a3e
Installed baseline852841df completed the physical dual6kW trial without mission abort, but tracking oscillated. Both units restored to curve mode. New uninstalled build-effect-smooth retains capture after startup acceleration, limits ordinary taper to2C and trim to0.5C per >=15s decision, and preserves slope across normal pending refreshes. Thermal/degraded-feedback reductions take precedence. Mode11624/12288, mode-only OTA, BL2/ABI unchanged. Host/ARM/OTA tests passed; live stability not established. Details and evidence: requirements/package-runs/P0080/implementation-report.md.

Live status2026-10-10: smooth67ff1a3e installed on both devices and completed a bounded dual6kW test. Taper and native-pause recovery observed; stable6kW tracking NOT achieved. Both restored to curve mode. Short180s leases can expire during frequent APPLY because renewal is accepted only in ACTIVE; test repeat used1800s bounded lease, no firmware renewal fix. See P0080 implementation report.


## P0080 current built EFFECT behavior:982e160b — 2026-10-10

This supersedes the controller behavior in earlier fast/smooth candidate notes. Build-effect-rocket changes only mode; public schemas/addresses, BL2 and layout are unchanged. Deployment is in progress, with native physical validation pending at this entry.

- EFFECT cap>4000 selects the Hz-leading law; cap<=4000 retains legacy behavior. Cap remains bounded by5500. Running initial demand is at most4500, with no startup increase when measured power is already at/above the goal.
- Approximately35s Hz change leads the60s rolling water-side power; approximately60s Hz change estimates acceleration. Nominal30s corrections are bounded to50cC, with up to100cC decrease for a large predicted overshoot. Recent falling/flat Hz and large power-deficit guards suppress inappropriate braking. No calibrated electrical power/COP or internal FTC integrator is implied.
- Ordinary feedback age15000..59999ms holds demand. Thermal protection can still lower it; source qualification still requires age<60000ms. Hard-invalid/native pause/link recovery retains the mission and original snapshot subject to existing lease/ownership safeguards.
- In cC, `thermal_cap=min(configured_cap,3950+3*max(0,3950-Tlead10s))`. Actual>=3950 or positive30s forecast>=4000 sets this ceiling to3950. When constrained, phase LIMITED/reason TEMPERATURE_CAP reports the active limit alongside existing actual/requested power fields. There is no new maximum-capacity measurement or guaranteed overshoot-free temperature claim.
- Equal-intent next-sequence EFFECT renewal is accepted in ACTIVE and in an internal APPLY adjustment of a saved, already-applied mission (`applied==accepted`). Renewal preserves the pending transaction and original snapshot; it is not evidence that an internal FLOW adjustment completed. Initial/unapplied or changed-intent commands remain BUSY. Exact same-sequence retransmissions do not extend the lease. AUTO/expiry semantics remain unchanged.

Host, final-image ARM and1551 OTA mutation-cut tests passed. Consult the P0080 implementation report for installation and physical test status; historical67ff1a3e test results do not validate this candidate.

## P0080 early startup extension: 784a48ae — 2026-10-10

This candidate supersedes the startup and small-correction behavior of 982e160b. Public addresses, command formats, feedback quality definitions and source freshness limits are unchanged. Only the mode chunk changes. OTA and physical validation are in progress at this entry; no physical performance improvement is yet claimed.

For fast EFFECT (configured cap above 4000), a first coherent heating pair during SETTLING may trigger an initial demand of at most 4500, limited by the existing thermal ceiling. Admission requires at least one pair, age below 15000 ms, native mode 2 or 7, compressor Hz in 1..254 and supply in 0..10000 cC. An initial increase also requires a nonnegative retained power estimate more than 150 W below the goal. This narrowly authorizes startup temperature demand before the complete power window; it does not make SETTLING equivalent to ready power feedback. Native guards and successful target readback remain mandatory. The thermal ceiling continues to be evaluated during SETTLING, including after the initial target has been verified.

The native regression verifies startup completion within 10 s of the first qualifying heating pair. It does not promise startup within 10 s of an EFFECT command: zero-Hz native waiting, including a possible 10-minute restart pause, remains under Mitsubishi control. The existing pause-demand margin, DHW handling, lease expiry and AUTO restoration are unchanged. A transition that invalidates a pending startup cancels an unsent command; an already-sent command retains its readback transaction.

The ready-feedback regulator now uses a 150 W quiet band and retains signed sub-10-cC corrections between decisions. Carry clears on direction change, quiet/no correction, native pause, a history gap of at least 60000 ms, or same-direction saturation. No new register exposes this private carry, and no improved measurement precision or calibrated power accuracy is implied. Existing 35 s Hz leading, 60 s acceleration, 30 s decisions, thermal limits and in-flight lease renewal semantics remain.

Full host ASan/UBSan, actual final ARM startup/readback/thermal tests, 1551 OTA mutation cuts and fake Shelly transfer/cleanup tests passed. Candidate mode size is 11824 / 12288 bytes, RAM 984 / 4096 bytes. See the P0080 implementation report for subsequent physical results.

## P0080 entry transition correction: d64080c7 — 2026-10-10

Candidate 784a48ae aborted initial application on both pumps with error 8 / BAD_FEEDBACK, accepted 1 and applied 0. Both original curve settings were restored. There is no sustained physical tracking result for that attempt.

The latest `build-effect-entry` candidate, prefix CRC `d64080c7`, preserves the public protocol and the preceding startup/fine-correction contract. Fast EFFECT temporarily collects feedback when cached quality is READY but newer telemetry fails full feedback qualification, provided native mode remains one of the existing permitted heat/pause/DHW modes. This does not make the incomplete report valid for a new power correction. An unsent action yields and rechecks native guards before sending; a sent action still completes readback. The original snapshot, finite initial lease, initial renewal restrictions and native ownership/inhibit/power/mode guards remain unchanged.

The same-millisecond sampler/native-mode race failed before the fix and passed after it. Full host tests, 60 entry-transition cases, actual final ARM transition tests, 1551 OTA mutation cuts and fake Shelly transfer/cleanup passed. Only mode changes, using 11840 / 12288 bytes and 984 / 4096 bytes of allocated RAM. Physical validation is pending at this entry; no new timing, stability or power-accuracy claim is made.

## 2026-10-10 thermal correction after the physical boundary breach

The later physical test observed 40.5 °C actual supply on VP1 while its requested temperature remained 39.5 °C. The previous fixed protective request could not correct the persistent actual-to-requested offset. Both units were restored to their original curve state and the test helper was stopped. The new candidate therefore replaces that fixed thermal floor with continuous signed feedback around 39.0 °C.

In centidegrees, let `lead = supply + max(temperature_rate_per_minute, 0)/6` and `margin = 3900 - lead`. The candidate ceiling is `3900 + (margin > 0 ? 3*margin : margin)`. A positive 30 s forecast reaching 4000 may only reduce that result to at most 3900, never raise a lower result. The final ceiling is bounded to 3000 through the configured command cap; the lower bound prevents unsigned conversion of an extreme negative result. At flat measured supply of 39.5, 40.0 and 40.5 °C, requested ceilings are respectively 38.5, 38.0 and 37.5 °C. This is a ceiling, so it does not raise an existing lower request.

Atomic mode entry, first-pair startup and ready-feedback regulation share this helper. Cooling releases the ceiling but does not replay startup or saved upward corrections: ordinary positive changes remain at most 0.5 °C per decision. Phase LIMITED / reason TEMPERATURE_CAP continues to expose an active constraint. No new register, cross-module ABI or integral state is introduced. Native guards, lease and restoration semantics remain unchanged. The measured 40 °C trial boundary is unchanged; this empirical correction still requires physical validation and does not guarantee zero overshoot.

### Physical status after e8fc6d86 trial — 2026-10-10

Both units run e8fc6d86. A30-minute dual6kW-request trial completed with observed maxima39.5/39.0C, no poststart compressor stops and verified AUTO/curve restoration. Initial entry and thermal protection improved, but sustained6kW tracking is not qualified: last5-minute means were4.741/4.557kW and VP1 recovered slowly after thermal headroom returned. See the final dated section in `requirements/package-runs/P0080/implementation-report.md`; do not interpret temperature limiting as proof that all power deficit is physically unavoidable.

### Uninstalled response-memory candidate7adaecf1

Offline-qualified P0080 follow-up retains a bounded, decaying acceleration forecast over short frequency plateaus and strengthens low-demand recovery after limiting. Positive steps may reach1C only with measured and predicted deficit>750W and requested-minus-actual<2C; otherwise0.5C. The thermal envelope remains unchanged and applies last. Full host/ARM/OTA tests pass, but no new physical performance is claimed. Devices remain on e8fc6d86. See the dated implementation-report section and `procon/modular/build-effect-response/VERIFICATION.json`.


P0081 candidate adds a separate diagnostic range600..631 and exact FC16/600/count8 envelope; existing control300 is unchanged. See [RAW API](../modular/RAW_API.md). The new range is unavailable on installed7adaecf1 until activation.
