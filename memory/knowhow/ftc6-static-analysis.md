# FTC6 offline analysis — P0082

An S-record termination address is not necessarily the reset vector. Preserve sparse addresses and compare imported address-byte hashes. Test processor modules with documented instructions before trusting their call graphs; a plausible mnemonic can still have incorrect flow metadata. Distinguish decimal service selectors from direct GET bytes. Status 3 may be a structured format, not unsupported functionality. Match firmware identity/version before transferring any address or semantic claim. Full vendor images and disassembly stay local.

## P0083 lessons

Direct branch metadata and instruction p-code need separate tests. Synthetic rotate emulation must check carry/sign/zero as well as result. Far-pointer arguments in decompiled C can collapse into misleading RAM addresses; inspect stack operands. Table-seeded function discovery is safer than treating arbitrary byte offsets as entry points.

A service query may change accounting state: FTC image candidate 20.01 selector 532 snapshots and clears energy banks, and 340 mutates initialization state. Exclude these from read-only probing. Even normal counter queries can fold pending accounting into RAM.

A dated energy snapshot is not a live/current-day counter. Trace source banks, rollover trigger and timebase before assigning that label. Session-gated FF readbacks do not mean numeric zero or unsupported hardware. PWM readback alone does not prove actual hydraulic flow or direction. These findings must be revalidated across firmware revisions.

## P0084 lessons

A shared diagnostic-ring writer can resemble a transport wrapper: distinguish RX/TX logging from the actual peripheral path. FTC's 9D8FE records both directions; UART2 uses separate receive/transmit buffers and interrupt handlers. Use vector entries including the prologue, not a plausible ENTER in the middle of an ISR.

Shared internal setters do not imply transport parity. Preserve session/category gates, arbitration, direct-A3 restrictions and separate display-local behavior. Setting bytes staged by a CN105 command are not a complete safe write transaction, especially when neighboring fields are copied too. Similar response latency cannot identify a physical connector. Check indirect switch bounds from actual operands, and replay from a clean project after exploratory corrections.

## P0085 lessons

Do not map physical ports by elimination from UART numbers. One peripheral can have multiple protocol personalities (UART1 here), and similarly named connectors can have unrelated functions across Mitsubishi product families. A diagnostic memory-read path proves code capability, not connector access or complete flash readout. Keep electrical mapping, packet validation, session eligibility and per-function reachability as separate evidence layers.

An operator wiring correction supersedes a package premise: the reported CNRF WiFi installation is now probably installer miswiring, not evidence that CNRF supports MELCloud/CN105. Preserve the corrected provenance explicitly. Exact reset INTB and vector prologues resolved the D timer roots; mid-ISR exploratory seeds must not enter the final project.

## P0086 lessons

Inspect the final response packer as well as its numeric helper. The 20.01 odd energy helper computes four digits, but the service handler zeros two before transmission. Pair resolution is ten raw units. Forced reads divide pending accounting and discard remainders in calculation mode 1; repeating the high half can bias accounting. “Read intent” does not mean an operation is observationally neutral.

A wide parser address and a 32-bit intermediate do not prove a far memory access. At9E99C, MOV.b [A0] uses only16 bits despite the upstream ADD/ADC. Check actual load bytes against the architecture manual and emulator before trying flash addresses; an apparent flash read may alias MMIO.

A firmware log may be destructive and incomplete: this diagnostic reader drains its ring, flags loss without a count and omits the original CN105 checksum. Preserve raw fragments and unknown timestamps; do not retry drains or synthesize missing bytes as observed evidence. Session GET callbacks can also advance state. Keep an observer model distinct from a qualified wire transaction.
