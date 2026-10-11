# P0082 findings — partial completion

Tool installation, input validation and reproducible initial M16C analysis succeeded. Full acceptance remains **PARTIAL / UNKNOWN** because exact MCU/board attribution, complete decoder semantics and requested control/energy paths are unresolved.

1. **Confirmed:** sparse image integrity and coherent M16C startup at D5540. ID bytes match PACIC02.
2. **Strong hypothesis:** 8C0B4 is a service selector dispatcher. 506/511/540 formats and scaling agree structurally with P0081; 550 explicitly produces format 3. Its two payload bytes are not safely interpretable as an ordinary little-endian numeric value yet.
3. **Confirmed static behavior:** selector 340 mutates RAM; do not treat all service queries as read-only.
4. **Confirmed:** setting path strings are indexed by code at C96E6. **UNKNOWN:** file layout and relationship of individual fields to pump levels.
5. **Not found in established flow:** a CN105 GET 07/A1/A2 response packer or a proved write path for heating/DHW water-pump level 1–5. Occurrences of A1/A2/A3 in the service dispatcher are decimal 161/162/163, not evidence of the direct GET path.
6. **UNKNOWN:** current-day consumed/produced accumulators, update cadence and COP availability. P0081's stale dated A1/A2 values and increasing GET07 field remain separate physical evidence, not disproved by this search.
7. **Identity uncertainty:** [R5F364AENFB](https://www.renesas.com/en/document/mah/m16c64a-group-users-manual-hardware) is the 256 KiB program-ROM variant, incompatible with straightforward placement of this 349,889-byte populated image into its internal ROM alone. [R5F3651TNFC](https://www.renesas.com/en/products/m16c-65/part-details/r5f3651tnfc-u0) has 768 KiB and M16C/60 CPU, so capacity fits; this does not prove board identity. The cited board photographs are not present among these two uploads.
8. **Version mismatch:** image header 20 01 00 00 versus observed 21.00 in P0081. Never transplant these RAM addresses to installed firmware.

No pump, Procon, Shelly or network equipment was accessed. No vendor image, derived full binary or full disassembly is published.
