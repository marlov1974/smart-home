# P0088 — timeboxed command/port pass

## Deliverable and stop rule

The user authorized a first pass capped at two hours, with at most15 minutes per
individual gap. This pass prioritizes CN105, source and D; SD/diagnostics remain
structural. It does not wait out the budget after a useful checkpoint. No live
reads, writes, flash or connector changes. No full-firmware completion claim.

The new generated [matrix](command-port-matrix.md) and JSON assemble existing
qualified evidence into one worklist. Reproduce with:

`python3 tools/ftc6/p88/port_matrix.py requirements/package-runs/P0088`

Do not sum its mixed units into a total feature count.136 mapped41/42 routes
and5 alternate routes are separated from376 rejected/default lookup slots.
Source37 templates aggregate249 bitfields. D33 ranges cover742 numeric selectors
with aliases, not742 independently understood settings. Normalized branch
records remain in a separate residual list. UART0 default transaction is labelled
separately. Whole-command completion is deliberately stricter than field-source
closure, so the report currently marks every row PARTIAL.

## Edges closed in this pass

1. Previously separated SET32 target dataflow now links the CN105 route to the
   source82C2A packet; C8 links to D advertisement/end, A3 to source request/result.
   These links are profile/session conditional, not a guarantee of immediate action.
2. CN105 response byte stores now join their command via the actual response
   packer, rather than being counted as independent commands. Raw stores retain
   UNKNOWN meanings; callback fields need further analysis.
3. All32 source RX low-five-bit values and16+16 D receive/transmit-event low
   nibbles now map to normalized candidates and existing branch handlers.
   State/history gates below prevent treating these as unconditional handlers.
4. GET04 and C9 response sources are fully bounded, including the otherwise unwritten tail.
   5C/5D response payloads are constant. Their full native request effects remain open.

## CN105 small-family pass: exact response sources

A535E invokes TX descriptor callbacks in order +4 initialization, +8 payload,
+12 checksum. C9's descriptor85676 selectsA9080/A8F8A/A90A0.
A9080 callsA906A, clearing22 bytes2359..236E, then installsFC/02/7A.
The packer supplies response type239F (descriptor7B here), payload length16.
A90A0 appends the negative sum of frame bytes1..last-1;FC is excluded.

|C9 payload offset|Source/value in supplied20.01|
|---|---|
|0|C9|
|1..4|ROM84ADE..84AE1 =03 00 01 00; pairs passed high-byte first|
|5|14 hex, fromA4A9A|
|6|03, fromA4AA4(1)|
|7|05B2, throughA4AA4(2)/A22F4|
|8|Boolean099B!=0, throughA4AA4(3)|
|9|01, throughA4AA4(4)|
|10..15|00 from shared frame initialization; not stale previous response bytes|

The native field names for the ROM words and capability fields are not all
qualified. Do not label the first bytes a firmware-version string merely from
their appearance.099B's known accounting-mode role is separate from this
Boolean availability presentation.5C's payload isCC FF;5D's payload isCC.
Their parsers require connected2342.bit0, header helper result3 and selectorCC;
5B requiresC9. This proves packet processing, not absence of all side effects.
Eight new about/parser exports match in both corrected Ghidra projects;
A22F4 and the common TX helpers have supporting single-project exports.
Pinned-byte and assembly hashes are in port-sprint-evidence.json.

GET04 also uses the shared initialization. Its16 payload bytes are now sourced:
p0=04; p1=062C&7F; p2..7=395A+12*i for i0..5; p8 maps4925;
p9/p10 map3958/3964. The mapping retains0,1,2 and returns0 for other
values. p11..15 remain zero. These are byte-source contracts; physical units
and identities of the six records must not be invented from their position.

## Source RX pass: pre-history mapping, not independent actions

9CBF6 masks08D3 with1F and indexes8328E. The32-slot table has15 nonzero
normalized values; zero means no normalized event, not proof the wire type
can never have a transport effect. Values7/9/10 are admitted only after prior
state6 or0B; otherwise state becomes0. The resulting state indexes88F46;
flags8 and20 select the16-branch receive dispatcher. The final branch candidate
is `(state-1)&FF`, capped to15. Full peers/field meanings are a later tier.
The type1D service-result path remains fully connected to the shared A3 consumer.

## D pass: raw nibble is only one part of the transaction

9F152 translates RX08BD.low4 through832FE and local transmit notifications
through832EE. RX normalized5 changes to6 after prior5/12(hex); transaction-class
mismatch can suppress5 after prior3/4. TX18(decimal,12hex) can change to19.
A25-by25 history matrix at88F65 then admits events only with flags8 or10hex.
9F2EA dispatches from normalized1430-1 with index capped to24. Therefore the
JSON candidate branch is a pre-history association, not a safe transmit recipe.
D raw0B -> normalized14(decimal) -> branch13 is the known settings/service path.
The physical CN22 assignment still needs independent verification.

## Ranked residual queue — no open-ended detours

|Priority / gap|Next bounded action|Done when|Evidence type / stop|
|---|---|---|---|
|1 CN105 frequent GET fields|Byte-source layouts0B/0C/14/15/26/28 are mapped; next qualify sampled companions, A4D5E rounding and GET04 record producers|Each byte has source, encoding, invalid marker and uncertainty|Offline,15min per command; park unresolved writers|
|2 CN105 SET32/34 remaining fields|Selected enables, setters and repeat-sensitive field mapped; finish p4 and native admission|Each enabled field has effect and admission; distinguish response ACK from application|Offline; no full regulator reconstruction|
|3 Source RX non-service families|Use new raw-type candidates and bounded branch exports|One family at a time: length, staged fields, consumers, history gates|Offline; stop at absent source-board firmware|
|4 D base command families|Follow normalized handlers with raw/state maps|Identify settings, telemetry and transaction roles with aliases|Offline; do not invent peer scheduling|
|5 Settings47 blocks|Group by import callback and shared encoding|Map payload fields to settings/default/persistence|Offline batches; unresolved peer sequence stays external|
|6 Physical connector binding|Continuity or passive traffic correlation at candidate connector|Measured association between software path and labelled connector|Separate hardware work; not authorized/performed here|
|7 Peer session behavior|Capture a native settings transaction or obtain peer firmware|Observed1005/start/transfer/end timing and error recovery|External evidence; stop repeated FTC-only searching|
|8 SD/diagnostics|Keep structural inventory and explicit side effects|Only deepen for a concrete needed feature|Deferred; no impact on the first three priorities|

A later pass should report command IDs whose fields or gates became qualified,
not growth of raw inventory rows. Zero whole-command completions is an honest
strict baseline; field-level closures and usable partial contracts are reported
separately. Existing coverage.json remains the raw atlas coverage, not this
new command-level accounting.

Continuation: [six frequent GET payloads](cn105-fast-fields.md) now have explicit byte-source contracts. Remaining work is sensor/flag meaning, freshness and the identified helper gaps rather than rediscovering packers.

Continuation: [SET32/SET34 field contracts](cn105-control-fields.md) distinguish zero ACK from application, target mode context from mode-update enable, and the SET34 repeat-sensitive counter.

Start with the [code/function/port catalog](command-catalog.md) for the complete currently identified inventory and evidenced cross-interface relationships. Unknown functions remain visible.
