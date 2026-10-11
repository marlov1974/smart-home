# P0084 settings and ordinary control evidence

Identity/confidence convention: [transport trace](screen-cn22-trace.md). All findings are static20.01; no setting was written.

## New pump-setting write path

P83 found GET65/79 plus staging imports. P84 connects CN105 setters to those staging buffers:

| Operation | Mapping and branch | Data movement |
|---|---|---|
| SET65 | A504C lookup84B56; internal1A; A90F8 switch tableA910F →AACA5 | AtAACCC: RX2352 (payload10) →197B; BD296 atBD401 →0770 (DHW candidate) |
| SET79 | Same lookup; internal2E; switch →ABA09 | AtABA24: RX234F (payload7) →1CB0; BD780 atBD811 →07E6 (heating candidate) |
| GET65 | internal73→A7D48 | 0770→reply payload10 ifCFB18 returns0 |
| GET79 | internal87→A8BCC | 07E6→reply payload7 ifCFB18 returns0 |

Payload index0 is the command. These are proven field-to-buffer relationships, **not a complete operational write recipe**. The branches also copy neighboring settings. BD166 invokes the import only for2373=6; these imports do not locally clamp the pump byte to1–5. A safe single-field transaction and all defaults/validation/persistence remain unqualified.

## Settings session rather than unrestricted writes

CEE20 dispatches session state2372 through0..12. CF66E recognizes internal34, which the descriptor map ties to **SET C8**, distinct from A3 and from GET configuration C9 in public research. CF75C reads RX234A (payload2), CF760 reads234B (payload3). CF704 applies eligibility checks; CF7C8 selects a category into4981 from request bits. CF832 compares4981 with RX2357 (payload15).

In session states2/3/5, CF04C/CF0E0/CF1A4 check that the input is a recognized settings command and category matches before invoking A90F8. **CF67E is only a recognized-settings predicate**, not itself the write handler: internal05..33 map to return1 atCF6FA; other/default maps to return0 atCF6FE.

Readback CFB18 also requires category match. States7/8/10 return busy1; state9 returns success0; others/mismatch returnFF. This grounds P81's FF observations without treating zero-filled following bytes as settings. CEEA8 also reads shared service state0414 into3248; CF8D4 checks service1002 and session code uses its low command bits. Complete session choreography and caller/persistence validation remain PARTIAL. CN105 and the D-path demonstrably interact with shared state, but shared state is not unrestricted external access.

## Ordinary settings converge

- **Heating mode:** SET32 maps to internal01. BBCB6 checks flag bits08/10, takes payload6/7, validates viaA468E (<6 and active flag), and callsBBE92. BBE92 writes3913/3914 and shadow3F02/3F03. The D-path consumers BBC34 andBBC74 read packed050B mode fields and also callBBE92 (BBC6C/BBCAF). This is actual internal convergence. Exact display wire bytes and full translation-table semantics are not qualified. Public CN105 sources independently identify0/1/2 as room/fixed-flow/curve.
- **DHW normal/ECO:** SET32 flag04/payload5 →BC02C→A462A (<2)→3912. GET26 packerA612C provides mode readback throughA4610. Normal/ECO is not a general adjustable heating-versus-DHW priority control.
- **DHW target:** SET32 flag20/payload8–9 →BBA48→A46C4→3906. Target readbacks exist throughGET09/26; this package did not retest them physically.
- **Boost and holiday:** SET34 internal03 reachesB95A4/B95E0 andC0A98/C0AD0 respectively. GET28→A61F2 reports the corresponding state family. Public inhibit controls shareSET34 but require server-control semantics; this package does not equate a SET ACK with effect.
- **Energy configuration readbacks:** GET71→A8290 includes heater configuration075B and pump1 power07D3; GET72→A830C includes pump2/3 power07D5/07D6 and adjustment07D7. Both are session-gated byCFB18. Encoding of the signed adjustment and complete setters is not qualified here; do not reuse decompiler arithmetic without operand checks.

The static link is stronger than “a matching constant exists”, but does not establish physical21.00 compatibility or authorization to actuate.
