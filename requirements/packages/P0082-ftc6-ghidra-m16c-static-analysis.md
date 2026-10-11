# P0082 — Install Ghidra on Mac and analyze FTC6 M16C firmware

## Scope and authorization
**Ordered for Codex execution on operator Mac:** install necessary analysis tools when permissions permit; configure/validate Renesas M16C processor support; import the operator-provided `ftc6.mot` and `ftc6.id`; perform an initial reproducible static reverse-engineering investigation. **No FTC/Procon firmware flashing, writes, live CN105 tests, network probing of heating equipment or configuration changes.** Do not publish original vendor firmware in any GitHub repository.

## Inputs and evidence
The operator has provided `ftc6.mot` (Motorola S-record/S2) and `ftc6.id` (observed identifier includes PACIC02). Earlier local exploration tentatively placed firmware records at `0x080000–0x0FFFFF` and hypothesized a reset vector near `0x0D5540`. Treat these as **claims to verify**, not facts about chip mapping. Board photographs were provisionally identified as Renesas M16C family, markings `R5F364AENFB` and `R5F3651TNFC`. Verify markings, MCU variant, memory map, vector location, endianness and image target; different chips/cards may have different roles. Compare with official Renesas datasheets and traceable source evidence. Do not assume FTC6, its main display, outdoor controller and Procon all run the same binary. The image's true CPU/ISA must be proven through plausible instruction/control-flow analysis.

If uploaded files are not mounted or available to the Mac Codex workspace, **STOP with an explicit request for file transfer**, preserving original names and checksums; do not substitute a random internet firmware download.

## Installation and tooling
1. Inventory Mac host architecture, macOS version, Java/JDK, existing Ghidra, available package managers/build tools, storage and user permissions.
2. Identify a trusted official release of Ghidra compatible with the Mac and its documented JDK requirements **at installation time**; pin version and SHA-256, use official download/source, and install in a reversible, user-local location where practicable. Do not blindly assume a previously mentioned Ghidra 12.2/Java25 version is current or required. No `sudo` unless essential and explicitly approved.
3. Investigate and compare M16C processor language modules: `silverchris/m16c` and `esaulenka/ghidra_m16c` are initial research candidates, not guaranteed working plugins. Pin a reproducible revision and examine build/license, ISA coverage, Ghidra API compatibility and architecture support. Build/install a module only if compatible. If neither works, document exact blocker and try an isolated alternative (e.g. custom SLEIGH subset or controlled byte-pattern analysis) rather than declaring a successful disassembly.
4. Validate toolchain on known M16C instruction vectors or documented opcode examples before trusting its output. Record CPU language identifier, address width, instruction validity, warnings and unsupported opcodes.

## Image ingestion and disassembly
- Parse the original S-record with independent checks on record addresses, payload lengths, checksums, overlaps, entrypoint types, holes and unused FF regions. Hash raw inputs and reconstructed memory image; no reliance solely on previous chat-generated analysis files.
- Import at **actual S-record addresses**. Do not relocate to 0 arbitrarily. Verify reset/interrupt vector hypotheses using the **correct specific MCU** datasheet and plausible decoded control flow. Distinguish vector tables from arbitrary lookalike little-endian constants. Preserve gaps and avoid marking FF as code.
- Produce a headless import/analyze command or Ghidra script, a project export as permitted, entrypoint/vector report, sections/regions, selected instruction listings, function/call/reference graph and confidence annotations. Check that repeat runs produce consistent results.
- If the plugin yields nonsensical code, stop and investigate architecture settings instead of assigning guessed C semantics.

## Reverse-engineering priorities
**A. FTC request/service dispatch:** Search direct CN105 GET 0x07/0xA1/0xA2/0xA3 handling, A3 3-digit service-code lookup and statuses 1/2/3/4/6. The proven CN105 wire protocol and P0081 physical scan are available for cross-check; do not assume main-display CN22 messages use exactly the same wire framing. Find actual function references/tables, not merely coincidental occurrences of constants.
**B. Water pump settings:** Locate service-menu pump speed 1–5 settings for heating vs DHW, how these affect PWM and persistent settings, and whether CN105 provides a callable **write** path. A physical screen option does not imply an A3 write opcode. No speculative SET commands to live heat pump.
**C. Energy/COP:** Locate internal live accumulators for consumed/delivered energy, including separate heating/DHW, dating/update cadence, and relevant response packers for GET 0x07, A1, A2. Test the hypothesis that current-day counters exist but are unexposed; absence of a located link is not proof of absence.
**D. Setting/storage paths:** Cross-reference previously observed strings `A:\SETTING\6_HW.DAT`, `6_AC.DAT`, `6_SER1.DAT`, `6_SER2.DAT` and adjacent filenames. Verify addresses and what functions use them; no guessed file semantics.

## Method and proof standard
Cross-check against `requirements/package-runs/P0081/command-map.md` and `implementation-report.md`, Geodan SER manuals, public F1p/gekkekoe CN105 source, and operator-provided chips/images. For each discovery record input evidence, exact flash address, disassembled instructions/crossrefs or reproducible search, conclusion, uncertainty, and what would confirm it. Separate **confirmed disassembly**, **strong hypothesis**, **weak signature match** and **not found**. Do not treat unchanged/mocked bytes as hardware evidence. All processing is offline.

## Deliverables
G2: `requirements/package-runs/P0082/review.md`, `design.md`, `functions.md`, `toolchain.md` (download sources, pinned hashes, install commands), `image-validation.md`, `disassembly-evidence.md`, `findings.md`, `open-questions.md`, and `CHANGELOG.md`. Provide portable scripts, reproducible headless invocation, annotated critical address lists and ideally redacted diagrams. Keep licensed firmware, derived full binaries and private input files **local on the Mac**; repository receives only non-infringing analysis notes/code and the minimum short instruction excerpts required for substantiation.

## Acceptance
PASS only if installation is evidenced (or explicitly identified as already present), valid M16C decoding is demonstrated, raw S-record validated, vectors and memory mapping tested, and prioritized research findings are backed by crossrefs/addresses. Partial success is permitted with **BLOCKED / UNKNOWN** labels and concrete next steps. An unproven CPU/plugin or inability to access uploads must not be reported as completed analysis. Do not actuate either pump or change installed firmware.
