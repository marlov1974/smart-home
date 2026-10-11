# P0086 — UART1 personality source

Analytical **PARTIAL**; physical **NOT RUN**. Static 20.01, identity in verification.json.

CONFIRMED:06D8 bit7 selects init8A504, task8A528, RX ISR942AE and TX ISR944C6. The bit selects9E642 diagnostic versus8AF86 normal initialization. Diagnostic session3D4C is a separate flag changed by5-byte packets after personality selection. An “open session” packet does not select parity or change06D8.

All three explicit bit writers in the targeted listing are8E5DB/8E766/8E853, variant branches of8E3DE; they use inverted3879 bit7. 8E12C loads raw08E6..08ED, inverts them into387B..3882, then transposes bits into3875..387A. In particular8E331–8E338 puts3880 bit4 into3879 bit7;3880 comes from inverted08EB. Without an override,06D8 bit7 equals raw08EB bit4 after the two inversions.

8E37E can override: signature80FF4 must equal5A5A, then nonzero ROM888DB replaces3879. Supplied image has signature0000 and888D7..DB all-zero, so this override is inactive in this image. This is a confirmed logical source, **not an identified physical DIP position**. Upstream acquisition of08EB is not resolved by direct references; an indexed/table-driven writer remains possible. No physical switch instruction is justified.

8E0F6 initialization calls8E12C then8E3DE;8E10A and8A7D4 also refresh configuration. UART initialization is reached from91310 startup. Whether all personality-dependent UART registers are safely reinitialized on a runtime change is UNKNOWN; do not assume hot switching. No reset was performed here.

8A528 has an ordinary diagnostic task path and continues into8A69E; it is not the explicitly blocking45/46 service loop. This supports continued scheduler execution, but does not prove every native heating/watchdog consequence. Changing personality removes ordinary UART1 traffic from its normal handler. Effect on the still-unidentified attached peer is UNKNOWN and must be observed in a separately authorized stage. CN105 UART2 remains a different peripheral; no live coexistence claim is made.
