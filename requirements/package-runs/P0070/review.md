# Consistency review — WARN

M1 r2 is hardware-confirmed: operator reports heartbeat, five read-only FC04 replies were888 at2026-10-06T19:01:01–06Z. Copied raw evidence accompanies package. CN105/M3–M4 now directly requested, so previous defer-until-M1 gate satisfied. Add minimal M2 diagnostics in the same package to make bring-up observable.

Clean isolated checkout at6926f72 equals origin/main; persistent worktree retained untouched because its only untracked file is the preceding live evidence. No remote divergence.

Original USART1 init/MSP establishes PA9 TX/PA10 RX AF7, parity enabled with9-bit word (8 data + even parity), no SWAP/inversion. Original startup baud9600 is not proof of runtime baud. Independently pinned F1p reference7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5 uses24008E1, ATW connect FC5A027A02CA015D, GET0x04 with16-byte payload, response0x62 payload[1] compressor Hz. Use2400 as experimental CN105 setting, expose UART errors and RX counts. No baud scan or control command. Physical MCU/package and CN105 pin wiring remain inferred until live response.
