# P0084 reproduction

Use P0082/P0083's pinned private inputs and qualified Ghidra installation. Run from the original workspace root; G2 is `P0080/implementation-smart-home`. Never copy private inputs or full exports into public G2. The exact Ghidra12.1.4/JDK21.0.12.1+1/module identities and image hashes are in [P83 provenance](../P0083/provenance.md).

For a fresh replay, choose absent output/project paths (do not overwrite existing work):

```sh
G2="$PWD/P0080/implementation-smart-home"
cp P0083/private/projects/qualified.gpr P0084/private/projects/final.gpr
cp -R P0083/private/projects/qualified.rep P0084/private/projects/final.rep
P0082/run_headless.sh P0084/private/projects final -process ftc6.mot -noanalysis -scriptPath "$G2/tools/ftc6/p83;$G2/tools/ftc6/p84" -postScript P83Seed.java "$(cat "$G2/tools/ftc6/p84/roots.txt")" 3 -postScript P84Switch.java 9f2ea 9f315 9f31a 25 -postScript P84Switch.java cf67e cf695 cf69a 48 -postScript P84Switch.java a90f8 a910a a910f 48 -postScript P83Trace.java P0084/private/final "$(cat "$G2/tools/ftc6/p84/targets.txt")" -log P0084/private/final.log
P0082/run_headless.sh P0084/private/projects final -process ftc6.mot -noanalysis -scriptPath "$G2/tools/ftc6/p83" -postScript P83Trace.java P0084/private/final-repeat "$(cat "$G2/tools/ftc6/p84/targets.txt")" -log P0084/private/final-repeat.log
python3 "$G2/tools/ftc6/p84/evidence.py" P0082/private/ftc6.bin P0084/private/final/instructions.tsv "$G2/requirements/package-runs/P0084/address-evidence.json"
# Expected rejection, intentionally read-only; log must show unqualified switch bounds.
P0082/run_headless.sh P0084/private/projects final -process ftc6.mot -noanalysis -readOnly -scriptPath "$G2/tools/ftc6/p84" -postScript P84Switch.java 9f2ea 9f315 9f31a 26 -log P0084/private/rejected-bounds.log
python3 "$G2/tools/ftc6/p84/verify_local.py"
```

Manual visual checks used:

```sh
pdftoppm -f 11 -l 11 -scale-to 1900 -png -singlefile P0083/private/OCH722A.pdf P0084/private/wiring11
pdftoppm -f 63 -l 63 -scale-to 1800 -png -singlefile P0083/private/OCH722A.pdf P0084/private/board
```

The original exploratory trace7 had an extra switch row from a misread bound and ISR fragments were first viewed after PUSHM. Both were corrected before replay from a clean P83 copy: 25 entries, vector roots A37A8/A397C. No exploratory project is the final evidence source. An initial compact-excerpt address A3798 was rejected as missing and corrected to actual instruction A3797.

The repeat test compares 273 files byte-for-byte, including full instruction/reference indexes and selected function exports. Those checksums are published, not the proprietary listings. Identical output proves reproducibility, not full decoder accuracy. P83's 11 decode and20 rotation cases remain the qualification boundary; no SLEIGH opcode changes were made in P84. Switch decompilation remains incomplete; assembly and operand-derived tables govern conclusions.
