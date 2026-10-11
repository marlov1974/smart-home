# P0088 — isolated bit-address decoder repair

The user requested continuing with the decoder itself after repeated manual corrections. The repair is an opt-in language variant `m16c:LE:16:p88-bits`; the installed baseline language, P86/P87 projects and production firmware are unchanged. The package patcher rejects any source other than qualified SHA256087e6afb29a7625e789b30467a12cad4ab2c2731e08a98c914969a308df3f46f and requires a new destination.

## Corrected shared operand semantics

- FB-relative bit addressing: sign-extend the encoded5-bit byte displacement (-16..15), rather than treating it as0..31. Use a separate signed token so SB's unsigned form is retained.
- Address-register-relative forms: effective byte is base+(An>>3), modulo65536; selected bit isAn&7. The old code divided the base together with the index and used immediate&3 for the mask.
- Address-register-indirect form: retainAn>>3 but use all three bit-index bits, notAn&3.
- SB-relative16-bit packed form: useSB, notFB, as the byte base. This adjacent constructor error is covered by the same bounded proof.

Reference: supplied Renesas M16C/60 software manual, bit addressing description printedpp14,30–31; negative FB displacement follows the bit-instruction addressing range. No general instruction semantics or EXITD repair is included.

Patched spec SHA256:1395807e49d7ef74e368fbd97b6aa0ca7a9cbeba6abe9843b68aa8739385e358.

## Verification

`P88BitProof.java` executes468 synthetic BSET cases against the actual Ghidra p-code emulator. Each case checks the entire64KiB near-memory space, so an incorrect extra write also fails. Cases cover all32 FB displacements and8 bits; bothA0/A1; indirect,8-bit-base and16-bit-base addressing; high index bits;16-bit address wrap; and SB offsets with SB deliberately different fromFB. These validate the shared address/mask operands through BSET, not every flag behavior of every bit opcode.

Two independently imported raw-binary projects pass. The unmodified baseline fails case0 (FB-16), providing a negative control. Compiler warnings about pre-existing NOP constructors remain; no compile errors occurred. Automatic MOT import initially chose the wrong loader and failed, so both new proof projects explicitly import the SHA-qualified binary at80000; no historical project was converted.

Five selected routines were re-decompiled in the separate fixed project:

|Routine|Before|After|
|D3E44|Incorrect constant false|39EA==0|
|D3E5E|Incorrect constant false|3D07==2 OR3A02==2 OR3A2C==0|
|D3E8A|Seven conditions lost|All seven threshold tests and7F mask visible|
|984D2|False destination075A.bit3|Correct destination3ACF.bit1|
|923BC|Local gate masks lost|Local gate masks retained|

The corrected C now supports the earlier manual predicate model. It still does not establish every inferred parameter type; D3E8A's result is consumed as a byte, although Ghidra infers a wider return. Other known decoder defects remain. Use this language variant for future targeted bit-sensitive analysis, record its hash, and do not silently mix old/new exports.

## Reproduction

1. Run `python3 tools/ftc6/p88/patch_bit_decoder.py <qualified-extension> <new-extension-directory>` in the local Ghidra Extensions directory; compile its `data/languages/m16c.slaspec` with Ghidra `support/sleigh`.
2. Import the private binary with `-loader BinaryLoader -loader-baseAddr 0x80000 -processor m16c:LE:16:p88-bits -noanalysis` into a new project. Run `P88BitProof.java` from the P88 script directory.
3. Use P83Seed/P83Trace read-only tooling with rootsD3E44,D3E5E,D3E8A,984D2,923BC on that project. Compare against private old exports and the named predicate model. Do not publish full vendor listings.
