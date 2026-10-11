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
