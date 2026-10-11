# P0086 — physical UART1 binding

Analytical **PARTIAL**, connector assignment **UNKNOWN**, physical **NOT RUN**. MCU register family strongly matches M16C; exact device/package remains unconfirmed. Earlier R5F364AENFB256KiB candidate conflicts with349,889populated imagebytes; capacity-compatible R5F3651TNFC is not positive identification.

Official Renesas M16C/65 hardware manual R01UH0135EJ0210 table1.10 (100-pinpackage, printedp17): P6_7=TXD1 ispin31(FA)/29(FB), P6_6=RXD1 pin32(FA)/30(FB). These are **conditional package candidates**, not confirmed pads on thisFTC. UART1 registers0258..025F support peripheral identity, not physical connector identity. Exact top marking and package orientation are needed before using pin numbers. M16C/60 software manual supports operand semantics independently of this package assumption.

No exact-board schematic or documented connector→component→MCU continuity path has been established. UART1→CNIT UNKNOWN; UART1→CNRF UNKNOWN; CN105 is separately proven working withProcon/UART2, not available evidence forUART1. D timers are another path, not provenCN22. User's originalWiFi adapter is **MAC-597IF-E**, attached toCNRF and never working; likely wrong installer port is an installation hypothesis, not UART1 ownership proof.

Available Procon board photos do not resolve FTC mainboard routing. Smallest missing observations: a legible FTC main MCU top marking withPCB/revision and packageorientation, followed by one unpowered continuity trace from the exact UART1RX/TX candidate through any resistors/transceiver to the candidate connector. No additional adapter-model question is needed.

A qualified operator must establish ground/reference, isolation, supply versus signal pins, logic amplitude, idlepolarity and direction. Official connector supply observations in P85 (CN22 roughly10.4–13.7V;CN105/CNRF supplypair roughly11.5–13.2V) are not TTL voltage specifications. CNITblue5pin purpose stillunknown. Do not connect USBTTL orRS485 as a probe. A passive high-impedance isolated measurement precedes any transmitter or adapter selection. DTR/RTS behavior on adapteropen remains unqualified; the CLI cannot openserial.
