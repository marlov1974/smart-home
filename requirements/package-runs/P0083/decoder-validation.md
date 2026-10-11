# P0083 decoder qualification

Scope/identity: [provenance](provenance.md). **PASS for the tested subset, not the complete M16C decoder.**

The original module described absolute/relative direct calls and jumps as computed flows, losing static targets. `patch_module.py` hash-gates the original file and adds target-export operand subtables for JMP.s/b/w/A and JSR.w/a. No upstream source is redistributed. SLEIGH compilation succeeds; 20 pre-existing empty-semantics constructors and four redundant extensions remain.

`P83Vectors.java` passes 11 synthetic checks: NOP, RTS, REIT, absolute jump/call to D5540, positive/negative relative byte jumps, word jump/call, short jump, and far word load from 81234. Checks cover length, mnemonic, direct target, call category and far operand. This is not a proof of every instruction's p-code.

The missing instructions at 8BE27 (`E1 24`) and 9B038 (`E1 54`) are immediate word rotations by +3 and +6 of A0. The manual's ROT description specifies 16-bit rotation and S/Z/C effects. Added positive/negative immediate ROT.w semantics pass **20 emulator cases**: rotations +6,+3,-1,-8 across 8123,1234,8001,ABCD,0000, checking result, carry, sign and zero. This repairs two gaps and expands their existing function bodies, rather than declaring them data. Full ±1..8, every addressing mode and the pre-existing byte-rotate implementation are not qualified.

Two attempted compilation runs before success exposed a configuration-directory sandbox denial and invalid `//` SLEIGH comment; corrected to `#`, recompiled, then ran the tests. No failed compiler output was used for analysis.

Important remaining limitations:

- Decompiler calling convention and near/ram aliasing produce wrong argument/pointer expressions. For example `PUSH #8; PUSH #3A38` is the far pointer **83A38**, not RAM 3A38. Assembly operands control the conclusions.
- Some switch tables still require manual recovery. Do not infer unsupported code from absent decompiled branches.
- Sparse image, possible data/code overlap and unverified board identity remain P82 limitations.
- New indirect callback roots are anchored in bounded ROM descriptors, not guessed by arbitrary opcode sweeps. A fresh P82 copy plus deterministic seeds reproduces the final export. Exploratory fragments at CF9E4/CF9EA were discarded and are not in the final replay.

Reproduction is in [reproduce.md](reproduce.md); exact artifact checksums and repeat comparison are in `verification.json`.
