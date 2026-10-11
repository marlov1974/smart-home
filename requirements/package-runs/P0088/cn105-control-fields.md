# CN105 SET32 / SET34: enables, consumers and acknowledgment

Offline FTC20.01 evidence only. No device calls, flash or controller changes.
Image and assembly hashes, per-field layouts and ROM tables are recorded in
`port-sprint-evidence.json`; generated rows are `uart2.41.32` and `uart2.41.34`.
These are partial command contracts, not authorization or recipes for live writes.

## What the acknowledgment establishes

SET32 is dispatched as internal event2340=1, SET34 as event2340=3.
Their response packers A541A/A5446 return a16-byte zero payload after the
shared initialization. They explicitly set p0=0 and never consult the native
setter results. A response therefore does not establish that a requested value
passed a profile guard, was stored, became the effective target, or affected an
actuator. Readback and native state must establish those separately.

Payload positions below start at opcode p0=2348. p1=2349 and p2=234A are
field-enable bytes; they are not interchangeable between the two commands.

## SET32: operating and target fields

|Payload|Enable|Consumer / effect|
|---|---|---|
|p3|p1.bit0|90338/A459C:0 or1 accepted;2/3 and larger invalid. Valid result ->3AC3 ->90368 ->38BF; clears082E.bit7. Other90368 effects remain to qualify.|
|p5|p1.bit2|BC02C/A462A ->3912 DHW mode; FF ignored.|
|p6|p1.bit3|BBCB6/A468E ->BBE92 zone1 mode.|
|p7|p1.bit4|Same, zone2.|
|p8..9|p1.bit5|BBA48/A46C4 ->3906 DHW target, BE16; FFFF ignored.|
|p10..11|p1.bit7|B9AD0/A46FA ->B9BFE zone1 target, BE16, with decoded p6 as mode context.|
|p12..13|p2.bit1|Same, zone2 target with decoded p7.|
|p14|p2.bit3|92B92/A4B30:low3bits ->082A.bits11..13. A subsequent2342.bit2 condition clears all three.|

The p5..13 consumers listed above require0900!=2. This guard is not present
in the inspected90338 and92B92 entry paths; do not generalize it to all fields.
Disabled numeric targets decode toFFFF. The byte-mode lookup at84AF8 is
`00 01 02 03 04 FF`; invalid inputs also returnFF.

**Target-only changes still depend on the supplied mode byte.** B9AD0 calls
A468E with enable=1 for p6/p7, regardless of the mode-update enables. It skips
its target call for decoded mode2 or5 (the inspected table itself does not
produce5). Other results reach B9BFE with explicit zone and mode arguments.
It does not substitute the current mode here. This explains why clearing the
mode-update flag is not sufficient reason to omit or zero the mode byte.

For zone1 fixed-flow mode1, the previously qualified chain is:
requested38DE -> selection38D6 -> holiday/override38D4 -> effective3908
->BA962 ->39EF -> conditional source packet82C2A. See
[flow-target trace](../P0087/flow-target-trace.md). Requested, selected and
effective values must remain distinct in a future controller model.

Remaining SET32 gaps include p4/operating request, unqualified enables, all
native admission and persistence paths. This pass does not claim every field
or all possible side effects are closed.

## SET34: auxiliary fields and repeat-sensitive behavior

|Payload|Enable|Consumer / effect|
|---|---|---|
|p3|p1.bit0|B95A4/A472C ->B95E0 ->3919 boost;0/1 only;0900!=2.|
|p4|p1.bit1|C0A98/A4760 ->C0AD0 ->391B holiday;0/1 only;0900!=2.|
|p5..9|p1.bits2..6 respectively|8F816 and A4796/A47CC/A4802/A4838/A486E:0/1 replace39A6.bits0..4 respectively; FF means preserve prior bit.|
|p10|p1.bit7|CE8E2/A489E:0 raises4977;1 raises4976. Neither branch explicitly clears the other flag.|
|p11|p2.bit0|CE920/A48CE:1 increments byte33EA and sets39EC;0 clears both.|
|p12|p2.bit1|CE8E2/A4C2A:0/1 ->39A4.|
|p13|p2.bit2|ABDDE/A3D3E:table8929D lookup times10 ->3E06; copy to3933 with separate ABE04 override to100.|

For p5..12, an unset enable or a value other than0/1 returnsFF and leaves
the corresponding state unchanged. The p13 table is `10,1,2,3,4,5,6,7,8,9,0`:
wire0 ->100,1..9 ->10..90,10 ->0, values>10 ->100; disabled ->FF/no store.
The physical interpretation of that demand-like field is not established here.
The inspected auxiliary consumers do not contain the0900 guard used for
boost/holiday. Wider scheduler/admission conditions remain separate.

CE920, simplified from assembly (timer branch shown separately):

```text
if event == SET34 and p2.bit0:
    if p11 == 1:
        counter33EA = (counter33EA + 1) modulo256
        state39EC = 1
    elif p11 == 0:
        counter33EA = 0
        state39EC = 0
state39ED = timer_condition or counter33EA >= 10
```

This field is **not idempotent**: ten accepted enabled1 requests can take a
counter from0 to10, whereas one such request leaves1. The byte increment has
no saturation, andFF preserves state. This proves an internal retry effect;
it does not yet establish the physical action of39ED. Ordinary target retries
must not be conflated with this particular SET34 field.

The other39ED input uses timer840BC and threshold0258. After connection has
been observed via2342.bit0/33EB, events0/95 callA3334; other events callA3322;
A33D4 tests the threshold. Timer units and every downstream39ED consumer
remain open. Do not call this a confirmed seconds-based timeout.

GET28 p11 reads39EC and p12 reads39A4, so those two GET/SET state connections
are now explicit. Its p5..9 use399A, while this SET34 branch writes39A6:
those addresses must not be treated as identical state without tracing their
intermediate consumers.

## Evidence and residual boundary

Eleven main handler/ACK assembly exports match across both corrected Ghidra
projects. Additional helpers have single-project exports; pinned ROM tables
are tested directly against the private image. Calls with omitted decompiler
arguments were checked in caller assembly. This does not resolve the known
EXITD/calling-convention limitations or independently validate the entire ISA.

Next bounded priorities: finish SET32 p4 and native admission; then source RX
families. Physical meanings of the auxiliary flags and installed21.00 behavior
remain separate from this reference20.01 static analysis.
