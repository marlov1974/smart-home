# P0072 r2 — supervised control candidate

This revision implements commands; it is **not yet hardware-validated**. P0072 r1 was read-only. P0074 documented that read-only profile and does not establish control safety. No live writes or physical flash were performed while building r2. User alone flashes.

Reference: F1p EcodanDecoder.cpp/.h at7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5: TYPE41, basic32 flag01 power,08 Zone1 mode,20 DHW target,80 Zone1 flow; controller34 flag01 forced DHW. GET26 power/mode/DHW target,GET09 flow target,GET28 boost and native prohibit/holiday/server flags. Independently encoded protocol facts; no raw SET tunnel, pump override, zone2 modification or safety/prohibit bypass. Temperature limits below are our conservative command bounds, not vendor certification.

## Atomic command

Only Modbus FC16 at zero-based holding offset300,count8,bytecount16 (25byte RTU request) is writable. FC06/other addresses/broadcasts cannot command anything. FC16 response echoes address/count: it means accepted into RAM, not applied to the heat pump. FC04 input addresses0–255 stay compatible; new diagnostics256–282; reserved through319 read0. No FC03 holding reads.

|Word|Meaning|
|---|---|
|0|0xC072 magic|
|1|Sequence1–65535; first1 afterboot, thereafter exact next,65535→1|
|2|0 OFF;1 AUTO/restore saved session;2 FIXED_FLOW;3 DHW boost;4 TARGETS only|
|3|Flow target centidegrees20–45C if flag1,otherwise0|
|4|DHW target centidegrees40–60C if flag2,otherwise0|
|5|Lease30–1800seconds;AUTO requires0|
|6|Flags bit0 flow,bit1 DHW; others rejected|
|7|Envelope version2|

FIXED_FLOW requires flow flag;TARGETS requires at least oneflag;OFF/DHW reject flow flag. AUTO requires zero targets,flags,lease. Unused words must be0. Exact duplicate sequence+allwords is idempotent and **does not renew** lease. The next sequence with identical mode/targets/flags while ACTIVE renews lease without additional SETs. Different intent is rejected busy until AUTO restores; one session at a time. Invalid values/sequence yield Modbus exception03; busy/no saved session yields06; wrong writable range02. Error diagnostics do not by themselves alter an active lease.

Generate bytes without sending: `python3 procon/tools/control_command.py --sequence 1 --mode fixed-flow --flow 38 --lease 900`. AUTO: same tool with next sequence and `--mode auto`. The helper is deliberately offline; a verified Modbus master must transmit the atomic envelope. Do not type vendor H28/H32 addresses into this replacement API.

## Preconditions, changes and acknowledgement

At next completed A3-operation boundary read GET26,09,28. Snapshot original power,Zone1 mode,reported flow target,DHW target and boost before any SET. Reject power not0/1,mode outside0–2,cooling/dry-up,targets outside conservative ranges,holiday/server/prohibit flags or malformed replies. Waiting for that boundary can take a full bounded service operation. Normal Modbus reads remain available.

Apply one dimension then read it back. FIXED_FLOW sets mode1 (when needed),flow target,then power1 (when needed). DHW sets boost1 and power1, with optional DHW target. OFF sets power0. TARGETS alters only selected targets and does not explicitly request power/mode. Native priority/anti-cycling/protection may delay actual heating; verified settings do not prove compressor start or delivered temperature.

SET61 is only an acknowledgement hint; the reference accepts it without decoding status. Our command is applied only after matching fresh GET readback equals each requested setting. Missing SET acknowledgement still leads to readback because the write may have applied. Wait1s before readback after a SET and between mismatches; at most3readback attempts. Wrong type/echo never consumes the transaction. Flow SET also includes current DHW target and current mode, as required by the reference encoder; re-read GET26 immediately before every flow SET to avoid using a long-lived cached DHW value. This does not make the controller atomic against another user's simultaneous changes.

A3 retains whole-operation exclusivity. No SET,readback or reconnect is inserted between its pending retries. Control transactions form a bounded sequence outside that interval; FAST/A3 resume when the command reaches ACTIVE or restoration completes. Heat-pump responses and watchdog/Modbus are serviced throughout.

## Lease and restoration

Lease begins at acceptance, includes setup, uses uint32 wrap-safe elapsed time. When expired, wait for current wire transaction and bounded A3 operation, then restore touched settings from the original snapshot. Do not interpret900seconds as a guaranteed exact physical stop time. Explicit AUTO also restores this session's original settings; it does **not** blindly choose native mode2 or turn the system on. AUTO without a saved session is rejected.

Restore flow target first while the changed fixed mode still applies,then DHW/boost/power as touched,then original mode last. Original flow is the reported target, which under a curve may differ from a hidden stored fixed-flow target; restoration of undocumented hidden state is not claimed. The original snapshot is retained across renewal and failed commands. Mark fields touched before transmitting SET, so lost acknowledgement cannot skip rollback. Readback mismatch/timeouts after changes enter restoration. Failed restoration retains snapshot, reports blocked and retries the bounded plan after5s; no success is reported until matching readback. Link loss can prevent restoration indefinitely; operator intervention is then required.

**Power loss, MCU reset and reflashing erase the RAM snapshot/lease.** Startup is read-only; it sends no guessed AUTO command and cannot promise to undo a persistent Mitsubishi setting. Original settings must be retained outside the device by the operator/controller before a supervised test. Register282=0 explicitly advertises no persistent recovery. Do not deploy this as an unattended controller or claim reboot-safe fallback. A separately validated persistent journal/native timeout/host recovery design is still needed.

Restoration can overwrite someone else's concurrent adjustment to fields this session touched. Avoid simultaneous manual/other-controller changes during a test; use explicit cancellation/restore before handing control back. Brine pump writes remain unavailable.

## Read-only diagnostics

Identity inputs0/1 remain888/72;68=2,69=1 (telemetry API),70=3 (telemetry+experimental control),71=current control state. Input71 semantics differ from r1 unavailable4; use revision first.

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
