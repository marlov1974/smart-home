# FTC6 offline analysis — P0082

An S-record termination address is not necessarily the reset vector. Preserve sparse addresses and compare imported address-byte hashes. Test processor modules with documented instructions before trusting their call graphs; a plausible mnemonic can still have incorrect flow metadata. Distinguish decimal service selectors from direct GET bytes. Status 3 may be a structured format, not unsupported functionality. Match firmware identity/version before transferring any address or semantic claim. Full vendor images and disassembly stay local.

## P0083 lessons

Direct branch metadata and instruction p-code need separate tests. Synthetic rotate emulation must check carry/sign/zero as well as result. Far-pointer arguments in decompiled C can collapse into misleading RAM addresses; inspect stack operands. Table-seeded function discovery is safer than treating arbitrary byte offsets as entry points.

A service query may change accounting state: FTC image candidate 20.01 selector 532 snapshots and clears energy banks, and 340 mutates initialization state. Exclude these from read-only probing. Even normal counter queries can fold pending accounting into RAM.

A dated energy snapshot is not a live/current-day counter. Trace source banks, rollover trigger and timebase before assigning that label. Session-gated FF readbacks do not mean numeric zero or unsupported hardware. PWM readback alone does not prove actual hydraulic flow or direction. These findings must be revalidated across firmware revisions.

## P0084 lessons

A shared diagnostic-ring writer can resemble a transport wrapper: distinguish RX/TX logging from the actual peripheral path. FTC's 9D8FE records both directions; UART2 uses separate receive/transmit buffers and interrupt handlers. Use vector entries including the prologue, not a plausible ENTER in the middle of an ISR.

Shared internal setters do not imply transport parity. Preserve session/category gates, arbitration, direct-A3 restrictions and separate display-local behavior. Setting bytes staged by a CN105 command are not a complete safe write transaction, especially when neighboring fields are copied too. Similar response latency cannot identify a physical connector. Check indirect switch bounds from actual operands, and replay from a clean project after exploratory corrections.
