# P0085 protocol matrix — PARTIAL

All new code facts are static20.01; connector ownership remains separate. [Evidence](address-evidence.json), [sources](sources.md).

| Port/path | Bitrate / signaling | Framing and checksum | Handshake / dispatch | Evidence and limits |
|---|---|---|---|---|
| CN105/UART2 |U2MR65 means8E1, internal clock, non-inverted at MCU; C0=11 disables CTS/RTS and selects divided clock; BRG67. Absolute baud not requalified in P85 |FC/type/02/7A/length, payload/checksum; P81 physical replies and P83/P84 checksum qualification |Normal41 SET /42 GET lookup84B56/84C56, descriptor892A8; separate SETC8 settings session |RXFFD40→A37A8→026E→190C→2343→A4F68; TXA535E→2359→1922→A393C/A397C→026A. MCU8E1 is not Shelly/Procon RS4859600 8N1 |
| CN22 |Electrical main-remote bus documented; baud/encoding UNKNOWN |UNKNOWN on this connector |UI documented; exact transport/commands not assigned |D is provisional, not established CN22 |
| CNRF |Supply documented; signal levels, bitrate, framing UNKNOWN |UNKNOWN |Wireless receiver role; no proved MELCloud handshake |Installer miswiring hypothesis explains prior discrepancy; equal protocol not demonstrated |
| CNIT |UNKNOWN |UNKNOWN |Potential diagnostic/service role, unassigned |No connector-specific packet recipe established |
| D-path |P7.7 sampling +timerA4-controlled output; not demonstrated RS485/TTL |Six bytes; sum0 orFF selects receive status40/80; parity/symbol logic |9F152 low-nibble mapping,9F2EA dispatch;9F788→A0662→050A..050E service state |New exact ISR roots: TimerB1 FFD6C→942E6 and TimerA0 FFD54→C1456.08FF selects branches; both require3AD2=2. Calls at94318/9431C andC148D/C1491. Still no seconds/connector proof |
| UART0, connector UNKNOWN |C4C7E:MR65=8E1,C010,BRGCF; CTS/RTS disabled; baud requires clock provenance |02 followed by little-endian total length at bytes1/2; receive capacity247 hex=583 bytes; final byte additive two's-complement checksum |C4DFC RX, C4EE8 length,C4F18 checksum,C4D04 copies3FB3→4455;C5954 callsC921C; command tables8740C (38×14 bytes),87A60 (38×21 bytes) |FFD48→942A0→C4DFC reads024E; FFD44→944B8→C5004 writes024A, buffer41FA. Tables are distinct from CN105; full semantics and wiring UNKNOWN |
| UART1 normal personality |8AF86 MR15=8N2,C010,BRGCF; CTS/RTS disabled |RX3454, TX3655; format-dependent validation8B2E8, modes45/46/52 (ASCII E/F/R); no complete frame spec claimed |8A504/8A528,8B028;52 mode reaches8ACFC memory-read logic;45/46 enter sustained service loops8ADF8/8A668 |FFD50→942AE→8B200; FFD4C→944C6→8B3C2. Not automatically wireless receiver traffic |
| UART1 diagnostic personality |9E642 MR65=8E1,C010,BRGCF |5-byte receive record; sum of all5 modulo256=0. Response1346 uses length1347 and sum0 checksum9E8E0 |9E77A low-nibble0 initializes3D4C session;1 invokes memory read9E938 with length table832BE;2 invokes9D88C or9DAC0;other resets session |06D8 bit7 chooses this path in init/RX/TX/task. RX9E66E→3D4E; TX9E850/9E87A→025A. Not FC/CN105 protocol |

UART0 length capacity is **583**, not a tested maximum accepted command length. Before length bytes arrive, C4EE8 uses that capacity as a provisional bound. No fuzzing performed.

The diagnostic path now explains P84's logging ring:9D8FE→13B0→9D8A0→1346→UART1. It is a separate transport carrying copied traffic, not the transport originally generating those CN105/D packets. Exact baud still requires fully qualified clock configuration; divider constants alone are insufficient.
