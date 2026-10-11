# P0084 function design

Reuse P83Seed/P83Trace without changes for bounded local project exploration. Add package-local compact evidence extraction only if it improves reproducibility: pinned image/reference input, address-only output, no full vendor code or live operations. Verify deterministic output and input hash rejection. No production functions changed.

Implementation refinement: P84Switch reconstructs only three operand-verified relative switch tables (9F315/25 entries, CF695/48, A910A/48). It disassembles local branches and records computed-jump references; it does not claim that Ghidra C recovers every switch. Bounds outside these exact tuples are rejected. An exploratory run used 26 instead of25 entries for the first table; its extra target is discarded by fresh-project replay. ISR roots are their vector entries A37A8/A397C, including PUSHM, rather than the following ENTER instruction.

Compact evidence tool will hash-gate the image, derive selected protocol routes, switch targets, UART vectors and record operands needed for claims. Repeated output and intentionally wrong input verify the contract. Full exports remain local.

## Final tool contracts

| Function/tool | Input and output | Side effects and verification |
|---|---|---|
| P84Switch.run | Exact owner/branch/table/count tuple → targeted jump references | Changes only local Ghidra database; bounded table targets checked; incorrect26-entry tuple rejected before mutations in read-only negative test |
| evidence.derive | Hash-qualified binary plus private instruction index → small JSON routes/vectors/operands | Read-only derivation; rejects wrong image, out-of-range addresses, nonunique routes and missing operand evidence |
| evidence CLI | Same inputs plus output path | Writes compact JSON only; repeat tested |
| verify_local | Private workspace inputs and exports → verification.json | Runs assertions/negative guards, compares273 files and writes report; no network or device I/O |
| roots.txt / targets.txt | Reviewed hexadecimal addresses | Controls P83 seed/export reuse; not an external device address list |

No production functions were added, modified or removed. Existing P83 tools were reused without modification.
