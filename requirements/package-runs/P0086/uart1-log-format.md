# P0086 — diagnostic log decoding

Analytical **PASS for static format**, physical **NOT RUN**. 20.01 addresses:9D8FE→9DA08→13B0;9D88C(F0)→9D8A0→9DA78→1346. Firmware identity pinned inverification.json.

CONFIRMED: ring has9 slots of12 bytes, read/write indices33D2/33D1; one slot remains empty, so8 usable. A full ring rejects the new record and setsbit20h in the previous written record's tag. That flag proves loss, not its count.9DA78 copies12 bytes and advances read index: **reading drains logs**. Never automatically retry after a missing response; it may have consumed records already.

| Tag bits | Meaning |
|---|---|
|low5bits|Source;6 CN105,3/4 D; unknown values retained|
|40h|TX; clear RX|
|80h|Second fragment|
|20h|Loss/overflow marker|

Source binding derives from P84 callsites to9D8FE; D is not proven to be the wall display orCN22. No screen delay is inferred. No timestamp/sequence counter is present in these12 bytes; host capture time is not an internal event timestamp.

9D8FE mode0 copies11 bytes. Mode1 converts word-based data (tag42 uses low bytes, others shifted words); exact D-field semantics remain raw. Mode2 logs21 original bytes across two records: originaltag+bytes0..10, then tag|80+bytes11..20+zero. A22-byte CN105 frame therefore loses its final checksum in the log. Decoder reports21observedbytes andchecksum_captured=false, never fabricates an observed checksum. It joins only adjacent matching, non-loss CN105 fragments within one response; boundary/orphan fragments remainraw. No claimed complete packet on gaps.

F0 response is77bytes: `02 4D F0 02`,6 record slots,checksum.9D8A0 normally drains at most 5 records; if all 5 were available and tagat 137A (fifth record) has80h, it attempts a sixth. This unusual condition is recorded literally. Output is zero-cleared before filling; all-zero slots are padding candidates, not fabricated real events. Repeated empty reads can be expected after draining, but duplicate transport data is not proof of new events.

Tests cover coherent21-byte reassembly, orphanfragment, direction/source, all-zero padding and loss. The tool never claims a global timestamped trace or retransmits log requests. A physical log-observation stage follows electrical/session qualification and requires separate approval.
