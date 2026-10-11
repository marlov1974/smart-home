# Reproduce P0085 offline

Use P83's pinned Ghidra12.1.4/Java21/M16C decoder and the exact private inputs in sources.md. No network/device tool is required for analysis or verification. The legacy root launcher writes Ghidra preferences outside the workspace.

1. Copy finalized P84 `final.gpr`/`final.rep` to a private P85 project. Do not overwrite P84.
2. Use P83Seed.java with `tools/ftc6/p85/roots.txt`, depth3. Use P83Trace.java with `targets.txt` to export to a private `final/` directory.
3. Reload the saved project with `-noanalysis -readOnly`, run only P83Trace to `final-repeat/`. Compare every file. Exploratory seeds94300/C1470 are **not** final function roots: correct interrupt prologues are942E6/C1456. Final project was rebuilt from P84 to avoid split function bodies.
4. `python3 tools/ftc6/p85/verify_local.py /path/to/ftc6.bin /path/to/final /path/to/final-repeat requirements/package-runs/P0085`
5. Validate `git diff --check` and regenerate tracked file index after staging all package files. Keep binaries, full disassembly/decompiled output and projects private.

Verification intentionally checks exact opcode text as well as hashes/vectors. An initially mistyped expected CEDD6 operand was rejected (RAM3238, not a stack slot); the fixture was corrected from the reviewed assembly before final verification. No firmware or decoder was changed to make a test pass.
