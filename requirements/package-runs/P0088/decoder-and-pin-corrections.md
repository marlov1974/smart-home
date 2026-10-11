# P88 corrections, preserving historical P87 outputs

Two operand checks prevent plausible but false hardware conclusions.

1. P87 continuation described9C46C as samplingP6.3 and controlling UART0 registers0264/0265. At9C498 the bytes `7E BF 8B 1F` decode BTST bit3,address03F1; M16C/65 register map says03F1=P9, whileP6=03EC.9CA48/9CA4D set/clear bit4 at03F1. Therefore this sampled path is **P9.3 input / P9.4 output**.0264/0265 are **UART2** special mode4/3, notUART0. These corrected register identities do not by themselves identify CN3C or prove all paths are simultaneously enabled. P87 published files remain unchanged.

2. UART1 snapshot9DAF0 initially decompiled as changing peripheral026D. Actual9DC83 loadsA0=6,9DC8A bytes `7E 2C 67 13 FA` perform BMNE/NZ base1367[A0]. M16C60 software manual chapter2.5, printedp31 defines address-register-relative bit addressing: byte=base+(A0>>3),bit=A0&7, modulo16-bit address. Thus this is **response byte1367 bit6**, not026D bit3. Current module instead computes(base+A0)/8 and a mask fromimmediate&3. Do not report an observed UART side effect from that decompilation.

`addressing.py` and boundary tests encode the manual rule; no shared Ghidra module has been modified. Other such indexed-bit decompilations require requalification. Earlier P87 EXITD and signedFB displacement defects remain applicable. Static C output is supporting evidence; instruction operands and architecture semantics decide these conclusions.
