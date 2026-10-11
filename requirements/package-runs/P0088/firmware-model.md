# P0088 — cumulative readable firmware model

This is the entry point for the reconstructed FTC20.01 architecture. It is a partial analytical model, not recovered complete source code. Names describe proven responsibilities; addresses preserve links to evidence. Each module records inputs, outputs, dependencies and open edges so the next analysis starts from established contracts.

|Named module|Inputs and responsibility|Outputs / dependency|Detailed evidence|
|---|---|---|---|
|CN105 settings staging|SET categories populate staging fields;CF0E0/CF846 announce import|2373 category event|[Application ordering](settings-apply-order.md)|
|Active settings import|90ABA→BC0D8→BD166 consumes event;ordinary importer runs earlier|Active settings, e.g.0770 and07E6; event cleared by90BD4|[Application ordering](settings-apply-order.md)|
|D extended settings transfer|33 bounded range entries resolve742 selectors, including aliases;direction must match|Staging records, not a complete setting inventory|[Transfer mapping](settings-transfer-map.md), [events](settings-d-events.md)|
|Settings persistence|Serialize selected profile; compare and write words;verify twice|Read/shadow bookkeeping, storage fault, startup reload|[Named persistence model](settings-store-model.md)|
|Pump-level consumers|Active0770/07E6, demand and profile reduction|Timer A2 output and separate table-derived accounting contribution|[Consumers and timing](pump-consumers-and-timing.md)|
|Pump reduction and energy chain|Timed state49C8/count49C9 and calculated sample windows|Reduction code49C7, power output and separate running/published energy banks|[Reduction and accounting](reduction-and-energy-chain.md)|
|Reduction activation|Descriptor30, configuration0939, phase3CB7 and upstream inputs|Gate/reset/update and result49C7; effective target and selected temperature ownership|[Activation contract](reduction-activation.md)|
|A3 job lifecycle|Request class/selector, queue and asynchronous completion|Cached result; cancellation can follow unrelated commands|[A3 lifecycle](a3-job-lifecycle.md)|
|Source-board outgoing packer|37 qualified templates,249 bitfields, selected active values|Packed messages toward source-board path|[Outgoing descriptors](source-outgoing.md)|
|Source-board result import|Response decode and result dispatch|Service values and completion state|[Source link](source-link.md)|
|UART6 room path|Eight-room message decoding and target representation|Room-related values; physical CNRF attribution qualified|[Room path](uart6-room-path.md)|
|UART0 storage/file path|File-oriented controller operations|Storage-related data; SD/CN108 attribution qualified|[Storage path](uart0-storage-path.md)|
|UART1 snapshots|Snapshot formats and maintenance functions|Diagnostic data; connector attribution qualified|[Snapshots](uart1-snapshots.md)|

## Walk one value through the puzzle

```text
CN105 heating-pump staging1CB0
    -> import event2373=6
    -> BD780 writes active07E6
    -> default serializer94A82 writes desired image[1AB]
    -> background9687C finds dirty word[1AA..1AB]
    -> writer968E0 drives948A2
    -> two physical readbacks OR fault after three failed verifications
    -> startup96AF4 loads read image[1AB] back into07E6
```

This connects communication, active RAM and persistence. The next module now follows07E6 through selected level3A33 into a timer-backed output and a separate accounting contribution; physical speed remains unqualified. The neighboring byte in the word must be preserved.

## Rules for extending the model

For each newly understood function: give it an analytical name; retain firmware address and image identity; record read/write fields and callers; distinguish proved behavior from interpretation; add pseudocode for branches that affect state; and test an independently checkable edge where possible. Contradictions update the model rather than accumulating competing unqualified descriptions.

Do not merge staging, active state, physical memory and telemetry merely because values resemble one another. Do not promote a software UART role into a physical connector fact without supporting evidence. Export complete bounded control flow when the decompiler or function body is incomplete.

The immediate remaining boundaries are physical status-indicator attribution, timer clock qualification, external meanings of pump configuration gates, remaining physical gate identities and accounting freshness/units, then source-board control requests. Exact compressor regulation remains incomplete; understanding the FTC-to-source contract alone does not establish the source board's internal control law.

For new bit-sensitive exports use the qualified isolated language variant described in [decoder repair](decoder-bit-repair.md). Historical exports retain their original language identity; repaired C does not imply that unrelated CPU semantics are fully validated.

Configuration producer0939 is now traced through09F1 and the184-byte publication in917FE; see the activation contract.
