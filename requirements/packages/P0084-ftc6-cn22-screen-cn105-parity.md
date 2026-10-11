# P0084 — FTC6 main display CN22 vs CN105 functionality parity

## Status and scope
**Independent new research package, following P0083; do not interrupt or expand P0083's currently running A/B/C investigation.** Static firmware reverse engineering on operator Mac with P0082's working Ghidra/M16C setup. No flash, physical bus injection, or heating control. Vendor binaries/disassembly stay local.

## Central question
**Can everything available through the FTC6 main screen be read or controlled through CN105, or are there screen-only operations?** Distinguish identical internal FTC functions from actual transport-level accessibility and from functions proven on the installed FTC21.00. FTC firmware image under analysis appears 20.01, so cross-version generalization is not automatically valid.

## Required work
1. Establish from Geodan wiring documentation that the display uses **CN22**, a two-wire powered controller link (~12 V), while the adapter uses **CN105**. Do not assume identical framing, standard RS485, UART voltage levels, or shared dispatch based on apparent similar latency.
2. With targeted Ghidra call/data reference analysis, locate main display communication RX/TX, parsers and screen-command routing in the FTC20.01 image. Locate corresponding CN105 request dispatch and SET/GET handlers, extending P0083 findings *after its handoff*. Identify whether the two interfaces converge on the same internal setting functions or whether one is restricted.
3. Produce a **screen-to-CN105 capability matrix** per function: screen menu/path and read/write action; CN22 packet/handler evidence; underlying setting or RAM reference; CN105 GET, SET or A3 equivalent; actual wire encoding only if proved; confidence and version applicability; counterexample/unknown reason. Do not equate a function being present in ROM with an externally callable command.
4. Prioritize: Heating and DHW **water-pump speed 1–5**, curve vs fixed-flow, heating and DHW prohibit/enable, VV normal priority, pump economy/timers, energy monitor settings and energy counters, display's Running Information service codes, and installation/service menu distinctions.
5. Investigate screen's 10–15 second service-request latency and whether it shares the internal service selector from P0082/P0083 while using a different transport. Trace format/status handling (1/2/3/4/6) where supported.
6. Document any menu operations that demonstrably have no counterpart in current **known** CN105 command maps, and separately those proven impossible or blocked in the firmware. Avoid unsupported categorical claims of total parity or lack of parity.
7. If binary cannot establish the CN22 protocol, identify exactly what extra evidence is needed, possibly display firmware or a later separately approved **high-impedance isolated passive observation** while a human operates the menu. Do **not** connect TTL/RS485 directly to CN22 or perform any physical sniffing under P0084.

## Evidence and methodology
Follow G2 bootstrap and use P0082 toolchain, P0083 concluded results, P0081 physical code map, FTC service manual, F1p/gekkekoe public CN105 implementation. For each trace show exact firmware SHA/version, address, genuine instructions/crossrefs, alternative hypotheses and CONFIRMED / STRONG HYPOTHESIS / UNKNOWN confidence. Address known M16C plugin decoding gaps; absence of a found path does not establish impossibility.

## Deliverables
Create `requirements/package-runs/P0084/review.md`, `design.md`, `functions.md`, `screen-cn22-trace.md`, `screen-cn105-parity-matrix.md`, `transport-comparison.md`, `open-questions.md`, `verification.json` and `CHANGELOG.md`. Publish only safe summaries, compact evidence excerpts and reproducing scripts; no vendor full binaries. The conclusion must answer YES / NO / NOT ESTABLISHED about complete display parity, with actual evidence and next smallest verification experiment.

## Acceptance
Report PASS/PARTIAL/BLOCKED against actual code traces and verified protocol support. It is acceptable to conclude NOT ESTABLISHED if requisite transport evidence is missing; do not invent CN105 writes or claim successful decoding on unsupported instructions. Keep P0083 unchanged while it finishes.
