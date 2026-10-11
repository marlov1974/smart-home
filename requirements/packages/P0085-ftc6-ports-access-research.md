# P0085 — FTC6 communication ports and access control

## Scope
Codex investigation using existing P0083/P0084 Ghidra environment. **Offline static research only**. Do not operate, rewire, flash or command the installed heat pumps. Do not publish vendor firmware.

## Installation evidence
User confirms: main display on CN22, Procon on CN105, **original Mitsubishi MELCloud WiFi adapter on CNRF**, CNIT physically present with unknown function. Treat user-observed wiring as specific to this machine. Geodan manuals describe CN22 as the main remote, CN105 as adapter and CNRF as wireless receiver; resolve any apparent documentation discrepancy instead of overriding observed facts.

## Research objectives
1. Identify CNIT's intended purpose from manuals, firmware and MCU/PCB connections. Classify documented fact versus inference.
2. For CN22, CN105, CNRF and CNIT, establish each port's physical interface, pinout, supply voltage, peripheral/UART/GPIO, serial framing, handshake, data and checksum format. Never infer protocol identity from equal connector shapes or similar circuitry.
3. Trace per-port RX/TX, interrupt handlers, parsing, message dispatch, validation and shared internal FTC functions in the M16C Ghidra image. CN105/UART2 and the separate provisional D-path were found in P0084; **D-path is not yet proven to be CN22**. CN3C is an alternative hypothesis. Investigate other peripheral paths separately.
4. Compare effective **rights and access restrictions**: normal GET, A3 service codes and selector filtering, normal SET, heating/DHW permissions, pump-level settings, service configuration, scheduler/curve edits, energy-monitor settings, diagnostics and firmware/service functions. Identify actual code gates and settings-session requirements; a shared internal function does not prove reachability via every port.
5. Test the hypothesis that CNIT or CNRF offers additional privileges over CN105, particularly where CN105 has A3 filtering or requires special SET C8 settings session. Report **proved, disproved or unknown** for each capability. An unidentified port is not automatically a privileged service interface.
6. Account for the working original MELCloud adapter on CNRF. Look for evidence about its protocol and supported messages without connecting to the cloud, intercepting private traffic, sending commands or moving cables.
7. Distinguish FTC20.01 static firmware conclusions from P0081 physical FTC21.00 results. Identify minimum additional evidence needed for confidence (manual, exact adapter model, board traces, passive isolated capture), proposing future separately approved measurements only.

## Required matrices
A. Hardware: port, actual connected device, manufacturer intended role, pins/rails, transceiver, CPU peripheral, wiring confidence.
B. Protocol: bitrate/signaling, frame format, address/session/handshake, command handling and observed evidence.
C. Access: each requested function versus CN22 screen, ordinary CN105, CN105 settings session, CNRF and CNIT; each cell CONFIRMED / INFERRED / UNKNOWN / RESTRICTED plus supporting address and version.
D. Conclusions: do CNIT/CNRF use the same protocol as CN105? Does any port have demonstrably higher rights? Would moving Procon actually help? Explicit evidence-qualified answers, not assumptions.

## Starting sources
Read standard G2 bootstrap, P0081 mapping results, P0083 findings, and P0084 transport-comparison, screen-cn22-trace, settings-trace, parity matrix, Geodan service manual wiring pages 11 and 63, and available original WiFi-adapter references. Reuse Ghidra setup and pinned M16C decoder with known limitations; do not redo completed scans.

## Deliverables
Create `requirements/package-runs/P0085/` with `review.md`, `design.md`, `functions.md`, `hardware-matrix.md`, `protocol-matrix.md`, `rights-matrix.md`, `cnit-investigation.md`, `access-gates.md`, `findings.md`, `open-questions.md`, `verification.json`, `CHANGELOG.md`. Use exact ROM addresses/call chains, evidence source and CONFIRMED/STRONG HYPOTHESIS/UNKNOWN classification; portable scripts and sanitized summaries only. Update tracked file index. Report per-area PASS/PARTIAL/BLOCKED. No real-device interaction authorized in P0085.
