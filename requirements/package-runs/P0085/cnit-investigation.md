# P0085 CNIT investigation — PARTIAL

**Intended Geodan CNIT purpose is not established.** S1 p11 labels a blue five-position connector without an accessory assignment. Its test-point page does not provide a CNIT pinout or voltage. Generic claims that “CNIT means privileged service” are unsupported.

Manufacturer cross-family evidence reinforces caution: S5 uses CNIT for transmission-power functions, while naming a different connector the IT terminal. This disproves the naming shortcut, not a possible service role on Geodan. No foreign pinout is imported.

New static lead: UART1 has a diagnostics personality and a normal personality with service-oriented handlers.06D8 bit7 switches both ISR routing and initialization, making this a real alternate software mode.9E77A session/9E938 reads and9D88C diagnostic ring export offer a concrete target for later PCB identification. **UART1→CNIT remains UNKNOWN**, not confirmed and not a reason to move Procon. UART0 is another unidentified path, with an independent length-prefixed protocol. There is no justified one-UART-per-connector assignment; external multiplexing, another controller or unused functionality remain possibilities.

06D8 is derived from board configuration processing8E3DE; the physical switch number is not qualified. Do not turn the derived bit into a DIP instruction. No switch changes were performed.

The memory-read helper9E938 checks a lower bound0400 and upper address arithmetic against0FFFFF, then copies into1348. However, the exported load at9E99C uses [A0]; far-pointer/bank semantics in the M16C decoder are not fully qualified. This establishes a memory-read routine, **not proven full-flash readout**. Length-table values are1,2,4,8,16,32,64, then1 for remaining entries. No request was sent and no boot/EEPROM dump was attempted.

A suitable next evidence item is an exact FTC PCB part/revision and documented or unpowered continuity routing from CNIT through its interface components to MCU pins. The adapter's exact part number and a clear CNRF/CN105 connector photo would resolve the installation record. Passive isolated captures only after separate approval and electrical qualification; no live operations are part of P85.
