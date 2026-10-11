# P0083 function design and implementation

All functions are offline; no runtime firmware functions changed or removed.

| Tool | Input → output | Side effect / purpose | Verification |
|---|---|---|---|
| patch_module.py | pinned original SLEIGH → repaired local module | Writes only chosen destination; restores direct flow and ROT.w. Does not distribute upstream source. | Original hash gate, SLEIGH compilation, bad-source rejection |
| make_vectors.py | output path → synthetic binary | Local fixture generation | P83Vectors |
| P83Vectors.java | synthetic Ghidra program → pass/failure log | Decodes fixtures and emulates rotations | 11 decode/flow + 20 result/flag checks |
| P83Repair.java | qualified project → repaired gaps/function bodies | Local Ghidra database edit at two verified rotations | Clean replay, targeted export |
| P83Seed.java | address CSV, bounded depth → functions/references | Local table-anchored code discovery | Deterministic ROM seed extraction, replay |
| P83Trace.java | project, directory, address CSV → assembly, C, refs/indexes | Full vendor exports remain private | 366-file repeat comparison |
| extract_evidence.read_image/extract/targets | hash-qualified binary → compact JSON, seed CSV | No live I/O; bounded descriptor walks | Repeat equality, wrong-image rejection, expected routes |
| verify_local.py | private inputs/logs → verification JSON | Local validation and report output | Positive/repeat and negative guards |
| crosscheck.py | historical JSONL → selected fields/checksums | Validates frame length/header/checksum/command; strips full frames | 12 observations, repeat equality, bad-checksum rejection |

Implementation refinement: original direct-flow plan expanded to ROT.w when two verified code gaps blocked tracing. Synthetic emulation qualifies the added semantics. Exploratory fragment roots were removed from the final clean replay.
