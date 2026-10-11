# P0084 transport comparison

| Property | Documented CN22 / D candidate | CN105 |
|---|---|---|
| Connector | Main remote, two wires,10.4–13.7V DC; OCH722A p11/63 | Adapter connector; supply pins1–2 11.5–13.2V DC |
| Actual signal encoding | CN22 UNKNOWN. D code uses GPIO sampling and timer-controlled symbols, six-byte receive records | FC/type/02/7A/length plus payload/checksum, matched to P81; UART2 code found |
| RX/TX | D9E9BE/9EA6E/9EB94 and9ED22; final connector mapping unproved | A37A8/A397C interrupt vectors,026E/026A; staged190C/1922→2343/2359 |
| Parsing | D low-nibble lookup832FE, transition table88F65, switch9F31A | Descriptor892A8, lookup84B56/84C56 |
| Shared service | D8B7E2/8B980 | CEB98/CEBEE; both reach8C0B4 or shared forwarded state |
| Arbitration | Pending0509 bit7 takes service mode1 | A3 mode2 can be preempted; format6 may mean busy |
| Settings | D packed selectors participate in session state | SETC8 plus settings commands use2372/category gate; ordinarySET32/34 separate |
| Full feature parity | Not established | Not established |

Do not identify D as CN22 solely because it is non-UART or has plausible response latency: CN3C/internal control traffic is a real alternative. Do not connect TTL or RS485 directly to CN22. This package made no physical connection or measurement.

The diagnostic ring9D8FE is neither connector: it records both UART and D-path activity with different tags. Its frame slicing is not the on-wire packet format.
