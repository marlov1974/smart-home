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
|10|Brine pump running|unavailable|no verified mapping; never inferred from compressor|
|11|Brine pump step|unavailable|no verified mapping|
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

Compressor expires10s; other direct FAST fields30s; brine60s; disconnect invalidates cached direct/service samples. Raw data survives for diagnosis. Long pending A3 operations can legitimately make Hz stale. Brine delta can mix samples acquired several seconds apart; it is not a simultaneous high-resolution measurement.

Conservative accepted ranges: brine -40..80C; flow/return/tank and targets0..100C; outdoor -40..80C; flow0..200L/min; boolean0/1; operating0..7; pump lookup exact. These are parser plausibility bounds, NOT writable target limits. Missing sentinels/range failures cannot produce valid thermal power.

## Heat calculation

`W = trunc(flow_cL_min * delta_cC * 418 / 60000)` using signed64 intermediate, signed32 output. Assumes water density1kg/L and heat capacity4180J/(kg K). No glycol correction; this is water-side power, not brine-side power. Positive supply-return gives positive heat, negative gives negative cooling. Zero flow/delta gives valid0 if sources are valid. Invalid/stale source or acquisition skew>2000ms between GET0C and GET14 gives invalid power. TTL30s still permits an aging cached power estimate; consumers should check exposed age for their own cadence requirements.

20L/min and5.00K yields6966W (integer truncation). Whole-L/min source quantization and unverified temperature accuracy limit precision despite the W unit. No COP, electrical measurement, energy integration, autonomous stress testing or closed-loop power control.

## Raw evidence and operator readback

Inputs200–255 hold seven16-byte matched FAST payloads,8 words each in schedule order04,0C,14,0B,09,15,26. Each raw word low byte first. Completion payloads A3 remain52–67. Use generations/status to establish new data rather than zero-filled buffers.

After operator flash:
`python3 procon/tools/read_mvp.py --samples 10 --interval 2 --output <new-file.jsonl>`
The helper only invokes MbRtuClient.ReadInputRegisters. Interval is minimum sample-group period; serial transactions can take longer. Correlate physical flow/return/DHW/outdoor/flow/Hz/targets, brine completions, error counters and LED. Do not test control until a later actuating revision has explicit verified semantics and telemetry passes. Hardware attempts used for this revision:0/3.

## P0072 r2 update

Revision2 adds supervised, reference-backed control commands with snapshot/readback/runtime lease restoration. See [control API](CONTROL_API.md). Earlier r1 read-only statements remain historical. No hardware control validation or reboot restoration is claimed.
