# FTC6 port/access research — P0085

Offline tooling only. `tools/ftc6/p85/evidence.py::derive(binary,instructions)` checks image SHA, eight vectors and42 exact operand excerpts; emits compact evidence with diagnostic length table and explicit unknown port assignments. CLI writes JSON. `verify_local.py::verify(binary,first,second,report)` checks all export hashes, requested function coverage, evidence equality and rejected wrong/missing/changed inputs; writes verification.json. No device/network access. See P0085/reproduce.md for private prerequisites.

New analyzed firmware functions (candidate20.01, not modified):

| Family | Functions | Contract/evidence |
|---|---|---|
| UART0 |C4C7E,C4DFC,C4EE8,C4F18,C4D04,C5004 |Init, RX, LE length, checksum, RX handoff, TX; buffers3FB3/41FA/4455; connectorUNKNOWN |
| UART0 dispatch |C5954,C921C,C9278,C943E,C94A6 |State processing and38-row RX/TX callback tables; complete semanticsUNKNOWN |
| UART1 |8A504,8A528,8AF86,9E642,942AE,944C6 |06D8bit7 selects normal or diagnostic personality across init/task/ISR |
| Diagnostics |9E66E,9E77A,9E938,9D88C,9E850,9E87A,9E8E0 |Checksum-gated5-byteRX, session, memory read, ring export, TX/checksum; physical port and far-address semantics unqualified |
| Normal UART1 |8B200,8B3C2,8B2E8,8ACFC,8A668,8ADF8 |RX/TX/format validation, mapped memory read and service loops; no operational recipe |
| D timers |942E6,C1456 |Correct TimerB1/TimerA0 ISR entry points calling9E9AE/9F04C; not proofCN22 |
| CN105 session |CF704,CF764,CF77E,CF7C8,CF846 |Payload eligibility, first-set-bit category, category→import state; live procedure not qualified |

Research evidence and limits: [P0085](../../requirements/package-runs/P0085/findings.md). Tests cover reproducibility and exact pinned observations, not pump behavior or complete decoder correctness.
