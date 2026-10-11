# P0083 track A — service and transport

**PARTIAL.** The CN105-format GET/A3 request-to-response path and local/forwarded selector distinction are established. Physical UART/connector ownership of the internal tunnel, complete forwarding and all response-type semantics remain unresolved. All addresses use [this image](provenance.md).

## CONFIRMED: byte-level protocol route

A4F68 receives a completed frame buffer starting at RAM2343. A4FE0 selects one of 15 descriptors at ROM892A8 (59-byte stride): FC/41 SET, FC/42 GET, connect/config variants and 02 framing have distinct rows. A5204 tests bytes2345/2346 as 02/7A; A523C reads command at2348. A50BC uses the command lookup at84C56 and the selected descriptor's mapping to obtain an internal ID. These are byte-level matches to CN105, not a label inferred from the number A3.

Selected complete GET mappings (also machine-derived in `address-evidence.json`):

| GET command | Internal ID | Output packer |
|---|---|---|
| 07 | 3B | A5724 |
| 15 | 49 | A5BF8 |
| 65 | 73 | A7D48 |
| 79 | 87 | A8BCC |
| A1 | 8D | A8E38 |
| A2 | 8E | A8EB6 |
| A3 | 8F | A8F34 |

A4F68 saves the returned internal ID in2340/2341. For8F, CEAEC's mode2 branch calls CEB98. CEB98→CEBA8 reads selector bytes2349/234A through A4A10 (big endian) into3238, then→CEBEE. The selector class comes from8C04E's upper-bound table at806AC. Class2 calls local8C0B4 atCEC8A. Class1 submits viaCED82 into0409/040B–D and waits for the shared asynchronous path; this is not a direct local sensor read.

Local8C0B4's three-byte result (format,value0,value1) is copied at8D346 viaD4D0C. CED66 saves selector3240, format3244 and value bytes3242/3243. A8F34 builds payload `A3, selector_hi, selector_lo, format, value0, value1, ...`, length16. Value order is little endian for the numeric two-byte handlers: A4A44's byte swap plus A8F34's stores preserve3242 first,3243 second.

A535E selects a16-byte output descriptor at84D56, then indirect calls its header, payload and checksum functions. A9080 writes FC/02/7A, the descriptor supplies reply type62 and total length22. A90A0 sums bytes1..20, negates modulo256 and stores byte21. A535E→9D8FE with selector46 and mode2 divides the frame into internal pieces. The last hardware UART/physical CN105 versus CN22 bridge is **NOT ESTABLISHED**; do not infer the physical port from this transport wrapper alone.

## Four dispatcher call sites

| Call site | Owner/upstream | Established role |
|---|---|---|
| 8BAB9 | 8B980 ←8B7E2 at8B8AA | Packed request at050B, class selection, local result into0410–12 |
| 8BBD6 | 8B980 | Second local branch of same packed-request state machine |
| 8BF6B | 8BDE0 ←CEAEC | Incoming389A/38A1–4 path, local handling for classes9/10 |
| CEC8A | CEBEE ←CEB98 ←CEAEC | CN105-format internal8F, selector3238, class2 local dispatch |

After ROT repair,8BDE0 demonstrably extracts format `(word38A1 >>13)&7`, value38A3/38A4 and selector `word38A1&3FF`. Classes1/3/4/5 consume this returned value; classes9/10 call the local dispatcher. Distinct transport/state paths share a service function. Packed050B/display/internal traffic is not automatically a CN105 GET.

## Compact selector evidence

| Decimal selector | Class/path | Data/result evidence | Confidence |
|---|---|---|---|
|17,18,19,27,28,52,54|1, table806AC (upper bound149); forwarded path|Absent as local cases is expected.8BDE0 receives externally supplied format/value; source-side implementation is not in this dispatcher.|CONFIRMED routing; final sensor source UNVERIFIED|
|175|2;8C57C|Format1 bitfield, including bit0 fromRAM3A34, bit1 from06A9 and other output states|CONFIRMED|
|176|2;8C624|Format1 bitfield from051E/0515/0542/0530/0539/054B/0554 comparisons|CONFIRMED; names of every input UNVERIFIED|
|506|2;8C8FE|Format2, signed0664 /100|CONFIRMED; P81 return-temperature corroboration|
|511|2;8C95D|Format2, signed0662 /100|CONFIRMED; P81 flow-temperature corroboration|
|540|2;8CC6E|Format2, unsigned322E /100|CONFIRMED; primary water flow corroboration|
|550|2;8CC81|Format3,39DE plusA22FC-derived data|CONFIRMED format; complete fault-display encoding UNVERIFIED|
|340|2;8C6F2|Sets3ADC=1, returns format7|CONFIRMED mutating; excluded|
|532|2;8CC0C→CDF46|Copies six energy counters to published bank, zeros original bank, saves date; format7|CONFIRMED mutating; excluded|

Format1 is not universally an integer: versions/bitfields and energy BCD use it. Format2 has signed numerical examples. Format3 is a real locally generated result, consistent with P81 fault-history/550 replies. Format4 appears in P81 service0/107 and can traverse the forwarded path, but its full display semantics are **NOT ESTABLISHED**. Format6 is the local default at8C0BA and also produced by eligibility/timeout paths CED4A/CEBEE; it does not uniquely prove that a selector is absent. Format7 can acknowledge a mutating action. P81's API treated only1/2 as established, explaining its `UNSUPPORTED` classification for valid3/4 replies; it was not a firmware capability verdict.

No proposed new bytes were sent. The static routing is specific to20.01; P81's21.00 corroboration is explicitly separate.
