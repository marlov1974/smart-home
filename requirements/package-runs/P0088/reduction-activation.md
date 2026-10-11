# P0088 — activation and input ownership of pump reduction

Offline FTC20.01, language `m16c:LE:16:p88-bits`, qualified spec1395807e49d7ef74e368fbd97b6aa0ca7a9cbeba6abe9843b68aa8739385e358. This closes the generic-dispatch edge left open by [the reduction model](reduction-and-energy-chain.md). It does not establish installed Geodan configuration.

## Descriptor to execution: the missing edge

`9171A` walks **33 records**, each26 bytes, from81732. The pump module is record30 at81A3E:

|Offset|Value|Meaning established by consumer|
|---|---|---|
|0|0939|Pointer to configuration byte; not a service selector|
|2|49C7|Pointer to published result byte|
|4|88794|Far callback-table pointer|
|8|8972C|Far callback-count/policy pointer; data, not executable code|
|12..25|Only byte8 equals1|14-entry mask indexed by operating phase3CB7|

`91642` reads the configuration, selects the matching30-byte callback record (0 or1 here), calls initialization and result callbacks, and stores configuration/selected-row/previous-activity state. Both callback rows contain the same seven function pointers. An unmatched configuration records a diagnostic and selects the zero row; this is not validation that arbitrary configurations are meaningful.

On each main-loop pass, `9171A` reloads the descriptor. A configuration change reruns initialization. It looks up the phase mask and forces activity0 when configuration==0. Activity changes dispatch enter/leave/transition callbacks. Activity0 calls D3C78 (clears49C8/49C9 and both timers); activity1 calls D3D0C; the result callback D3CAC always publishes to49C7. Main loop92482 calls9171A at9256A.

Therefore the reduction updater is active only when **0939!=0 and3CB7==8**. Leaving phase8 clears its progress; the reduction timer is not a global timer that continues uninterrupted through DHW or other phases. This is separate from the state3 inhibit latch within an otherwise active phase. The configuration's UI name and current physical value remain unknown.

## Effective heating target, not merely the incoming SET

The first D3E8A condition uses3908 minus0662. P87 already established3908 as the ordinary effective heating target after mode and override selection; this continuation connects that result to pump reduction. Initialization97D48 chooses from38DC/38DE/38E0 according to3915 and calls the shared target-selection routines. See [P87 target chain](../P0087/flow-target-trace.md).

Thus `effective_target - flow >=300` cannot in general be replaced with `last_sent_target - flow >=300`. Fixed-flow SET32 and the active target may agree in an ordinary case, but alternate target/override paths must remain explicit.

## Temperature input0686 is selected upstream

`8FA7E` writes0686, not merely the startup initializer8F1F8. For profile0900!=1, it copies0619. For profile0900==1 it selects one of six12-byte source records and copies3956+12×selected_index. It also maintains separate delayed samples0688/068A, with source buffers updated after timer counts300/600. D3E8A uses0686 directly, not those delayed fields.

The same selected0686 flows through A4088 into response packerA5832, which emits GET0B and stores the encoded byte at2369. A4088 passes raw minimumF060(-4000) and step50 to A4D5E. This establishes a communication-visible selected temperature with half-degree-style encoding arguments. Physical sensor/port provenance and the exact conversion helper remain distinct qualification tasks; no new wiring claim is made here.

## Entry mode39EA has a separate owner

`CBCFE` writes39EA. Several gates force0:39EB!=0 with0986==0;38BF==2;39E8==1;082A bits2 or4. Otherwise, when the low nibble of0508 or0509 equals1 and050A.bit7 is clear, it sets39EA according to whether the decoded top three bits of050B equal5. Decoder9A942 uses the eight-byte table82516:0,1,2,3,4,5,FF,FF. If the message condition is absent or050A.bit7 is set, the old39EA is retained.

D3E44 requires39EA==0. This is a latched mode value with explicit update conditions; it should not be guessed to mean a fresh measured temperature, compressor frequency or universal system-on flag. Identifying its external command name remains open.

## Implications for the executable model

The complete local ordering now is configuration/phase gate -> initialize/reset or timed reduction update -> publish49C7 -> AF452 applies bounded level reduction. Effective target and selected sensor ownership are upstream contracts. Current hardware activation, configuration0939's owner and remaining physical signal identities are still needed before asserting this reduction happened in a particular historical trial.

Cross-reference caution: Ghidra's reference index missed some writes shown in the instruction listing, including8FBC4/8FBEF to0686. Absence from references.tsv is not proof of no writer. This is now recorded as reusable analysis guidance.

## Configuration owner — subsequent checkpoint

The direct-writer search missed a **block copy**, not an absent feature. `917FE`
constructs a 184-byte configuration at09AA..0A61 and copies92 words to
08F2..09A9 when ROM88EEE!=1. The qualified image contains0 there.
Offset47 therefore copies **09F1 ->0939**.

`91FC0` sets09F1 to the result of923BC only when3A4A==0; every other
branch clears it. With the corrected bit decoder,923BC requires:

- 3A4F==0,07DF==1,07E6>=3 and06D5.bit7 set;
- 07EE!=1,0A45!=1 and06D7.bit0 clear;
- not(06D4.bit4 set and073C==1).

Executable pseudocode is `reduction_configuration()` in
[the pure model](../../../tools/ftc6/p88/pump_control.py).
These are configuration gates, separate from the seven runtime temperature/flow
conditions inD3E8A. Pump level07E6 is already identified; the other raw settings
must retain their addresses until their external meanings are established.
This closes the immediate producer, not every producer of its inputs.

There is a later profile overlay:09B8==2 calls92298(2), selecting row6 of
seven159-byte records at88A3C. Its nine5-byte copy descriptors start88EEF.
Descriptor6 covers09D7..09F4 from3C4C..3C69, including09F1 from3C66.
For selected row6, the corresponding ROM byte88E46 isFF, meaning **retain**.
Thus it does not replace the computed09F1. Moreover09B8==2 requires06D7
bits0 and1; bit0 itself inhibits923BC. This path cannot enable reduction.
Other ROM rows must not be substituted for the actual selected row.

Resulting chain: settings/state ->91FC0/923BC ->09F1 ->block publication
->0939 ->phase8 dispatch ->timed reduction ->49C7 ->AF452 pump level.
No installed-device value or universal Geodan activation is established.
Three owner routines were independently exported from both corrected projects;
the assembly matches.92298 and the overlay bytes were separately inspected.
A raw-byte3909 match atCBFAA was rejected as overlapping operands, not a0939
reference; the exploratoryCBF90 seed supplies no evidence for this result.

## Upstream gate provenance — continued mapping

The gate inputs are not all persistent configuration. The following distinctions
are now established in the20.01 reference:

|Field|Producer and provenance|Meaning established|
|---|---|---|
|07DF|BD780 copies1CA1&1;96AF4 loads102A;94A82 stores0E2A|Persistent Boolean enable required by923BC; UI label unresolved|
|07EE|BD780 copies1CC2&1;96AF4 loads0F6B;94A82 stores0D6B|Persistent Boolean inhibit; UI label unresolved|
|07E6|BD780 copies1CB0; image offset1AB|Selected heating pump level, already traced to actuator consumer|
|3A4F|C61F6 derives it from06D5 bits5/6 and06D6 bit5|Derived class, not directly a saved setting|
|0A45|91A70 derives it from06D9 bits3/4 and06A5|Calculated configuration field; later overlay remains relevant|
|3A4A|B4674 publishes a selected three-byte candidate record|Runtime arbitration result, not a fixed model identity|

The desired/shadow offsets for07DF and07EE are146 and087 respectively.
959DE reads the same offsets in its selected ROM defaults. **All three previously
qualified default rows8000A/8020A/8040A contain07DF=0,07EE=0,07E6=5.**
Therefore the07DF gate disables reduction in these defaults even though the
pump level is high enough. This says nothing about saved settings, later
transfers, another firmware version, or the current installed units.
BD780's staging addresses must not be presented as Modbus registers or inferred
D-selectors: they did not directly match the existing33-range transfer table.
The missing staging-copy edge remains to be traced.

C61F6 simplifies to:3A4F=0 if06D5.bit5 is clear; otherwise1 if06D6.bit5
is set or06D5.bit6 is clear; otherwise2. Hence its zero/nonzero gate depends
only on06D5.bit5.91A70 sets0A45=0 when06D9.bit4 and06A5==1; otherwise
0A45 equals06D9.bit3. The model preserves this as a pre-overlay calculation.

8E3DE copies the reduction prerequisite06D5.bit7 from3876.bit7 in all
three profile branches.8E12C builds3876 by transposing bit1 from eight inverted
snapshot bytes08E6..08ED; specifically3876.bit7=NOT08ED.bit1. It is a
sampled input/configuration path, not evidence that the user must set a named
physical DIP switch.8E37E can override3876 from ROM888D8 only with magic
80FF4==5A5A and a nonzero override. This image has magic0000 and override00,
so that ROM override is inactive. Physical switch-bank/pin identity is open.

B4674 calls16 candidate producers, starts with mode0, and copies qualifying
three-byte records into its selected result in an explicit order.0900==2 skips
the ordinary selection block. It publishes3A4A..3A4D. Decompiled C shows
uninitialized candidate locals and parameterless helper calls because the
caller-provided output ABI is not recovered; it is not evidence of firmware
reading genuinely uninitialized data. The exact candidate meanings and priority
chain require assembly-level argument recovery before an executable arbiter.

Four main routines match across both corrected projects.8E12C/8E37E andBD780
were inspected in one corrected project; existing persistence exports supply
the storage connections. Pure derived-gate helpers exhaust65,536 flag pairs
and1,024 auxiliary cases. ROM defaults are separately checked against the
hash-qualified binary. No physical readings or writes were performed.
