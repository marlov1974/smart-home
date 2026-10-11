# Settings acknowledgment is a D-path event

P88 closes the provenance of P86's opaque CF978 acknowledgment. It does **not** yet provide a complete autonomous CN105-only settings transaction.

The observed static chain is D receive08BD →9F152 translation →9F2EA normalized14 →9F788 bank0 →A0662 →050A..050E plus0509.bit7 →8B7E2 →0414 →CEEA8 →4987/3248. Raw low nibble0B maps to normalized14, but acceptance still depends on the25×25 transaction matrix and high-nibble transaction class; this is not a ready-to-send packet.

8B7E2 distinguishes two word layouts at050B:

| Condition | Selector extraction | Event0414 |
|---|---|---|
| bit0=0 | `(word>>3)&03FF` | selector, high tag0 |
| bit0=1,0630.bit1=0 | `(word>>6)&03FF` | selector OR4000 on accepted8BD02; rejected transfer uses7FFE |
| bit0=1,0630.bit1=1 | `(word>>6)&03FF` | selector ORC000, separate8BC5C path |

The high tags are proven by assembly BSET at8B8BF/8B8CA. The old decompiled C drops them because of signed FB-bit displacement defects. They must not be read as tag0.

CEEA8 splits0414 into tag4987=`word>>14` and number3248=`word&3FFF`. Thus **CF978 means accepted tag1, selector0**, not an arbitrary transport ACK. For the extended selector0 case,8D694 intentionally bypasses its nonzero-selector table while reporting success, provided8BD02's address/role/direction gates admitted that call. This is the concrete no-data/end marker behind the previous missing edge.

CEFA8 instead requires tag0, selector1002 and050D low2 bits:0 for write-direction4980=0,2 for read-direction4980=1. It then enters state2 or7 respectively. CF8EC/CF904/CF91C similarly distinguish tag0 services1003/1004/1005. CN105's external A3 filter rejects selectors>=700; numeric1002 is not an externally usable CN105 A3 command.

The special1002 route is outside8C0B4's ordinary local equality cases:8B980 reaches8BB18, and for0630.bit1=0 calls8D36C with1002,4980 and040B low2 bits. 8D36C selects a response from806FE/80718 based on session state and direction. This avoids incorrectly declaring1002 absent merely because the local selector switch has1001 then1003.

8BD02's extended transfer requires the addressed/role branch (low dispatcher argument6), transfer-kind argument2, and equality between4980 and050B.bit5. 8D694 maps nonzero selectors using33 bounded ranges at807EA, eight-byte records, each mapping to three-byte staged records at`1940 + bank*512 + offset + (selector-first)*3`. Direction1 copies the incoming format nibble plus two value bytes into staging; direction0 reads the staged triple. Unmapped selectors report failure. Several ranges deliberately alias storage, so they are not independent settings without category/session context.

The request is advertised through **internal service1005** at8D232. With0630.bit1=0 and2372=1 it returns format1 and value `((497F<<2)&01FC) | (4980!=0)`. Thus mask20 hex/category6 yields raw128 for write and129 for read. Outside state1 it returns format6 (raw0 for write,1 for read); the other0630 profile returns format6/raw0. This is a concrete polling interface by which the D peer can learn that CN105 requests a category transfer. It is not reachable through the external CN105 A3>=700 filter.

Concrete consequence: CN105 settings are coordinated with D-path events. A GET in states7/8/10 reports busy and can move the state; only state9 exposes data. FTC's1005 advertisement,1002 start and selector0 transfer-end acknowledgment are now connected. The next unresolved edge is **the peer's scheduling of1005 polling and generation of the1002/transfer/end-marker sequence**, including close/retry behavior for each category. The peer implementation is not in this FTC image. No guessed CN105 bytes, cable migration or live test was performed. Persistence, complete neighboring fields and rollback remain independently unqualified.

Continuation correction: bit5 is not complemented; see settings-apply-order.md and the STZX regression test. The33 mapping records are itemized in settings-transfer-map.md. Import can occur before handshake completion; reset-to-idle is not a rollback guarantee.
