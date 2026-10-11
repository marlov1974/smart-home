# P0083 — FTC6 M16C: trace service dispatcher, water-pump control and energy accumulators

## Status / authorization
**Ordered Codex deep static analysis**, continuing P0082's working Mac Ghidra/M16C installation and validated local FTC6 firmware image. Do **not** install firmware, write to FTC/Procon, change settings, probe physical communication or operate heat pumps. No new broad opcode sweep. Do not publish vendor MOT/ID, full binary or proprietary disassembly to public repos.

## Objective
Deliver evidence-backed program-flow and data-flow traces for (A) CN105/A3 service request handling and response formats, (B) water circulation pump heating/DHW settings 1–5, (C) live consumed/delivered heat/electric energy counters including any CN105 exposure, and (D) whether main-screen CN22 functionality is reachable via CN105. Answer what can be learned from the supplied FTC6 image versus what is not provable from it.

### Mandatory starting evidence
Read normal G2 bootstrap, P0082 `findings.md`, `disassembly-evidence.md`, `service-dispatch-candidates.json`, `open-questions.md`, `verification.json`, P0081 physical `command-map.md`/`implementation-report.md`, relevant Geodan service manual and pinned public F1p/gekkekoe protocol sources. Reuse local Ghidra project/scripts and image checksums instead of reinstalling tools or reimporting needlessly.

P0082 achieved a coherent M16C/60 startup at `0x0D5540`; plausible service selector dispatcher `0x08C0B4` with calling sites `0x08BAB9`, `0x08BBD6`, `0x08BF6B`, `0x0CEC8A` and shared response tail `0x08D346`. Proven selected cases include 506→`0x08C8FE` (RAM 0x0664, signed /100), 511→`0x08C95D` (RAM 0x0662, signed /100), 540→`0x08CC6E` (RAM 0x322E, unsigned /100), 550→`0x08CC81` (format 3), and 340→`0x08C6F2` (**mutates RAM**, exclude from probing). File table at `0x087620` and indexed selection `0x0C96E6`. These are leads; some selector-to-CN105 transport links and semantics remain unverified. Image header appears 20.01 versus installed FTC reporting 21.00. Do not transport absolute RAM addresses or assume code identity across revisions. M16C decoder has a known issue at 0x09B038 and incomplete control-flow metadata.

## Track A — establish service / transport route
1. Validate enough M16C branch/call/far-load and operands to follow dispatcher callers correctly; document repairs or verified workarounds with synthetic opcode tests, without silently trusting wrong decompiler output.
2. Trace **backward** from dispatcher `0x08C0B4` and its four call sites to input parser, request selector, frame construction and transport ownership. Distinguish CN105 GET/A3 requests from display CN22 or internal buses; labels only after byte-level proof.
3. Trace **forward** to handler selection, response-copy tail `0x08D346`, response length, value scaling, type/status codes **1/2/3/4/6**, checksum/framing if found. Connect to actual P0081 captured behavior and show why some valid service codes were classified unhandled.
4. Produce a compact selector table with actual code paths for 17/18/19/27/28/52/54/175/176, plus 506/511/540/550 and reset/initialization 340; distinguish missing cases from decoder blind spots. No assumption that A3 means an independent universal wire opcode.

## Track B — water pump 1–5
1. Follow setting-file lookup `0x0C96E6`, descriptor/callback path and relevant service/menu setting references; identify storage (RAM, persistent data or file offset) only with actual xrefs and reads/writes.
2. Identify *separate* Heating and DHW water circulation pump 1–5 parameters, any clamping/range checks, and mapping to FTC CNPWM/Pump1 outputs. Distinguish requested step, actual pump PWM, measured water flow and brine pump's unrelated A3/18 step 0–10.
3. Search for *existing* CN105 writable handler to those settings. If not found, state searched call paths, false positives and confidence; no invention of packet bytes and no live SET tests.
4. Where possible compare read-only `GET 0x15` with setting/speed internals; identify which bytes are readback candidates and what is still unknown.

## Track C — electrical/thermal energy
1. Locate the source data and output packers for direct CN105 `GET 0x07` and `GET 0xA1`/`0xA2` (if present in this binary). Trace backward to computations, accumulation registers, daily rollover, heating/DHW attribution, pump/heater inclusion, and timing.
2. Test whether **current-day running** consumed/delivered energy accumulators exist and whether a documented or undetected **read-only CN105** path can reach them. Distinguish internal RAM counters from exposed read APIs. No speculative live probing.
3. Explain apparent difference between direct GET07 increasing energy (physical P0081: 477.0→477.3 over ~33 min) and unchanged dated A1/A2 5 October, without asserting a shared unit or clock until supported.
4. If paths cannot be located, provide addresses/graphs investigated, decoder limitations, what minimal additional image or trace would be needed. Explicitly allow outcome `NOT ESTABLISHED`.

## Track D — main controller display CN22 vs CN105 feature parity
1. Identify the FTC6 main remote controller connection **CN22** and compare with CN105, using the Geodan wiring/service manuals. CN22 is the documented two-wire main-controller port (approx. 12 V feed); **do not assume RS485, TTL UART, identical A3 wire framing, or a shared packet parser**. CN105 is the distinct external adapter port.
2. In FTC6 20.01 binary, trace CN22 receiver/transmitter and UI/menu message dispatch, command selection, handlers, and data stores; compare call graph and references against CN105 parser/SET/GET handlers. Identify whether paths converge on shared internal APIs (e.g. pump speed heating/DHW, curve/flow mode, pump timers, service menu, prohibited heating/DHW, energy settings and A3 request codes).
3. Build **feature parity matrix**: (a) documented screen action and menu path, (b) CN22 command evidence and handler, (c) shared internal function/data, (d) CN105 GET availability, (e) CN105 SET availability, (f) exact confidence and evidence (static / public protocol / P0081 physically verified), (g) remaining barrier. Separate **possible in MCU**, **exposed by an identifiable CN105 command**, and **physically demonstrated on installed FTC21.00**.
4. Focus first on our needed screen functions: primary pump speed 1–5 separately in heating/DHW; compensation curve versus fixed-flow mode; DHW permit/prohibit and heating permit/prohibit; normal water-heating priority; flow/pump energy settings; service-code display reads. Also identify classes only available in installation/service menus.
5. If the two-wire framing cannot be recovered from this FTC image or requires screen firmware, state exactly what is missing. Suggest a safe **non-intrusive observational** capture design for later authorization, including high-impedance isolated measurement of CN22 and comparison to known screen actions; no live capture or injection in this package. Avoid incorrectly wiring UART/RS485 devices to the 12 V screen bus.
6. Explicit answer to the operator's central question: **can everything available on the screen be done through CN105?** Return YES / NO / NOT ESTABLISHED, with documented counterexamples or unknowns rather than conflating internal handler reachability with external protocol permission.

## Method and deliverables
Use targeted Ghidra headless scripts, cross-reference walks, table-seeded disassembly, constrained signature searches and reproducible exports. Every claimed instruction/data interpretation must include firmware image hash/version, flash address, caller/callee, relevant operand or data-reference evidence, confidence (**CONFIRMED / STRONG HYPOTHESIS / UNVERIFIED / NOT FOUND**), and any external corroboration. Separate observations of FTC20.01 from VP1 FTC21.00.

Create G2 `requirements/package-runs/P0083/` with `review.md`, `design.md`, `functions.md`, `decoder-validation.md`, `service-trace.md`, `pump-control-trace.md`, `energy-trace.md`, `candidate-cn105-actions.md`, `open-questions.md`, `verification.json` and `CHANGELOG.md`. Add `screen-cn22-trace.md` and `screen-cn105-parity-matrix.md`. List scripts, command lines, exact input/plugin/tool versions and deterministic output checksums. Store raw vendor firmware/full instruction exports **only locally**. Update repo file index and function registry according to bootstrap process.

## Completion gate
Codex must report **per-track A/B/C/D** PASS / PARTIAL / BLOCKED. PASS means a reproducible actual call chain and grounded interpretation, not a plausible constant match. Propose smallest further research or **separately authorized supervised physical test** for unresolved protocol hypotheses; this package itself never actuates any hardware. If the exact FTC hardware attribution or plugin opcode validity blocks evidence, report this explicitly and stop rather than fabricate answers.
