# P0080 current release: BL2 protocol2 + frozen telemetry

## Installed EFFECT + rolling pair-energy v4 — 2026-10-16

Both devices run the atomic Mode+Service+Debug Command v4 update: VP1 manifest
`57ee1885`, VP2 `fd001ec7`. Actual-supply priority is 45 C and requested flow
may reach 55 C. Firmware diagnostic schema 4 exposes the adaptive model and
accepts one exact-UID C077 gain seed per boot; the seed changes RAM only.

Shelly Script 7 contains executor 1.5.1, SHA-256
`29813a747a7c2decef73aa80bc041383344a51dd8c5ab8d907dd926e9f1832a5`,
stopped and disabled. It consumes a strict rolling four-quarter KVS plan,
integrates the two pumps independently and stores only qualified long-term gain
in UID-bound Shelly KVS. A read-only live runtime validation passed after fixing
the validation self-stop for unready post-flash feedback. No physical energy
mission was part of that installation. See the P0080 installation report and
`release-effect-energy-v4-20261016/`.

## RAM-only adaptive-gain seed candidate — 2026-10-15

The firmware now has a bounded way for an external controller to preserve only
the long-term `kW -> Hz` gain across a reboot without using Procon EEPROM.
FC16/300..307 accepts the versioned `C077` gain envelope only while the existing
native maintenance gate is quiescent. It validates gain range and carries all
96 factory UID bits exactly. Input310 exports the current gain, input346 reports
whether this boot accepted a seed, and input308 reports
diagnostic version4. Bias, EFFECT trim and learning counters are neither
imported nor reset by acceptance. A reboot restores gain1350, bias-1090 and
seed flag0. Only the first valid seed per boot is accepted; exact retries are
idempotent and conflicting gain/UID packets fail. No flash,
EEPROM or option-byte path is called. The exact wire contract and host flow
are documented in `../docs/CONTROL_API.md`; Shelly KVS persistence is a separate
host-side change.

Latest physical repeat (2026-10-12), unchanged firmware: both requested5kW.
Last5min delivery6.190/6.035kW, maximum actual40.5/39.5C. VP1 waited about5min
before starting; neither stopped after startup. Both restored to their current
30C curve settings. This repeat failed sustained5/5kW tracking and the strict
<40C goal on VP1. The demand floor can prevent further gentle braking when the
request is already near/below actual. See the latest P0080 CHANGELOG for evidence
and limits; the previous trial's good temperature result is not a general guarantee.

Latest EFFECT continuation (2026-10-11): both units now have the same adaptive
Mode, with manifest fingerprints D1 `b39273d4` and D2 `b8fb9712`. Their other
modules remain different intentionally; BL2 is unchanged. Build the controller
with `make effect-adaptive`. D2 keeps its prior Common/Dispatcher when composing
the Mode-only update. See the latest P0080 CHANGELOG section for exact hashes,
qualification and live evidence; the dated sections below describe earlier work.

The current operating priority is **actual supply below40C first, requested heat
power second**. The requested temperature is an actuator, allowed up to55C.
A60s/source-age temperature forecast limits demand; running reductions are
bounded0.5C per30s and avoid a new request below min(current,actual+0.5C).
Neither a brief temperature overshoot nor time above40C ends the mission.
Native safeguards, valid-data/ownership guards, lease and AUTO remain in force.
The controller may deliver less than the requested kW to respect temperature;
this is not proof of the pump's maximum physical capacity. The dual6/5kW trial
completed900s with maximum actual39C on both and no observed in-trial compressor
stops. Both original curves were restored and verified. Last5min mean delivery
was4.719/5.568kW: temperature control passed this trial, sustained6/5kW tracking
did not. See the latest package CHANGELOG for the shared-load limitations.

Use `release-bl2-v2/` for the authorized original-bootloader installation.
Build with `make bl2-v2`; validate with `make bl2-v2-test` (Unicorn Python/toolchain
settings as below). All seven feature chunks are identical to the snapshot OTA
release. Only BL2 changes (6584/8192 bytes). Older release directories and the
sections below are historical evidence; old snapshot build targets are retired.

Protocol2 changes both resident status word385 from1 to2 and P8 wire version byte
from1 to2. CRC32(first56 manifest bytes) is the version fingerprint, used for
status, BEGIN expected-base and postboot validation. The on-flash manifest layout,
module ABI and slot addresses remain unchanged. Host planning requires
`ota_protocol:2` in build sizes metadata and rejects BL2 changes; a protocol1
installation cannot migrate using OTA. The original bootloader path is required.

Updated host rejects old status before ENTER/WAIT, keeps2s for COMMIT/EXIT, and
validates the data-only manifest fingerprint after boot. No cryptographic
signature/authenticity claim. These checks detect accidental mismatches.

The protocol2 candidate passes actual ARM status/CRC/snapshot/flash guards and
native C OTA with523 mutation cuts, old-wire rejection and the previously missed
same-whole-CRC/different-valid-base regression. Host delayed-ACK and old-status
rejection tests pass. Physical installation evidence is in the package report.

---

# P0080 — modular EFFECT firmware and chunk OTA

Offline-verified implementation candidate based on local P0076 pause-r2, pinned in
`baseline.json`. No physical installation, OTA or heating commands were executed
by this package run. This is separate from the MVP3 flash-test firmware currently
used for the physical self-programming proof.

## Build and tests

```
python3 build.py --toolchain /path/to/arm-gnu-toolchain
make test PYTHON=/path/to/python
make test-arm PYTHON=/path/to/python-with-unicorn-and-pyelftools
```

Compiler: GNU Arm14.3.1, Cortex-M4 Thumb soft ABI, -Os, independent images,
no cross-module LTO. Native regressions use clang ASan/UBSan. Outputs are under
`build/`: eight ELF/map/raw/padded images, `sizes.json`, `manifest.bin`, and the
96KiB `install.bin` envelope plus `install.json` for the established first-install
flasher. `build-next/` is a deliberately moved service implementation used only
as an independent-update test fixture; do not treat it as a production release.

## Partition and ABI

| Chunk | Base | Reserved | Ownership |
|---|---|---:|---|
| BL2 | 08008000 | 8KiB | Boot, RS485, system commands, WAIT/OTA, flash, identity, watchdog |
| Common | 0800A000 | 12KiB | CN105 transaction owner and scheduler, routing to service/control |
| Dispatcher | 0800D000 | 4KiB | Existing Modbus application envelope and reads |
| Mode | 0800E000 | 12KiB | P76 control, EFFECT, feedback windows, native pause policy |
| Drift | 08011000 | 4KiB | Telemetry decoding/cache |
| Service | 08012000 | 4KiB | Actual A3 state machine, retry/response decoding |
| Debug command | 08013000 | 4KiB | Existing supervised command adapter; no new arbitrary RAW path |
| Debug telemetry | 08014000 | 4KiB | Extracted P76 feedback diagnostics |
| Manifest | 08015000 | 2KiB | Complete compatible image set, commit marker |

54KiB reserved, inside the exercised96KiB application envelope. See measured
results in the package-run report; reserved size is not transmitted code size
for first installation. OTA sends the full padded size of each changed chunk.

Each module has a64-byte header and fixed4-byte Thumb branch veneers. Functions
may move within a slot. Modules are linked separately; imports reference the
veneer addresses, never another module's internal symbols. Full ABI/layout
fingerprint includes export lists and per-slot RAM reservations. Changing those
requires a new initial installation; compatible implementation changes use OTA.
Every module's .data and .bss is initialized by BL2 before calling Common.cn_init.
There is one stack/VTOR and no private module heap or interrupt owner. BL2 exports
low-level UART access for the current scheduler. All modules are one compatible
set: if any is invalid, none runs; resident identity/status and OTA remain.

The adaptive EFFECT model is a paired Mode/Service implementation detail. To
keep Mode inside its fixed 12KiB slot, Service owns its code and RAM and exposes
two private veneers at `08012068` and `0801206C` (Thumb entry addresses
`08012069` and `0801206D`). They immediately follow Service's ten public veneers,
so the public export count, export order and layout fingerprint remain unchanged.
Any build changing this private interface must update Mode and Service together;
the complete-manifest CRC gate prevents either half from running alone.

Common owns transaction sequencing; A3-specific timing/state remains in the
service chunk. EFFECT calls common services and does not require debug commands.
The debug command adapter is small because the latest P76 had no full RAW engine;
this refactor preserves its supervised FC16 functionality rather than inventing
an unrestricted command mechanism.

## First install vs later OTA

First install must replace the monolithic application with `install.bin` through
the existing original bootloader/Shelly flasher, retaining the full96KiB erase
contract. No existing MVP3/P76 monolith understands this OTA protocol. Original
bootloader below08008000 and resident BL2 are never updated by chunk OTA.

After an operator-confirmed normal boot/DIP address, read FC04 raw384/count16:
B180, protocol1, full-set-valid, mode, layout high/low, manifestCRC high/low,
UID six words, native-maintenance-ready, schema1. Ordinary P76 registers remain.
OTA refuses an active control lease and requires recent native curve/DHW
permission observations. It never sends pump settings to manufacture readiness.
Native curve restoration across arbitrary controller power loss remains an old
P76 limitation, not solved by modularization.

## Protocol

Addressed FC16 raw384/count4: `[B180, FF(ENTER) or FE(WAIT), nonzero nonce, seconds]`.
Duration1..3600; sender uses900. Response is the standard Modbus write ACK. BUSY6
means native/transaction preconditions not satisfied; host may retry that explicit
rejection. WAIT retains CN105 polling but emits no RS485 responses until timeout
or reset. ENTER ACK is sent at9600, then only the target listens at115200.

Addressless OTA frames: `P8`, command byte, version1, LE sequence16, payload length16,
payload0..240, CRC32-IEEE little-endian over header+payload. Maximum252 wire bytes.
Commands1 HELLO,2 BEGIN,3 WRITE,4 COMMIT,5 STATUS,6 EXIT. Replies carry status,
active state, next sequence, current slot/offset and UID. See `tools/ota.py`.
WRITE payload contains slot32+offset32+up to232 firmware bytes (eight-byte aligned).
Thus the verified252-byte wire ceiling is retained;240 is total OTA payload,
not240 firmware bytes plus additional addressing overhead.

BEGIN binds exact target UID and expected current manifest CRC, complete new
manifest and changed-slot mask. Before modifying flash, unchanged slots must
already match the new manifest. Manifest is erased first; selected slots then
erased. Writes are sequential and checked. Exact duplicate mutations return their
last reply without reprogramming ECC words. Conflicting/out-of-order requests
fail. CRC-corrupt/incomplete input is silent. Commit verifies every slot/header,
writes manifest content then final checksum/marker doubleword. EXIT ACK precedes
reset. Update errors latch the session; reset/re-enter for a repair attempt.
After120 seconds without an accepted uploader frame the device returns to9600
maintenance without running modules. Host can explicitly re-enter and restart.

CRC is accidental-corruption detection, not a signature. Use trusted locally
built images and an isolated, single-master maintenance network. There is no
firmware authentication or anti-rollback claim.

## Mac → Shelly → Procon sender

Offline plan:
```
python3 tools/shelly_ota.py old/build new/build --out plan.json
```
Live command shape (separate physical authorization required):
```
python3 tools/shelly_ota.py old/build new/build --live \
  --host 192.168.86.85 --device-id shellypro2-80f3dac8bfec \
  --target 1 --peers 2 --out evidence-directory
```
Use `--isolated` instead of peers only when physically isolated. An invalid image
requires `--repair-native-confirmed` after independent confirmation of native
pump state; repair writes all modules. BL2 must still match the local baseline.
Prepared script8 `P0075 write reference`, js_uart1152008N1, all other scripts
stopped/disabled and both relay outputs off are required and verified. The tool
does not reconfigure relays or persistent serial mode. It preserves prior script
source, verifies uploaded helper source, performs addressed inventory/WAIT/ENTER,
stages at most336 Base64 characters per packet, checks UID/ACKs and final image
identity after reset, restores volatile baud115200 and stops the helper.
Peers remain silent until their900-second WAIT expires; do not resume ordinary
shared-bus polling sooner. An interrupted handoff can likewise leave peers in
WAIT. Uncertain traffic stops the run. No production schedules are auto-resumed.

## Evidence and limits

Actual module images pass the legacy37-case ARM behavior suite. Native P76 tests
include pause handling, feedback, control and addressing. OTA C (not merely a
Python model) is exercised with mutation cuts and the host sender through fake
Shelly RPC; RAM flash operations are separately executed from the actual ELF.
Service code is moved32 bytes inside its slot while all other chunk binaries stay
byte-identical. The full physical dual-device OTA/timing test remains outstanding.

Real power interruption can produce flash ECC faults, which the mutation model
does not emulate. Such faults may require original bootloader/DIP recovery;
there is no A/B rollback or guaranteed unattended recovery. Hardware self-program
proof at one fixed page is supporting evidence, not proof of this whole updater.

## P0080 snapshot follow-up (revision2 Drift + Dispatcher)

Historical build used `make snapshot`, `make snapshot-test` and `make snapshot-test-arm`
(with the same PYTHON/toolchain overrides as above). The original installed
`release/` remains the comparison baseline; `release-snapshot/` is the new OTA
candidate. No live deployment is implied. Only Dispatcher and Drift differ;
BL2, layout, Common, Mode/EFFECT and all other chunks remain byte-identical.

FC04 raw400..527 is new; all previous registers retain semantics. Read400/count8
captures all20 cached telemetry records in one scheduler operation. Header:
400 magic5380hex,401 schema1,402..403 sequence32 (high word first),404 link-lost,
405 count20,406..407 zero. The snapshot is volatile, cleared at boot and otherwise
held until another read including400 replaces it. Sequence increments nonzero,
wrapping UINT32_MAX to1. Never treat a saved snapshot as a continuously fresh read.

Records408..527 follow `tools/read_mvp.py` NAMES order, six words per record:
signed value high/low (80000000hex if invalid), status, age_ms high/low, source
generation. Ages and status describe capture time. This is a consistent cache
snapshot, not simultaneous physical sensor measurement; existing skew/freshness
rules still apply. Read in blocks of at most16 words, then reread402/count2 and
reject/retry if the sequence changed. Multiple readers must coordinate captures;
a second capture invalidates the first reader's transaction. The supplied
`tools/read_snapshot.py` decoder retries at most3 times and timestamps capture.
It uses existing Modbus RPC when Shelly is in mb_client mode; in the current
js_uart maintenance configuration pass a UART FC04 read callback instead of
changing Shelly configuration. It sends no pump control or flash commands.

The update contains two4KiB slots (8192 firmware bytes) plus the manifest/protocol.
Dispatcher routing must be updated with Drift: the original dispatcher could not
reach this new range. OTA's existing manifest commit binds both chunks as one set.

### Physical OTA finding (2026-10-09)

Snapshot candidate installed successfully with session recovery after late COMMIT
ACK; snapshot1/2/3 verified. Host now allows2seconds for full-set COMMIT/EXIT
validation (delayed ACK regression added). One-shot revised host still needs a
future physical test. Protocol1 whole-manifest CRC is a fixed residue and DOES
NOT identify the installed version: do not rely on this field as exact version
proof. Module/manifest-prefix integrity checks still work. A BL2+host protocol
fix using prefix56 CRC remains pending; requires original installation path.
# Direct flow-target candidate (P0080)

Live update2026-10-10: build-direct-flow is installed and normal-operation verified on D1 and D2, prefixCRC c9d5de0b. Both56-frame mode-only transfers and peer WAIT expiry verified. The feature's target replacement remains offline-tested; no physical temperature-step test was included in installation. The candidate wording below describes the pre-install build history.

`build-direct-flow` supports next-sequence, flow-only fixed-flow target updates within an active fixed-flow session. It preserves the initial restoration snapshot, rechecks native guards and sends only the flow target. Read `applied` plus the native target; an ACK alone is insufficient. Pending updates return BUSY. Cross-mode and combined DHW changes are outside this replacement path.

Build: `python3 build.py --out build-direct-flow --change-slot bl2,drift,dispatcher,mode --revision 2`. Only mode.bin changes versus release-bl2-v2; other images including BL2 are identical. Candidate prefixCRC `c9d5de0b`, installed baseline `d9dd3c62`. OTA plan is generated with `python3 tools/ota.py release-bl2-v2 build-direct-flow --out build-direct-flow/ota-plan.json`. It updates only the12KiB mode slot in56 frames. Offline verified, not flashed. See package-run CHANGELOG and build-direct-flow/VERIFICATION.json.

## P0080 brine pump A3 extension (2026-10-10)
OCH722A service manual p30 identifies decimal018 output step0..10 and019 RPM0..9999. A3 support is a wire-mapping candidate pending physical observations, not a confirmed flow sensor. Schedule27,28,18,19 with a full FAST round between service operations; original retry ownership/limits retained. Snapshot schema1 remains20 fields: index11 step, index10 running derived ONLY from valid in-range RPM>0. ZeroRPM is valid stopped feedback, never inferred from missing data or step0. Controller feedback still needs physical correlation for the hydraulic test.
FC04 zero-based87..92 (018) and93..98 (019): retained raw, protocol-valid flag, age_seconds, last status, completion generation, ever-completed. Raw/protocol-valid do not perform engineering range checks; snapshot does. Age TTL60s, link-down invalidates all four services, no stale value becomes valid zero. Temperature and pump sources are asynchronous; a stopped test must require fresh repeated RPM samples and actual water-pump stop feedback. No new pump commands. Only drift/service chunks differ from installed direct-flow; BL2/layout/ABI/control unchanged.

Physical deployment completed on D1/D2: prefixCRC3f41636b, UID verified, normal curve power1, valid CN10526Hz, advancing snapshots/counters. Both WAIT periods expired and all four helper cleanup records verified. A3/018 D1 raw10, D2 raw16; A3/019 D1 changed3810->3780, D2 raw3810. D2 level remains range-invalid, raw retained; no guessed scaling. Firmware test passed, hydraulic circulation conclusion still pending.

## EFFECT freshness and bus refresh — 2026-10-10

Offline candidate only; no OTA or pump writes in this change. Operator explicitly requested that values younger than one minute count as fresh. Direct telemetry, compressor compatibility registers and EFFECT source/last-pair admission now accept age <60000ms; age >=60000ms is stale. A known lost link still invalidates immediately. Native control readback guards retain their independent timing; measurement freshness does not authorize stale write guards. Temperature/flow pairing still requires <=2000ms acquisition skew, distinct generations and a heating-mode observation after the pair. Short-window warmup pauses adjustments without aborting an established session; it does not permit initial EFFECT admission or a new power adjustment without qualified feedback. Lease expiry and hard invalid/DHW/zero-flow guards remain.

Integrated real CN105/sampler/controller regression reproduced the former entry failure:220ms replies, six A3 attempts, accepted1/applied0, Hz reaches10000ms during entry and BAD_FEEDBACK restores the curve. CONTROL now allows complete FAST refresh rounds between owned transactions, with proactive refresh at6s Hz age; no interruption of owned A3/CONTROL frames. Refresh completion remains owned when partial feedback suspends APPLY. RESTORE is not gated on successful GET04 refresh.

Validation: complete host ASan/UBSan suite passed, including59999/60000ms boundaries, warmup recovery, real scheduler entry with220/500ms replies and varied timing, actual adjustment, stale Hz/DHW/zero-flow/link-loss faults and restoration. Actual built ARM module/veneer/pump/direct-target tests passed. OTA C engine passed3607 mutation cuts; fake Shelly host transfer/lost ACK/identity/cleanup passed. No physical validation of this candidate yet.

Candidate: procon/modular/build-effect-refresh. Common2816/12288, mode10072/12288, drift2736/4096 bytes. Only these three chunks change versus build-brine-pump; BL2 unchanged, layout/ABI unchanged. Existing local P0080 changes preserved; no commit/push. File index unchanged because existing tracked sources/docs were updated. Generic knowhow promotion deferred pending physical validation; this is currently a project-specific scheduling correction.

## Fast demand candidate 2026-10-10
Operator authorized fast-law build, OTA and15min dual6000W trial. PrefixCRC6137dc5e, mode10736/12288 bytes; only mode slot changes from9da1db61, BL2/ABI unchanged. Cap>4000 selects fast law with command ceiling5500; <=4000 retains legacy behavior for compatibility. Actual supply>=4000 aborts/restores in fast mode;>=3800 or positive30s trend projecting3900 brakes demand. Large deficit can request55C promptly; approaching target removes boost to supply+1C,15s decisions then adjust. Measurement age>=15s cannot sustain a new55C decision; existing hard stale60s/link/lease paths still apply. Native pause promptly drops boost and keeps mild demand. The old+5C and unresponsive latches do not constrain the fast branch. Tests: native ASan/UBSan suite, real wire scheduler with55C and faults, fast-law unit boundaries/temperature/pause/aging, host encoder5500/5501, actual built ARM boost/brake,1551 C OTA mutation cuts and fake RPC sender success/lostACK/cleanup. Physical performance not claimed until new trial. Known local changes preserved; no commit/push; existing tracked paths only, index unchanged. Readback decoder now permits55C; legacy v2 command limit remains45C. Uploader uses180s peerWAIT for one-slot update and retries exact packets on malformed responses.

## Current persistent fast candidate — 2026-10-10 (supersedes intermediate fast-limit descriptions)
Candidate prefix852841df; mode11448/12288 bytes. Only mode differs from installed intermediate6137dc5e; BL2/ABI unchanged. Uninstalled intermediatebc31ad62 was superseded before the physical trial. Fast missions (cap>40C, up to55C) retain mission/snapshot/lease across stale/invalid/zero-flow feedback, naturalDHW and communication/read timeouts. They suppress increases, lower an existing boost to39.5C when native heating guards can be verified, resynchronize native readback after link recovery, and resume when feedback qualifies. Native pause no longer has20min abort in fast mode. Legacy low-cap behavior unchanged. AUTO, lease expiry and explicit external ownership/power/mode/inhibit guards remain respected; the controller never forces power-on or overrides Mitsubishi safety logic. Readback mismatch remains an explicit control fault, not treated as successful delivery.
Thermal limiting engages at38C or positive30s projection39C, clamps requested temperature39.5C and disengages below37C with forecast<38C. Actual40C does not end the mission. Measured actual temperature above40C is still a violation of the supervised test boundary, not a commanded higher ceiling. Firmware reduces demand while retaining mission; physical overshoot and native minimum power cannot be ruled out by simulation. Existing phase LIMITED/reason TEMPERATURE_CAP plus requested/instant/short/slow power expose unmet demand and current achieved output, not a calibrated maximum-capacity estimate.
Native ASan/UBSan regressions and integrated real CN105/sampler/controller recovery cases (temporary lostHz, DHW, zero flow and total link loss) passed. Actual ARM boost/brake and module ABI tests passed. OTA engine1551 mutation cuts and fake Shelly duplicate/retry/cleanup tests passed. Live installer uses120s peerWAIT for one56-frame module update and35s remaining-margin gate. No commit/push; existing tracked paths only. Package-specific recovery evidence retained; general physical response/efficiency conclusions await live trial.

### P0080 smooth capture candidate 67ff1a3e
Installed baseline852841df completed the physical dual6kW trial without mission abort, but tracking oscillated. Both units restored to curve mode. New uninstalled build-effect-smooth retains capture after startup acceleration, limits ordinary taper to2C and trim to0.5C per >=15s decision, and preserves slope across normal pending refreshes. Thermal/degraded-feedback reductions take precedence. Mode11624/12288, mode-only OTA, BL2/ABI unchanged. Host/ARM/OTA tests passed; live stability not established. Details and evidence: requirements/package-runs/P0080/implementation-report.md.

Live status2026-10-10: smooth67ff1a3e installed on both devices and completed a bounded dual6kW test. Taper and native-pause recovery observed; stable6kW tracking NOT achieved. Both restored to curve mode. Short180s leases can expire during frequent APPLY because renewal is accepted only in ACTIVE; test repeat used1800s bounded lease, no firmware renewal fix. See P0080 implementation report.


## P0080 Hz-leading EFFECT candidate982e160b — 2026-10-10

This is the latest built controller; earlier candidate sections retain historical behavior. The build is `build-effect-rocket`, with only the mode chunk changed from67ff1a3e. Mode uses11984/12288 bytes and984/4096 bytes of its RAM allocation. BL2, layout, exports and Modbus schemas are unchanged. Deployment is in progress; the native quarter-hour trial is pending at this entry.

For EFFECT with a requested-temperature cap above40C, initial demand is at most45C. The regulator then adjusts demand gradually using35s Hz change to lead the rolling heat-power estimate and60s Hz change to estimate acceleration. Demand may rise towards the configured maximum55C. Nominal updates are30s apart; ordinary changes are at most0.5C, or a downward1C when predicted power is more than1.2kW above target. Falling/flat frequency guards stop unnecessary continued braking below the target. These gains are empirical, not a proven FTC model. Caps of40C or less retain the legacy controller.

Temperature protection reduces the allowed demand progressively as actual supply rises. In centidegrees: `Tlead = supply + max(temperature_rate_per_minute,0)/6`; `thermal_cap = min(command_cap,3950 + 3*max(0,3950-Tlead))`. Actual39.5C or a30s forecast reaching40C overrides this to39.5C. The mission remains active and reports LIMITED/TEMPERATURE_CAP when constrained. This is not proof that physical overshoot is impossible; the supervised trial still stops above40C.

Fresh feedback aged15..59s holds ordinary demand instead of abruptly dropping it. Thermal protection and hard-invalid/native recovery still take priority. Same-intent next-sequence EFFECT renewal now works during an internal APPLY adjustment after the mission has been applied; it does not reset the adjustment or restoration snapshot. A repeated identical packet still cannot extend the lease. Hosts should renew in APPLY as well as ACTIVE when `applied==accepted`.

Full host ASan/UBSan tests, final-image ARM tests and1551 OTA mutation cuts passed. The preceding host-controlled pilot reached about6kW on both pumps but exposed the old abrupt thermal clamp; it does not qualify this autonomous firmware. See `requirements/package-runs/P0080/implementation-report.md` for evidence and the subsequent physical result.

## P0080 early startup and fine correction candidate 784a48ae — 2026-10-10

`build-effect-startup` is the latest candidate. It changes only the mode chunk from 982e160b; BL2, layout, exports and public register schemas remain unchanged. Mode uses 11824 / 12288 bytes (464 bytes free), with 984 / 4096 bytes of allocated RAM. Grouping private regulator state retains the existing `-Os` build and full reset behavior. OTA and physical validation are in progress at this entry; this is not a claim of improved physical tracking.

Fast EFFECT can request a thermally bounded initial 45 °C during SETTLING after the first coherent heating pair, without waiting for the complete rolling-power window. The pair must be younger than 15 s, with native heating mode 2 or 7, valid positive compressor frequency (1–254 Hz) and valid supply temperature. The initial increase is withheld when the retained power estimate is already within 150 W of the target or higher. Native write guards and target readback still apply. Startup is marked complete only after successful readback, and the same thermal ceiling is reevaluated throughout settling. Losing qualification discards an unsent adjustment; it does not interrupt readback for a write already sent.

This removes a software delay after compressor restart. It does not override a native restart pause, which may still last about 10 minutes, force compressor operation, or take control during DHW. The host regression's less-than-10-second result is measured from the first qualifying heating pair in the synthetic scheduler, not from mission start and not as a physical timing guarantee. The zero-Hz pause margin remains unchanged.

Near the power target, the quiet band is now 150 W. Signed corrections smaller than 0.1 °C accumulate until a useful command step is available. This carry resets on a sign reversal, quiet/no-correction condition, native pause, a history gap of at least 60 s, or saturation in the same direction. It is bounded fractional command carry, not an unrestricted accumulated power error. The 35 s Hz lead, 60 s acceleration estimate, configured ceiling up to 55 °C, progressive thermal protection, ordinary 15–59 s feedback hold, lease renewal and AUTO restoration retain their previous contracts.

Verification passed the complete host ASan/UBSan suite, actual final ARM image tests (including first-pair startup and repeated thermal reductions), 1551 OTA mutation cuts and fake Shelly transfer/cleanup tests. The preceding 982e160b physical trial remains the baseline; whether this candidate improves startup, power offset or sustained tracking awaits the current physical trial. See `requirements/package-runs/P0080/implementation-report.md` and `build-effect-startup/VERIFICATION.json`.

## P0080 entry-transition candidate d64080c7 — 2026-10-10

The first physical attempt with 784a48ae failed during initial mode entry on both pumps: accepted sequence 1, applied 0, control error 8 / BAD_FEEDBACK. Both returned to their original curve settings and helper cleanup was verified. It produced no sustained tracking result. This supersedes the earlier physical-validation-in-progress note for that attempt; evidence is in `P0080/effect-learning/capture-native6kw-20261010T153111Z`.

The defect was reproduced offline using the real sampler/controller: a cached READY result and newer native mode 0 within the same scheduler millisecond were misclassified as a hard feedback failure. `build-effect-entry`, prefix CRC `d64080c7`, treats an unqualified cached READY report as temporary collection in fast EFFECT only when its native mode is one the existing guards permit. Unsent work yields to polling and requires guards again; sent writes retain their readback. Original settings and the finite initial lease remain intact. Native inhibit, ownership, power and unsupported-mode guards are unchanged.

The early startup and fine-carry behavior of 784a48ae is retained. Mode is 11840 / 12288 bytes (448 bytes free), RAM 984 / 4096 bytes; only mode changes, with unchanged BL2, ABI, schemas and `-Os` build. The full host suite, 60 entry-transition combinations, real sampler/controller reproduction, actual final ARM transition tests, 1551 OTA mutation cuts and fake Shelly transfer/cleanup passed. Physical validation of d64080c7 remains pending at this entry; passing the reproduction does not establish the requested power curve.

## 2026-10-10 thermal correction after the physical boundary breach

The later physical test observed 40.5 °C actual supply on VP1 while its requested temperature remained 39.5 °C. The previous fixed protective request could not correct the persistent actual-to-requested offset. Both units were restored to their original curve state and the test helper was stopped. The new candidate therefore replaces that fixed thermal floor with continuous signed feedback around 39.0 °C.

In centidegrees, let `lead = supply + max(temperature_rate_per_minute, 0)/6` and `margin = 3900 - lead`. The candidate ceiling is `3900 + (margin > 0 ? 3*margin : margin)`. A positive 30 s forecast reaching 4000 may only reduce that result to at most 3900, never raise a lower result. The final ceiling is bounded to 3000 through the configured command cap; the lower bound prevents unsigned conversion of an extreme negative result. At flat measured supply of 39.5, 40.0 and 40.5 °C, requested ceilings are respectively 38.5, 38.0 and 37.5 °C. This is a ceiling, so it does not raise an existing lower request.

Atomic mode entry, first-pair startup and ready-feedback regulation share this helper. Cooling releases the ceiling but does not replay startup or saved upward corrections: ordinary positive changes remain at most 0.5 °C per decision. Phase LIMITED / reason TEMPERATURE_CAP continues to expose an active constraint. No new register, cross-module ABI or integral state is introduced. Native guards, lease and restoration semantics remain unchanged. The measured 40 °C trial boundary is unchanged; this empirical correction still requires physical validation and does not guarantee zero overshoot.

### Physical status after e8fc6d86 trial — 2026-10-10

Both units run e8fc6d86. A30-minute dual6kW-request trial completed with observed maxima39.5/39.0C, no poststart compressor stops and verified AUTO/curve restoration. Initial entry and thermal protection improved, but sustained6kW tracking is not qualified: last5-minute means were4.741/4.557kW and VP1 recovered slowly after thermal headroom returned. See the final dated section in `requirements/package-runs/P0080/implementation-report.md`; do not interpret temperature limiting as proof that all power deficit is physically unavoidable.

### Uninstalled response-memory candidate7adaecf1

Offline-qualified P0080 follow-up retains a bounded, decaying acceleration forecast over short frequency plateaus and strengthens low-demand recovery after limiting. Positive steps may reach1C only with measured and predicted deficit>750W and requested-minus-actual<2C; otherwise0.5C. The thermal envelope remains unchanged and applies last. Full host/ARM/OTA tests pass, but no new physical performance is claimed. Devices remain on e8fc6d86. See the dated implementation-report section and `procon/modular/build-effect-response/VERIFICATION.json`.


### Installed response-memory controller 7adaecf1 — 2026-10-10

Explicitly authorized OTA installation completed on D1/VP1 and D2/VP2. Evidence: `P0080/effect-learning/update-response-20261010T200545Z` (outcome verified_both=true; all four helper cleanup checks passed). Only mode slot 2 changed; BL2 and other modules were preserved. Known device UIDs and manifest prefix 7adaecf1 were verified on both, with advancing CN105 reply counters and snapshots. Both remain power on, native curve mode 2, flow target 3050, DHW target 5200, boost off, and control IDLE/error 0/saved 0. Final compressor readings were 20 Hz and 22 Hz. No heating-control trial or setpoint changes were performed during installation. Effect-control tracking improvements remain physically unvalidated; prior offline test results still apply. The generic live trial identity gate now expects 7adaecf1.


## P0081 asynchronous diagnostic candidate

Candidate71b30837 adds isolated FC16/600 submission and FC04/600..631 sticky raw results. See [RAW_API.md](RAW_API.md). Only Common/Dispatcher change; BL2/layout/mode preserved. Offline host/ARM/2065 OTA-cut tests pass. Source published in standalone Procon commit7f7ca23285c5f5c4ca5c1a4d9cb84549f14dfc1d; physical activation and mapping pending. Existing installed units remain7adaecf1 until explicit activation.

P0081 physical mapping completed: 720/720 observations and final native curve verified on both pumps. See [the package report](../../requirements/package-runs/P0081/implementation-report.md) and [sanitized code map](../../requirements/package-runs/P0081/command-map.md).


### P0080 A3 frequency comparison

Input372..377 (service16, manual actual frequency) and378..383 (service17, manual target frequency) each contain six words: retained raw little-endian payload value; valid; completed-reply age in seconds; last wire status; successful completion generation; ever completed. Never-read raw is65535 and must be qualified by ever/valid. New completion does not prove new source-board acquisition. Normal GET04 remains unchanged. Service queue27,28,18,19,16,17 owns each entire retry operation, with a full FAST round between operations. No diagnostic injection during active control is required. Status1/2 retain the existing raw decoder; live scale/correlation must be established.

The earlier dense A3 experiment selected16,17,16,17 then one rotating background code. The current target-focused experiment instead selects17 for every service operation when the controller is ACTIVE, mode fixed-flow and applied target6000. It preserves the ordinary six-code queue cursor and resumes that queue outside this condition. FAST temperature/status polling still occurs between complete service operations; retry cadence/bounds are unchanged. A3/16 and background A3 records may expire while the experiment runs, retaining honest60s validity. No priority in EFFECT or curve mode.


### P0080 focused diagnostic cadence (2026-10-12)
Queued read diagnostics can take a not-yet-started Service operation after its complete eight-query FAST refresh. Each A3 retry sequence stays exclusive and bounded; no cadence/timeout/control-admission changes. The existing mailbox still requires controller IDLE, so this focused host-driven read mode is qualified in AUTO/curve and is not enabled during an active fixed-flow/EFFECT mission. Stop submitting and the ordinary service queue resumes automatically. Ordinary background A3 values can expire while diagnostics are prioritized; their TTL/status remains truthful. No extra persistent configuration or ABI field. Repeated same-selector results must show valid pending-to-completion rearm evidence before being counted as new jobs.

Live qualification on VP2 (`5fc25d43`) completed24 jobs in180s: mean7.583s,
median7.471s, approximately7.9 completed jobs/min. Every operation had valid
pending→completion; all returned20Hz. Primary telemetry continued updating and
the ordinary service queue recovered after stopping submissions. This is an
IDLE/curve-mode diagnostic result, separate from the later fixed60 Service profile.
See the2026-10-12 focused-cadence entry in the P0080 changelog.


### P0080 moving-delta experiment candidate — 2026-10-12

`build-delta-sweep-vp2` temporarily extends manual v2 FLOW/readback to65C for
actual+5/+10/+15/+20C trials stopping at45C actual. DHW60C and EFFECT55C bounds
are unchanged. Its Service selects A3/17 during ACTIVE fixed-flow at any target
or ACTIVE OFF cooling; AUTO/IDLE/EFFECT retain ordinary services. Each operation
keeps its selector through retries and complete FAST rounds separate jobs.
Direct retargets preserve original settings and require native readback; they
consume transport time, so8 A3 completions/min is an aim, not a guarantee.
All applied deltas and command timings are logged. The prior modules/profile
are to be restored after the bounded four-series experiment. Native65C
representation is supported by static evidence but installedFTC acceptance
requires live verification. See P0080 changelog for installed state/results.


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

### Two-loop EFFECT candidate — 2026-10-13

`make effect-two-loop TOOLCHAIN=...` builds the replacement controller in the
unchanged12KiB Mode slot (11936bytes,352bytes free). Outer affine heat-power
model starts at135W/Hz and-1090W; inner demand follows A3/17. Stable qualified
A3/16/power windows update the offset slowly, and repeated comparable separated
plateaus may update slope. Coefficients remain in RAM across missions only.
Thermal priority remains40C actual with gentle target reductions;55C is the
separate requested-temperature ceiling. No native protections are disabled.

Direct ACTIVE EFFECT target changes preserve the original restoration snapshot.
Input300–319 exposes validity/age/generation, model, goal and hold state through
the existing controller route, including old Common builds. Holding300–307
commands are unchanged. Read CONTROL_API.md for scaling and validity rules.
Host/ARM qualification covers thermal priority during oscillation hold, stale
source behavior, direct target replacement and restored originals. Physical
trial outcomes are recorded in the P0080 changelog; a passing synthetic test
is not proof of physical stability.

## Installed braking follow-up — 2026-10-14

Both installed images now use Mode-only qualified negative-delta braking: VP1 manifest0f48da4e, VP2a5a6dc0c. Release: `release-effect-braking-20261014`. Four-quarter2/4/6/4kW trial completed; both restored curve. Tracking is partial, especially2kW and temperature-limited6kW. See `../../../requirements/package-runs/P0080/dual-quarters-report-2026-10-14.md` (repository-relative report path is requirements/package-runs/P0080). Do not treat successful OTA as proof of full tracking.

## EFFECT + pair-energy v2 offline candidate — 2026-10-14

The final EFFECT build moves its RAM-only affine model into Service to keep Mode
inside its fixed 12 KiB slot. Mode calls private Service veneers at
`0x08012069`/`0x0801206d`; these are deliberately absent from the public export
ABI. Consequently **Mode and Service must always be OTA-staged and committed
together**. Final use is 11,928/12,288 bytes and 2,728/4,096 bytes respectively.
The device compositions are not interchangeable:

- VP1: installed `9580f1d1`, candidate `4bf657aa`;
- VP2: installed `3f6ef793`, candidate `e11851e8`.

Only those two chunks differ. BL2 and all other chunks remain the installed
device-specific bytes. `tools/compose_effect_energy.py` performs this offline
composition and rejects a layout, BL2 or unexpected-slot mismatch.

EFFECT now uses coherent telemetry until age 60 seconds. Ages below 15 seconds
permit fast correction; 15--59 seconds permit conservative best effort without
an aggressive increase. Diagnostics distinguish minimum output, request cap,
temperature limiting and stale source. Actual-supply priority is 45 C;
requested flow can be capped independently up to 55 C. Thermal braking is
limited to 1 C/30 s and ordinary downward control remains gentler.

`shelly/energy_pair_v1.js` version 1.4.2 executes a scalar current+next
cumulative-deadline plan. It applies response-lag, asymmetric ramp and learned
capability bounds, holds normal targets for 120 seconds, splits every 500 W pair
request exactly, and redistributes within fresh per-device caps. Missing or
>=60-second feedback holds/renews the exact accepted pair, records the interval
as unknown and replans on the first complete fresh pair. A falling command or
active thermal limiter now lowers the energy credited inside the response-lag
window. An output collapse larger than the normal ramp may bypass the remaining
dwell once with a 1 kW recovery step; a separate 120-second cooldown prevents
repeated target chasing. It is not the offline full four-quarter MPC.

All statements above describe an offline candidate. Host, ARM, FC04 mailbox and
mock OTA qualification do not constitute a live firmware or Shelly trial.
