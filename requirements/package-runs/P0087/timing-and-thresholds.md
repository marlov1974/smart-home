# Timing, thresholds and memory

Generic timer helpers are qualified independently from any named thermostat:
A330E dereferences a ROM descriptor and writes8000 (start/reset);A3322 writes0 (clear);A3334 ORs8000 (resume preserving low15 count);A3354 ANDs7FFF (pause preserving count). A3392 returns0 when disabled,1 when count<descriptor+4 threshold,2 at/above threshold. A33D4 tests enabled count>=caller threshold. These are raw counts, not seconds. The model supplies words explicitly and does not invent a tick scheduler.

| Evidence / predicate | Raw condition | Meaning / limitation |
|---|---|---|
| A13C4, profile0975=1 | 3A2A=1 and descriptor837E0 count>179 sets3A2C=1 | Local request/status gate; equality180 passes. Other predicates force0; not proven min-off |
| A13C4 clearing | A27B2 result differs3A29;3A02>1;0604=7;39C3=5/7;A22D6!=0 | Gate state overrides; no unconditional thermal start |
| A13A6, other profile | 3A2C=05DB unless3A02>1 ->0 | Reported peer state can determine local state |
| A1448 | 3A2C=1 resumes descriptor83EFA; on expiry resets;3D8C reaches100 then14FC increments | Accounting-looking state, **not** an error integrator; full time unit unresolved |
| B2700,3A4A=0 single circuit | max(3908,2500)-0662<-199 | Candidate branch at overshoot>=2C; overrides exist.3A4A ownership not sufficiently traced to call compressor thermostat-off |
| B2700,3A4A=2/3 | descriptor83A6E caller threshold180, error<0 and49A8=0 | Compound actuator-state branch, not universal stop predicate |
| AC79A | state3E02:0 ->1 when3E01!=2,3D07=2,error<200;1 ->2 when3D07!=2;2 ->0 on expiry | Timer83BCA; resets/re-enters on3D07=2. CallerAC6C8 output70 while state2, otherwise100; physical unit/consumer unresolved |
| AC880 | state3E05 starts with4927=2,error<=200,3DA4<3944; stops on expiry/3D07=2/4927!=2 | Timer83BD0; caller output50 while active. Not proof of compressorHz or percent |

The `83...` values are far ROM descriptors; Ghidra C may show `near:37E0` plus a separate upper argument8. Assembly stack arguments preserve that upper word. Do not address these descriptors as near RAM. Catalog values remain raw until the interrupt -> scheduler -> descriptor tick is connected.

P86 established clock register programming and conditional UART divisors. It did **not** establish the interrupt/prescaler/callback chain for these control timers. No180->180seconds,60->minute, or ten-minute restart assertion is made here. Wall-clock timestamps in historical captures are separate from native monotonic counters.

Official OCH722A's Heating operation **Room temp. control table** lists Heat pump thermo diff.adjust default lower-5C/upper+5C (ranges-9..-1/+3..+5). These are documented room-control settings, not code-proven fixed-flow thresholds. Their exact firmware fields and applicability to EFFECT's fixed mode remain UNKNOWN. No matching numeric constant alone is promoted. Likewise minimum run/off, valve lead time, pump overrun and DHW time limit remain unresolved; see discriminating proposals rather than fabricated graph edges.
