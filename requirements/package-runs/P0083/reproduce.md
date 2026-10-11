# P0083 reproduction

Prerequisite: P0082's validated private image and Ghidra project/tool installation, with hashes in provenance.md. Commands run from the original workspace root; `P0080/implementation-smart-home` is G2. The full binary and Ghidra outputs must remain outside public G2. Use a fresh destination when making the clean project copy; do not overwrite an ongoing analysis.

```sh
G2="$PWD/P0080/implementation-smart-home"
GH="$PWD/P0082/tools/ghidra_12.1.4_PUBLIC"
export JAVA_HOME="$PWD/P0082/tools/jdk-21.0.12.1+1/Contents/Home"
python3 "$G2/tools/ftc6/p83/patch_module.py" P0082/ghidra_m16c/data/languages/m16c.slaspec "$GH/Ghidra/Extensions/ghidra_m16c/data/languages/m16c.slaspec"
"$GH/support/sleigh" "$GH/Ghidra/Extensions/ghidra_m16c/data/languages/m16c.slaspec"
python3 "$G2/tools/ftc6/p83/make_vectors.py" P0083/private/vectors2.bin
# Fresh fixture project; reruns can use -process vectors2.bin instead of -import.
P0082/run_headless.sh P0083/private/projects vectors2 -import P0083/private/vectors2.bin -loader BinaryLoader -processor m16c:LE:16:default -cspec default -noanalysis -scriptPath "$G2/tools/ftc6/p83" -postScript P83Vectors.java -log P0083/private/vectors-final.log
python3 "$G2/tools/ftc6/p83/extract_evidence.py" P0082/private/ftc6.bin "$G2/requirements/package-runs/P0083/address-evidence.json" --targets P0083/private/repro-targets.txt
cp P0082/private/projects/ftc6tables.gpr P0083/private/projects/qualified.gpr
cp -R P0082/private/projects/ftc6tables.rep P0083/private/projects/qualified.rep
P0082/run_headless.sh P0083/private/projects qualified -process ftc6.mot -noanalysis -scriptPath "$G2/tools/ftc6/p83" -postScript P83Repair.java -postScript P83Seed.java "$(cat P0083/private/repro-targets.txt)" 3 -postScript P83Trace.java P0083/private/final "$(cat "$G2/tools/ftc6/p83/trace-targets.txt")" -log P0083/private/final.log
P0082/run_headless.sh P0083/private/projects qualified -process ftc6.mot -noanalysis -scriptPath "$G2/tools/ftc6/p83" -postScript P83Trace.java P0083/private/final-repeat "$(cat "$G2/tools/ftc6/p83/trace-targets.txt")" -log P0083/private/final-repeat.log
python3 "$G2/tools/ftc6/p83/crosscheck.py" P0081/mapping-20261010T205704Z/direct/readings.jsonl "$G2/requirements/package-runs/P0083/physical-crosscheck.json"
python3 "$G2/tools/ftc6/p83/verify_local.py"
```

The final fixture run used the existing vectors2 project with `-process vectors2.bin -noanalysis`; it passed again after the last source edit. The verifier checks deterministic derivations/exports, fixture identity, expected pass counts and rejection of a wrong image, wrong module and corrupt historical checksum. It writes verification.json. Export checksums exclude project metadata and logs. This verifies reproducibility, not correctness of all vendor code or physical behavior.

Manual review must accompany replay: operands and data references in the three trace reports justify semantics; Ghidra C alone is not authoritative. Java/SLEIGH warnings and unresolved flow limitations are recorded in decoder-validation.md.
