# P0088 transport inventory

Static supplied20.01; all paths PARTIAL until listed residuals close. Instruction/descriptor coverage is not a proof that every possible indirect peripheral access was found.

| Stable path | MCU driver and ownership | Framing / dispatcher | Activity / physical role |
|---|---|---|---|
|uart2|0268..026F; A36DA; RXA37A8/190C→2343; TX2359→1922/A397C|FC/02/7A and02 variants;892A8,84B56/84C56,84D56|Active conditional08F8; CN105 strongly corroborated by P81 frames|
|uart6|0298..029F; BFD16; RXBFDE4/2574→3F29; TX3F3F→258A/BFF8A|FC/04/03;48..4C,5A;8966B,86C5A|Active conditional08F9, main92482→C0458; strong CNRF/room role|
|uart0|0248..024F; C4C7E; C4DFC/C5004; buffers3FB3/4455/41FA|02+LE total length;38 RX and38 TX transaction records|Active schedulerC5954(1); strong SD/storage-controller role, candidateCN108|
|uart1|0258..025F;8AF86 normal /9E642 diagnostic; IRQ942AE/944C6|Normal8N2 or diagnostic8E1; 06D8.bit7 selects personality|Active personality-dependent; strongest CNIT candidate but unbound|
|d|P7.7 sampling;9E9AE; timerA4 output; six-byte RX08BD|9F152 normalization832EE/832FE;25x25 matrix88F65;25 branch table9F31A|Active conditional; screen/CN22 candidate; CN3C alternative must be excluded by bidirectional content|
|source-software|P87 serializer9C228→9C40E→timer ISR; P9.3 sampling and P9.4 output; separate U2 special-mode controls0264/0265|Descriptor-driven bit fields, profile-dependent demand representation|Active code; source-board/CN3C candidate; return path and full profile binding unfinished|
|uart5|0288..028F; vectors default in reviewed table|No positive active parser found in targeted work|8A728 explicitly disables0288; **not established unused**; indirect register paths still open|
|uart7|02A8..02AF; vectors default in reviewed table|No positive active parser found|8A728 disables02A8; same qualification asUART5|
|sio3|0270/0272/0273; interrupt0049|No qualified driver/parser found|Hardware available; actual use unresolved|
|sio4|0274/0276/0277; interrupt0048|No qualified driver/parser found|Hardware available; actual use unresolved|

UART5/6/7 and synchronous SI/O3/4 register identities use Renesas M16C/65 hardware manual R01UH0135EJ0210 register map and chapters23/24. Remote-control serial facilities and pin-multiplexed/indirect writes need a whole-image peripheral-access pass; the present targeted instruction listing cannot prove their absence. Default vectors can coexist with polled operation. Source-software use of0264/0265 is UART2 special-mode hardware, not UART0; physical exclusivity/profile arbitration remains to be closed.

CN22/CN105/CNRF/CNIT/CN3C and CN108 are accounted for in port-role-analysis. No one-to-one UART/connector assumption is used. Power-pair voltages from OCH722A are not signal-level specifications.
