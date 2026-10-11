# P0088 — pump reduction and energy-report chain

FTC20.01 static evidence, same SHA-pinned image as the persistence model. No live calls. This connects [pump consumers](pump-consumers-and-timing.md) to their upstream state and downstream accounting. Analytical names are not vendor symbols.

## Reduction is a timed state machine

Record81A3E contains raw identifier0939, output address49C7, callback table88794 and policy bytes at8972C. The latter is **data**, not executable code; an initial pointer classification was rejected after inspection. Callback table records0/1 contain D3C44/D3C52/D3C78/D3C9E/D3D0C/D3CA8/D3CAC. D3D0C maintains state49C8 and step count49C9; D3CAC encodes their result as the code consumed by AF452. Generic dispatch is now qualified in [activation and inputs](reduction-activation.md): record30, configuration0939 nonzero, phase8 only. Live Geodan activation remains unverified.

D3E44 permits entry when39EA==0. D3E5E inhibits when3D07==2 OR3A02==2 OR3A2C==0. These functions do not always return0: that C output is caused by the known signed-FB bit defect. Instruction-level predicates are authoritative.

```text
state0 (idle): clear both timers and step count
    if entry_allowed and not inhibited: state=1
state1 (initial wait): resume timer8419A; clear841A0 and step count
    on8419A expiry: state=2; step count=1 if reduction_allowed else0
    if inhibited: state=3
    if not entry_allowed: state=0                 # final override
state2 (periodic evaluation): clear8419A; resume841A0
    on841A0 expiry: restart that timer
        increment count, up to255, only if reduction_allowed
    if inhibited: state=3
    if not entry_allowed: state=0
state3 (latched inhibit): clear both timers and count
    remain here until entry_allowed becomes false, then state=0
```

Thus simply removing the inhibit does not restart state3. The entry gate must leave its active condition first. Code output is0 in state0,1 in state1,2+min(count,5) in state2,FF in state3. AF452 translates codes2..7 into reduction0..5, with output floor2, only for profile2 and demand1. Other codes do not reduce the selected level.

Timer descriptors8419A/841A0 use RAM18C0/18C2, mask2, accelerated step60, thresholds1800/600. With the earlier nominal mask2=1s assumption, these suggest30min initial wait and10min subsequent evaluation. Actual clock qualification, missed scheduler events and accelerated mode prevent claiming fixed elapsed wall-clock times.

## Seven simultaneous conditions for another reduction

D3E8A builds a7-bit local mask and returns true only when it equals7F. Its C output is invalid for the same signed-FB reason.

|Predicate|Native comparison|
|---|---|
|3908 minus flow0662 >=300|signed16 subtraction and comparison|
|Flow0662 minus return0664 >=300|signed16 subtraction and comparison|
|Return0664 <=5000|signed16|
|Sensor/state0686 >=1000|signed16; physical identity unresolved|
|Flow322E >=1000|unsigned16|
|Flow322E >=100×setting07E8|unsigned16|
|Selected pump level3A33 >=3|unsigned8|

Known temperature scaling makes300 consistent with3 C, but this report retains raw thresholds and does not guess the identity of3908/0686 or the engineering unit of322E. A failed predicate does not decrement the step count. The model preserves16-bit wrapping of differences rather than replacing the native arithmetic with unrestricted Python integers.

## Accounting reaches both power and energy outputs

The downstream chain reuses and rechecks the earlier P83/P86 energy findings; it is not presented as an entirely new energy protocol.

1. CD536 selects calculated mode099B=1 versus meter mode2. In calculated mode CD576 collects samples when062F.bit1 is set.
2. CD5AA sums nine terms, including the pump allowanceCE2A4, into318E's17-slot U32 sample array. Samples beyond17 are not appended.
3. On timer84080 expiry, CD62E averages the available samples by integer division into31D2/31D4, clears the17 slots and count. **With zero samples it retains the previous average.** The scheduler still proceeds to CD69A/CD744; an unchanged published value alone does not establish fresh underlying samples.
4. CD744 divides the average by1000 into3216/3218. CDFD2 selects this in calculated mode, or321A/321C in meter mode. A3E98 supplies this to GET07 through A5724. Consequently the exposed integer power discards the remainder below1000 raw units before output; physical units remain uncalibrated.
5. CD69A adds the average to one of the mode buckets31E6/31EA/31EE for mode9/8/11, and to running3152 with the native wrap helper. CD8F6, on84086 expiry, divides each pending calculated bucket by60, clears it and adds to running3156/315A/315E. Meter mode uses separate increments.
6. Running counters and published A1/A2 banks remain distinct. CDF46 copies running banks and date into published banks and clears the running banks. Service532 is a proven mutating caller; automatic midnight ownership remains unproved. See [P83 energy trace](../P0083/energy-trace.md) and [P86 query side effects](../P0086/energy-qualification.md).

Practical implication: pump commands feed a table/configuration estimate that contributes to total calculated consumption. Integer averaging, division by1000, stale-average retention, later division by60 and explicit publication boundaries each have different effects. Neither a stable GET07 power field nor a static A1 date alone proves stalled communications. Frequent even energy-service reads can force folds and discard remainders; this continuation does not authorize or recommend live polling of those services.

## Next unresolved contracts

Generic dispatch and upstream39EA ownership are now linked in reduction-activation.md;3908 is the effective heating target. Remaining work is the configuration0939 producer, physical0686 provenance/322E units, external39EA name and actual Geodan activation. Follow the zero-sample condition's upstream scheduling/validity handling before calling retained averages a production fault. The exact compressor control law and physical calibration remain outside what these functions prove.
