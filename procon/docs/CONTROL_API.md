# P0072 r3 — supervised control candidate

Revision 3 corrects the operation gate and adds passive GET28 diagnostics. Commands were introduced in revision 2; it is **not yet hardware-validated**. P0072 r1 was read-only. P0074 documented that read-only profile and does not establish control safety. No live writes or physical flash were performed while building r2. User alone flashes.

Reference: F1p EcodanDecoder.cpp/.h at7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5: TYPE41, basic32 flag01 power,08 Zone1 mode,20 DHW target,80 Zone1 flow; controller34 flag01 forced DHW. GET26 power/mode/DHW target,GET09 flow target,GET28 boost and native prohibit/holiday/server flags. Independently encoded protocol facts; no raw SET tunnel, pump override, zone2 modification or safety/prohibit bypass. Temperature limits below are our conservative command bounds, not vendor certification.

## Atomic command

Only Modbus FC16 at zero-based holding offset300,count8,bytecount16 (25byte RTU request) is writable. FC06/other addresses/broadcasts cannot command anything. FC16 response echoes address/count: it means accepted into RAM, not applied to the heat pump. FC04 input addresses0–255 stay compatible; new diagnostics256–282; new GET28 diagnostics283–298; reserved299–319 read0. No FC03 holding reads.

|Word|Meaning|
|---|---|
|0|0xC072 magic|
|1|Sequence1–65535; first1 afterboot, thereafter exact next,65535→1|
|2|0 OFF;1 AUTO/restore saved session;2 FIXED_FLOW;3 DHW boost;4 TARGETS only|
|3|Flow target centidegrees20–60C if flag1,otherwise0|
|4|DHW target centidegrees40–60C if flag2,otherwise0|
|5|Lease30–1800seconds;AUTO requires0|
|6|Flags bit0 flow,bit1 DHW; others rejected|
|7|Envelope version2|

FIXED_FLOW requires flow flag;TARGETS requires at least oneflag;OFF/DHW reject flow flag. AUTO requires zero targets,flags,lease. Unused words must be0. Exact duplicate sequence+allwords is idempotent and **does not renew** lease. The next sequence with identical mode/targets/flags while ACTIVE renews lease without additional SETs. Different intent is rejected busy until AUTO restores; one session at a time. Invalid values/sequence yield Modbus exception03; busy/no saved session yields06; wrong writable range02. Error diagnostics do not by themselves alter an active lease.

Generate bytes without sending: `python3 procon/tools/control_command.py --sequence 1 --mode fixed-flow --flow 38 --lease 900`. AUTO: same tool with next sequence and `--mode auto`. The helper is deliberately offline; a verified Modbus master must transmit the atomic envelope. Do not type vendor H28/H32 addresses into this replacement API.

## Preconditions, changes and acknowledgement

At next completed A3-operation boundary read GET26,09,28. Snapshot original power,Zone1 mode,reported flow target,DHW target and boost before any SET. Reject power not0/1,mode outside0–2,cooling/dry-up,targets outside conservative ranges,malformed replies or blocking GET28 flags according to the table below. Waiting for that boundary can take a full bounded service operation. Normal Modbus reads remain available.

Apply one dimension then read it back. FIXED_FLOW sets mode1 (when needed),flow target,then power1 (when needed). DHW sets boost1 and power1, with optional DHW target. OFF sets power0. TARGETS alters only selected targets and does not explicitly request power/mode. Native priority/anti-cycling/protection may delay actual heating; verified settings do not prove compressor start or delivered temperature.

SET61 is only an acknowledgement hint; the reference accepts it without decoding status. Our command is applied only after matching fresh GET readback equals each requested setting. Missing SET acknowledgement still leads to readback because the write may have applied. Wait1s before readback after a SET and between mismatches; at most3readback attempts. Wrong type/echo never consumes the transaction. Flow SET also includes current DHW target and current mode, as required by the reference encoder; re-read GET26 immediately before every flow SET to avoid using a long-lived cached DHW value. This does not make the controller atomic against another user's simultaneous changes.

A3 retains whole-operation exclusivity. No SET,readback or reconnect is inserted between its pending retries. Control transactions form a bounded sequence outside that interval; FAST/A3 resume when the command reaches ACTIVE or restoration completes. Heat-pump responses and watchdog/Modbus are serviced throughout.

## Revision 3 precondition gate

The first r2 live command was rejected before SET because at least one GET28 byte4–10 was nonzero. The exact byte was not exposed, so the site-specific cause remains unconfirmed. Revision 3 fixes the overbroad gate; it does not clear Mitsubishi flags or guarantee an active heating prohibition can be passed.

|GET28 payload byte|Meaning|Blocks a new session when nonzero|
|---|---|---|
|4|Holiday|Always|
|5|DHW prohibit|DHW boost or any selected DHW target|
|6|Zone1 heating prohibit|FIXED_FLOW or any selected flow target|
|7|Zone1 cooling prohibit|Not relevant to these heating/DHW commands|
|8/9|Zone2 heating/cooling prohibit|Not relevant to these Zone1/DHW commands|
|10|Server control|Always|

Values outside0/1 in any of these bytes still reject, including unrelated flags. Existing boost/power/mode/temperature checks remain. OFF retains global holiday/server checks; AUTO restoration remains available under the existing session rules. No new SET masks or writes to holiday/prohibit/server fields are introduced. Native Mitsubishi protections remain effective and can prevent actual heating even after configuration readback succeeds.

## Lease and restoration

Lease begins at acceptance, includes setup, uses uint32 wrap-safe elapsed time. When expired, wait for current wire transaction and bounded A3 operation, then restore touched settings from the original snapshot. Do not interpret900seconds as a guaranteed exact physical stop time. Explicit AUTO also restores this session's original settings; it does **not** blindly choose native mode2 or turn the system on. AUTO without a saved session is rejected.

Restore flow target first while the changed fixed mode still applies,then DHW/boost/power as touched,then original mode last. Original flow is the reported target, which under a curve may differ from a hidden stored fixed-flow target; restoration of undocumented hidden state is not claimed. The original snapshot is retained across renewal and failed commands. Mark fields touched before transmitting SET, so lost acknowledgement cannot skip rollback. Readback mismatch/timeouts after changes enter restoration. Failed restoration retains snapshot, reports blocked and retries the bounded plan after5s; no success is reported until matching readback. Link loss can prevent restoration indefinitely; operator intervention is then required.

**Power loss, MCU reset and reflashing erase the RAM snapshot/lease.** Startup is read-only; it sends no guessed AUTO command and cannot promise to undo a persistent Mitsubishi setting. Original settings must be retained outside the device by the operator/controller before a supervised test. Register282=0 explicitly advertises no persistent recovery. Do not deploy this as an unattended controller or claim reboot-safe fallback. A separately validated persistent journal/native timeout/host recovery design is still needed.

Restoration can overwrite someone else's concurrent adjustment to fields this session touched. Avoid simultaneous manual/other-controller changes during a test; use explicit cancellation/restore before handing control back. Brine pump writes remain unavailable.

## Read-only diagnostics

Identity inputs0/1 remain888/72;68=3,69=1 (telemetry API),70=3 (telemetry+experimental control),71=current control state. Input71 semantics differ from r1 unavailable4; use revision first.

|Input|Meaning|
|---|---|
|256|0IDLE,1QUEUED,2SNAPSHOT,3APPLY,4ACTIVE,5RESTORE,6RESTORE_BLOCKED|
|257/258/259|Last accepted/applied/rejected sequence|
|260|Last error:0none,1validation/sequence,2busy,3invalidnative snapshot/readback,4read timeout,5mismatch,7leaseexpired|
|261/262|Saved snapshot valid / touched bits:POWERbit1,MODEbit2,FLOWbit3,DHWbit4,BOOSTbit5|
|263/264|Accepted mode / remaining lease seconds rounded up|
|265/266/267|SET ack hints / matched readbacks / completed restorations, uint16wrapping|
|268–272|Original power,mode,flow_cC,DHW_cC,boost; valid only when261=1|
|273–277|Last control-readback power,mode,flow,DHW,boost; not continuous telemetry|
|278–281|Action index,count,phase(0SET,1verify,2flow-preservation preflight),retrycount|
|282|0:no persistent reset/power-loss recovery|

Applied sequence is historical; consultstate/error/lease too. AUTO applied sequence advances only after full restoration. Lease expiry/rollback may leave the last applied request in258; IDLE+snapshot0+restoration count establishes restoration. A Modbus accepted write, a61packet or unchanged stale value alone never means applied.

## Hardware validation after flash

First read identity/telemetry/error counters and prove new A3 completions. Capture original settings externally. Begin with a short supervised conservative command; inspect snapshot,accepted sequence,ack/readback/state and effective settings. Verify AUTO and then a short lease-expiry restoration before the requested15-minute38C experiment. Maximum3hardwaredebug attempts before reassessment. No pump overrides, fault resets, DIP/service-setting writes or forced bypass of native protections.

## Revision 3 passive GET28 diagnostics

GET28 is now the eighth FAST query:04/0C/14/0B/09/15/26/28, followed by the complete A3 operation. No extra GET is inserted among A3 retries. Previous raw200–255 addresses remain unchanged. All addresses below are read-only FC04 zero-based input offsets; read283–298 as one16-register block.

|Input|Meaning|
|---|---|
|283|GET28 received at least once since boot (not a freshness guarantee)|
|284|Age seconds, saturating65535;65535 before first sample|
|285|Sample generation, wrapping uint16|
|286|Last rejected GET28 blocking mask, bit number equals payload byte offset|
|287|Relevance mask evaluated for the most recent new-session snapshot|
|288–295|Last complete GET28 payload, two little-endian bytes per register|
|296|0x28 for last GET28 flag rejection, otherwise0|
|297/298|First rejected byte offset/value;0 when no GET28 flag rejection|

Relevant-mask bits4 and10 are always selected; bit6 for flow/heating, bit5 for DHW. Blocking-mask can also contain irrelevant bits when their encoding exceeds1. Masks/rejection persist through passive polling, so they may refer to an older command than the raw bytes; next accepted new session clears them before its snapshot. Invalid boost/range or timeout failures still use error260 and can have zero GET28 mask. Raw payload may be stale or never received: consult283/284. Passive reads permit diagnosis without submitting a control command. Helper `read_mvp.py` accepts r1/r2/r3, preserves `control_words_256_282`, and adds `controller_diagnostics` for r3.

## P0080 two-loop EFFECT — 2026-10-13

Input308–319 is a new diagnostic block (raw zero-based addresses):

| Address | Meaning | Unit |
|---|---|---|
|308|Two-loop diagnostic version|4|
|309|Current compressor-frequency goal|Hz ×100|
|310|Adaptive slope `a`|W/Hz ×10|
|311–312|Adaptive offset `b`, signed32, high word first|W|
|313|Accepted offset-learning windows|wrapping uint16 count|
|314|Accepted slope updates|wrapping uint16 count|
|315|bit0 thermal limit; bit1 oscillation hold; bit2 ramp up; bit3 ramp down; bit4 waiting for native response; bit5 observed minimum output; bit6 requested-temperature ceiling; bit7 tracking|bits|
|316|Remaining oscillation hold|seconds|
|317|Retained A3/16 raw actual frequency|Hz; quality is mirrored at300–303|
|318|Retained A3/17 raw desired frequency|Hz; quality is mirrored at304–307|
|319|Power-error frequency trim, signed16|Hz ×100|

The outer model starts with `P_W=135*Hz-1090`, independently on each device.
This is an empirical initialization, not a calibrated universal conversion.
The inner controller uses A3/17, while learning uses A3/16. GET04 remains a
separate freshness/running check. Reads are not an atomic snapshot; retain
A3 validity, age and generation when interpreting317/318.

A new EFFECT packet with a different watt target can replace an ACTIVE,
fully applied EFFECT mission directly. It preserves the first native snapshot
and learned model, changes the frequency goal, preserves the bounded per-device
trim, and renews the finite lease.  Retargeting alone does not break a model
window: any resulting change in actual frequency, water temperature or flow is
rejected by the existing physical-stability gates.  A qualified coefficient
window still needs120 seconds of stable observations.  An in-flight transaction
remains BUSY for changed intent;
identical-intent renewal retains its existing behavior. AUTO still restores
the original native settings. Model coefficients survive mission boundaries
in RAM. Version 4 can explicitly seed gain after reboot; offset, trim and the
seed itself still reset on reboot. Firmware writes none of them to flash/EEPROM.

Input300–303 contains A3/16 validity, age(seconds), completion generation and
ever-seen. Input304–307 contains the same fields for A3/17. These FC04 input
registers are separate from the FC16 command at holding300–307. They route
through Mode even when an older Common does not route372–383 to Service.
Use these mirrors with317/318 on both devices. Input350 keeps its original
nonpersistent-recovery flag1; only308 is the two-loop version field.

Version3 adds reversible capability states without changing the command or
diagnostic addresses.  Phase4 (`LIMITED`) with reason4 means the actual-supply
envelope currently has priority; reason16 means the requested-temperature cap
is reached while more compressor frequency is requested; reason17 means the
observed low-frequency boundary still overproduces.  Phase2 (`CAPTURE`) with
reason15 is the bounded native-response wait, and reason18 means source samples
are too old to authorize an increase.  These are current observations, not
latched aborts.  A later fresh sample with headroom returns to tracking.  While
thermally or request-cap limited, positive frequency trim is frozen so an
unreachable power request cannot wind the learned goal upward.  Invalid A3/17
status clears direction/tracking bits instead of presenting zero Hz as a real
actuator state.

The v3 inner loop binds each verified flow-temperature change to the current
A3/17 target and waits up to one native minute before stacking another change
in the same direction when that target has not moved.  Far above the goal,
downward authority is1C per60 seconds; near it,0.5C per60 seconds.  Thermal
priority may reduce1C per30 seconds.  A supervisor-requested reversal clears
the oscillation candidate, while same-direction response memory is retained.
None of these paths commands OFF or changes lease, restoration or native-safety
handling.


Two-loop production refinement (2026-10-13): initial demand is supply plus
10/5/3/2C according to distance to the inverse-model Hz goal. At the goal,
excess delta above2C tapers by0.5C per qualified decision, unless native target
is falling. Transient asynchronous power/skew readings are skipped for model
learning rather than erasing a valid plateau. Only fresh coherent samples
contribute; genuine invalid/link states and60s gaps still interrupt learning.
This does not establish that arbitrary power downsteps can avoid native stops.

### Slow-approach refinement — 2026-10-13

When more than3Hz below the model goal, slow native progress does not repeatedly reduce gas. A fresh independent A3/17 target unchanged for90s permits a0.5C increment, with another full observation interval before repeating. Thermal limiting, oscillation hold and stale raw telemetry inhibit increases. The positive supply+0.5C floor remains: the final physical6→5kW trial exposed insufficient downward authority near zero temperature delta. This is a known control limitation, not a qualified5kW tracking result. See the P0080 dated two-loop report.

### Qualified braking update — 2026-10-14

Supersedes the preceding positive-floor limitation: fresh water and independent A3/17 permit actual−1C above the Hz goal by more than6Hz, actual−0.5C above by more than3Hz. Near goal or at/below25Hz ordinary braking releases in bounded0.5C increases toward actual+0.5C. Native declining Hz suppresses further ordinary cuts. Every decrease is limited to0.5C and spaced at least60s from the last verified adjustment. Thermal priority may brake to actual−1C independently of the power goal. Invalid/stale source data cannot authorize this negative ordinary envelope. The supported requested-temperature lower bound is20C instead of the old artificial30C running floor. Native pause/restart and restoration remain unchanged. These limits reduce observed pause risk; they do not promise uninterrupted minimum-output operation.

### Requested45C policy — offline candidate2026-10-14

Default actual-supply priority is now45C in source (`EFFECT_SUPPLY_LIMIT_CC`), requested ceiling remains55C. Existing thermal approach and release thresholds derive from this policy (44C approach,43C release with43.5C forecast). This threshold-only candidate does not fix the known thermal-latch inhibition of power corrections. Installed units remain0f48da4e/a5a6dc0c with40C policy until a subsequent OTA. Native safeties unchanged;45C is a regulation goal, not a new emergency-off threshold.

## 2026-10-14: continuous envelope / faster upward response (installed)
Actual supply regulation priority is45C, requested-flow ceiling55C. The current thermal forecast and actuator ceiling replace the90s cooling latch; no cooling-to43C prerequisite remains. The Hz controller continues underneath the thermal envelope, including negative power correction. Positive goal trim is inhibited when constrained; negative correction is allowed. Temperature priority still overrides the power goal and does not commandOFF.

After independent fresh A3/17 feedback, upward slew is at most2C/decision when more than10Hz short,1C when more than6Hz short, otherwise0.5C. Decisions remain at least30s apart; this is a ceiling, not a compulsory boost. Initial demand selection and unchanged-target90s nudge remain. Downward slew remains0.5C per60s. Ordinary braking can reach actual-0.5C/-1C above20Hz; it releases at20Hz or early below24Hz when the observed target is falling. This replaces the fixed25Hz guard.20Hz is an observed operating point, not a universal minimum guarantee.

ABI,12KiB Mode slot, leases, restoration, telemetry freshness and native protections are unchanged. Only Mode was included in device-specific OTA compositions. VP1 manifest is `9580f1d1`; VP2 is `3f6ef793`.

The supervised90-minute 2/4/6/4/2/6kW-per-pump trial completed with verified restoration. Maximum sampled actual supply was43C, maximum request47.5C, and no thermal-limited sample occurred. Six-to-four and four-to-two down-ramps remained slow and unequal; the final low-to-six transition gained only about0.6–0.8kW per pump in five minutes. Two kW was below the observed stable continuous range. Treat ramps as delayed steps and integrate measured pair energy. Full findings are in `requirements/package-runs/P0080/dual-six-quarters-report-2026-10-14.md`.

## Combined EFFECT/energy v2 offline API — 2026-10-14

The command envelope is unchanged: holding 300--307 carries the version-3
EFFECT request and input 300 onward reports controller diagnostics. The final
candidate keeps the public register/layout ABI, but its private implementation
spans Mode and Service. Those chunks must be updated together; neither mixed
version is supported.

Input 308 reports diagnostic version 4. Input 315 retains the existing bits and
reports response wait, minimum output, request cap and tracking. Input 321/322
reports phase/reason, including temperature cap, request cap, minimum output and
stale source. Input 325--336 retains signed 32-bit power/error plus quality,
readiness, pair count and age. Shelly 1.4.1 reads 321--336 in one FC04 request;
the returned words are one non-atomic diagnostic snapshot and remain subject to
their validity/age fields.

Telemetry age <60 seconds is usable by EFFECT. Only <15 seconds authorizes its
quick response; 15--59 seconds yields conservative best effort. The actual
supply priority is 45 C and the independent requested-flow cap remains at most
55 C. Thermal braking is bounded to 1 C/30 s; ordinary reduction is slower.
Reaching a limiter is reported and regulation continues best effort rather than
aborting the mission.

The Shelly 1.4.1 energy executor preserves the existing 180-second lease and
version-3 command. Normal target changes dwell 120 seconds; an active limiter
may lower a target immediately. Missing/stale pair feedback causes no target
change: the exact last target is renewed after 55 seconds, its interval is
reported unknown, and a fresh complete pair triggers immediate replanning. It
uses current+next cumulative deadlines, not a full four-quarter MPC.

These semantics are source/host/ARM qualified only. The combined firmware and
Shelly 1.4.1 have not been installed or physically qualified.

## Version 4 RAM-only gain export/import

Version 4 adds a second, mutually exclusive envelope at the existing atomic
FC16 holding offset 300, count 8 and byte count 16. It imports only the
long-term model gain `a`; the heating envelopes above are unchanged.

|Word|Gain-seed value|
|---:|---|
|0|`0xC077`: schema/operation magic for gain import|
|1|Gain `a`, 700--2000 W/Hz x10|
|2--7|Exact factory UID input words 78--83, in that order|

The complete 96-bit factory UID is carried without hashing or truncation. This
catches a seed addressed to the wrong commissioned Procon; it is not an
authentication mechanism. Modbus unit address, factory-identity validity and
RTU CRC retain their existing checks.

Only the first valid seed is accepted during a boot. An exact repeat of that
same packet is idempotent even while the bus is temporarily busy. Another gain
or a UID mismatch returns exception 3 and cannot replace the accepted seed
until reboot. A valid first seed outside the quiescent gate returns exception
6. There is deliberately no wire sequence: a KVS generation/sequence is host
metadata and is never trusted by this firmware boundary.

The quiescent gate is the existing `maintenance_ready()` boundary: controller
IDLE with no saved session, no active CN105/control/diagnostic owner, a current
link, recent GET26/GET28, native curve mode 2, and no active holiday/server,
zone-1 heating or DHW prohibition. It does not send a CN105 command. Acceptance
changes gain only and discards any partial learning window. It preserves the
current RAM offset, offset/slope counters and EFFECT trim.

Read input 310 to export the current gain and input 346 for the seed-accepted
flag (0/1). Input 308 is 4 when this contract exists. Inputs 311--314 and 319
remain offset/counters/trim and allow the host to verify that a seed did not
import them. On reset input 310 is the deterministic fallback 1350, input 346
is 0, offset is -1090 W and trim is 0. Inputs 350/351 continue to advertise
unknown reboot recovery/no persistent recovery. There are no EEPROM,
option-byte or application-flash writes in this path.

The intended host flow is: read and verify UID 78--83; wait for
`maintenance_ready`/IDLE; read 308/310/346; retrieve a UID-keyed, validated
gain from external storage; send one C077 envelope; then read back 310 and 346.
Qualification and write-rate policy belong to the host. This firmware change
does not add Shelly KVS persistence by itself.
