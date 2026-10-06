# P0071 service27/28 protocol and register map

Status: software-verified candidate; hardware brine decoding pending. P0070 compressor20Hz remains the latest physically confirmed firmware observation. Do not reuse historical patched scheduler implementation.

## Evidence and interpretation

Pinned reference [F1p7687d11](https://github.com/F1p/Home-Assistant-Mitsubishi-CN105-to-MQTT/tree/7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5): Ecodan.cpp WriteServiceCodeCMD emits GET/A3 with service number in payload1/2 (big-endian). EcodanDecoder.cpp Process0xA3 accepts payload3 status1/2, leaves0pending and terminates other nonzero statuses. ExtractInt16_v2_Signed decodes payload4/5 little-endian signed16. ECODAN_Bridge.ino2029–2030 publishes TH32/TH34 unchanged as BrineInletTemp/BrineOutletTemp. This supports experimental whole-degree candidates for27/28, not physical validation or precision beyond whole degrees.

Request27: `FC 42 02 7A 10 A3 00 1B 00 00 00 00 00 00 00 00 00 00 00 00 00 74`.
Request28: `FC 42 02 7A 10 A3 00 1C 00 00 00 00 00 00 00 00 00 00 00 00 00 73`.
Response header FC62027A10, followed by16-byte payload and checksum. Expected payload A3,service-high,service-low,status,raw-low,raw-high,remaining10bytes. Parser validates complete frame before interpretation. Wrong echo/owner does not complete a transaction. Late same-code responses have no protocol transaction ID; ownership/timeout/guard reduce ambiguity but cannot distinguish arbitrary same-code replays.

## Scheduling

One owner: connect, normal GET04 or service. Connect starts after1s/retries3s. Normal GET04 has priority when due every2s. Service27 then28, retries at least1s from request start, deferred by an in-flight transaction/normal poll/50ms turnaround. Maximum10 transmissions per service (9retries); finite timeout/exhaustion, then next service. Both done ->20s cooldown. No busy waits or callback delays; UART polling remains serviced during RS485 TX. Reply timeout800ms from final byte queued; queue timeout1s; no matching reply10s causes reconnect/cancels service. Old completed raw payloads survive recovery, but validity clears. Compressor freshness10s, brine60s. All ages saturate65535s; stale flags cannot revive at timer wrap.

## Modbus FC04 map

Raw zero-based inputs. Preserve0–15 fromP0070, except expected build marker becomes71. Max16 consecutive registers per read; larger reads exception2. Invalid quantities0/>125 exception3. Writes rejected. Counters wrap16bits, no flash persistence. Each individual response is one synchronous snapshot; multiple blocks can cross an update. Bracket completed-payload reads with per-channel completion counts (operator helper does this).

| Address | Meaning |
|---|---|
|0|888 marker|
|1|71 build|
|2–15|P0070 compressor/validity/age/counters/link unchanged|
|16 /24|Last completed raw uint16 for27/28; retained when stale;65535 before first|
|17 /25|Experimental signed whole-degree candidate bits; valid flag required|
|18 /26|Completed sample still fresh (1), not hardware-correlation flag|
|19 /27|Seconds since completion,65535 never/saturated|
|20 /28|Latest matched service status,65535 never|
|21 /29|Completion count|
|22 /30|Ever completed flag; disambiguates raw0xffff (-1 candidate)|
|23 /31|Reserved0|
|32|Service state:0idle,1ready,2wait reply,3wait retry,4cooldown,5link down|
|33|Active27/28, or0when idle|
|34|Latest checksum-valid A3 status (including wrong echo),65535 never|
|35|Retries already started for active service; resets at advance|
|36|Accepted matching A3 responses including pending|
|37|Service error events: bad frames/UART,wrong echo/owner,timeouts,terminal status|
|38|Retry exhaustion count|
|39|CN105 owner:0none,1connect,2GET04,3service|
|40|All checksum-valid A3 response count|
|41|Gap in ms between most recent service request starts, saturated65535; may be short between27and28|
|42|Finished service cycles (success or failure)|
|43|Decoder evidence1=reference only; never hardware-correlated in this build|
|44–51|Latest checksum-valid A3 payload, including wrong echo|
|52–59|Last completed27 payload,16bytes|
|60–67|Last completed28 payload,16bytes|

Raw payload packing: each word represents byte0 +256*byte1. Decode low byte first, then high byte, in ascending register order. Modbus transport word byte order remains standard big-endian. Zero-filled raw buffers before completion do not establish a measurement. Candidate values are int16(raw), scale1. Never use65535 alone to identify missing: -1C has those bits too; checkvalid/ever. The complete original validated response is reconstructable from retained payload plus fixed header/checksum; distinguish this from a direct wire capture.

## Operator hardware verification

No hardware action performed inP0071 build. Operator owns flash and read-only validation. Capture timestamped blocks0/16/32, latest raw44–51 and completed raw52–67; helper read_brine.py records all, plus before/after completion counts. Verify888/71,heartbeat,fresh changing compressor reply count,27and28 echoes/statuses,~1s retry gaps and Modbus responsiveness. Preserve full completed payload and compare decoded candidate against physical Mitsubishi service display027/028 at matching times. Do not call brine hardware-verified until correlation is sufficient. If state remains pending, preserve raw/error/retry history; stop after3hardware debug attempts and reassess. Recovery: previous immutable P0070 BIN or original via documented vendor procedure, operator only.

## Engineering lesson

The conservative ARM timing model uses1us/instruction, not cycle-accurate STM32 timing. An initial68-register bulk response delayed CN105 RX during CRC in that model. Retaining the proven16-register maximum bounded this cooperative critical section; final pending-service test receives25CN105 bytes while Modbus DE is asserted without overrun. Native65s simulations show32normal replies while services complete, remain pending, time out or return corrupt/wrong-echo responses. Tests are synthetic, not hardware evidence.

## P0071 r2 — operator-directed exclusive sequence

The operator explicitly changed the schedule after r1 only returned A3 status0. Send exactly one Hz GET04, then service27 including all retries, then service28 including all retries, and repeat. No Hz or other query is inserted between retries or between27and28. One request owns the link at a time; retain1s minimum retry cadence,10attempt limit,800ms reply timeout,1sTXqueue timeout and50ms turnaround. The prior20s cycle cooldown is removed. State4 now means DONE waiting for next Hz, not cooldown. Link-loss reconnect is deferred until both bounded service operations finish; then connection recovery restarts from Hz. This overrides the previous interleaved polling design under explicit user direction.

Hz freshness remains truthful: during a long service sequence it can exceed10s, so input3 becomes0 and input2 becomes65535 until the next normal response. Input4 exposes age. Do not call this an unexpected communication failure without checking the phase/counters. Brine validity/retention unchanged. Inputs0–67 unchanged except state4 semantics; new input68=2 identifies r2. Marker0=888 and build1=71 remain. Maximum16registers/read.

Native65s simulations assert every emitted request follows Hz→27→28, including not-ready,missing,corrupt,wrong-echo,terminal-status and timer-wrap cases. All12ARM cases pass; pending-service case emits only one Hz then five27 requests while Modbus responds; complete case reaches next Hz only after28. Checksums/frame whitelist, heartbeat and no flash/control writes remain tested. r2 hardware result pending; no temperature is hardware-confirmed. Physical attempt1 was r1, pending-only, evidence stored in analysis/live/20261006T200502Z-p0071-first-readback.jsonl.
