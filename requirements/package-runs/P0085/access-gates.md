# P0085 access gates

## CN105 settings eligibility — new detail, CONFIRMED static20.01

CF704 reads three SETC8 payload bytes via CF758/CF75C/CF760. Payload0 is the command:

- payload1 (2349) must be0 or1: CF764.
- payload2 (234A) must be0..3: CF77E.
- payload3 (234B) must have at least one of bits0..6 set: mask7F.
- if internal0900 equals2, any payload3 bit in mask5F rejects eligibility. Combined with the previous mask, only bit5 can be selected in that internal state; bit7 is not checked by these masks. The human operating-state label for0900=2 is not established here.

CF7C8 chooses the **lowest set category bit**0..6, storing category1..7 in4981. It does not apply all set bits independently. CF832 additionally requires incoming payload15 to equal4981. CF846 maps category1..7 directly to2373=1..7; category6 therefore reaches the previously found BD166 import phase2373=6, including BD296/BD780 pump settings. This completes a missing category-to-import link; it does not validate a safe write transaction or persistence.

CEE20/CF04C/CF0E0/CF1A4 constrain the session state, CF67E restricts recognized setting IDs, and CFB18 restricts GET success to category match and state9 (states7/8/10 return1; other states/mismatchFF). Shared service1002..1005 state also participates. Complete choreography and failure recovery remain unqualified. No byte sequence is recommended for live writes.

## A3 and control gates — retained, confirmed

CEDD6 rejects selector200 or>=700 specifically for internal8F (A3); CEBEE returns format6. CEA8A/CEAEC prioritize pending D-side service requests over CN105 A3.8B794 can return format6 during that arbitration. None proves complete feature absence.

Ordinary SET32/34 and session SETC8 are separate paths. A468E validates heating mode (<6 plus active flag), A462A validates DHW mode(<2). Public SET34 inhibit semantics require server-control state; P85 does not claim to have re-proved every native arbitration branch. See P84's settings trace for field chains.

## Alternate protocol access — new code evidence, connector UNKNOWN

UART1 diagnostic9E77A requires3D4C=1 and idleTX3D53=0 for reads and diagnostic subrequests. Low-nibble0 establishes that session; invalid command resets it.5-byte checksum and UART receive-error checks precede dispatch.9E938 is a bounded-address read helper;9D88C selectorF0 reaches the ring containing CN105 and D traffic. This is diagnostically broader than the mapped normal GET list, but **does not prove CNIT/CNRF privileges**, a bypass of A3 filters, or additional heating-setting access.

Normal UART1 mode52 reaches8ACFC: a packed14-bit address selects remapped memory regions, a two-entry allowlist for part of the range, or a direct byte load at8ADB7. Modes45/46 enter service loops. Exact operational effects and connector are not qualified. No attempts were made to enter them.

UART0 requires a completed valid receive record before C4D04 hands data to4455. C921C/C9278 use a38-row handler table at8740C; C943E/C94A6 use a separate transmit table87A60. Their indirect callbacks and state machine have not been fully attributed to user functions. A shared internal symbol or a readable buffer does not prove externally reachable write permission.
