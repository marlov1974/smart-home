# P0085 findings

**Offline research complete; hardware/protocol/access coverage PARTIAL. No installed device was contacted.**

1. Operator correction resolves the main apparent wiring discrepancy as likely installer miswiring: WiFi is probably on the wrong port. Mitsubishi documents WiFi/Procon on CN105 and the wireless receiver on CNRF. There is no established working MELCloud protocol on CNRF.
2. New UART0 and dual-personality UART1 paths were traced from interrupt vectors through RX/TX. UART1 diagnostics use five-byte checksum-zero requests, a session flag, memory-read handling and exported bus diagnostics. They are distinct from the CN105 FC protocol. Their connector assignment is still UNKNOWN.
3. CN105 SETC8 eligibility is now more precise: payload1=0/1, payload2=0..3, category-mask/state checks, first-set-bit category selection and matching payload15. Category6 maps to import phase2373=6, connecting the pump-setting staging/import evidence. This is not yet a qualified live settings procedure.
4. D-path ISR boundaries and scheduler calls are now pinned: TimerB1→942E6 and TimerA0→C1456. This does not settle CN22 versus CN3C or establish timing in seconds.
5. CNIT's intended Geodan purpose, physical pinout and access remain UNKNOWN. Do not borrow another Mitsubishi model's CNIT definition. A candidate diagnostic software path is a useful lead, not proof of a privileged connector.

## Required conclusion matrix

| Question | Result | Basis |
|---|---|---|
| Does CNRF use CN105 protocol? |UNKNOWN |Manufacturer roles differ; corrected WiFi placement is not protocol evidence |
| Does CNIT use CN105 protocol? |UNKNOWN |No physical mapping; traced UART1 diagnostic protocol itself differs |
| Does some alternate software path have extra diagnostics? |PROVED static20.01 |9E77A→9E938 memory read and9D88C→9D8A0 log export |
| Does CNIT or CNRF demonstrably have higher rights? |UNKNOWN |Connector binding and version reachability absent |
| Does “same connector name/shape means same interface” hold? |DISPROVED as inference rule |Manufacturer cross-family CNIT roles vary; no PCB routing proof |
| Would moving Procon help? |UNKNOWN, no evidence supporting a move |Known CN105 works; neither alternative is electrically/protocol-qualified |

| Area | Status | Remaining dependency |
|---|---|---|
| Manual roles + corrected installation record |PASS |Exact adapter model still useful |
| Complete pins/peripherals by connector |PARTIAL |Matching FTC PCB schematic/traces |
| Software transport traces |PARTIAL |New UART0/1 paths found; physical owners and full dispatcher semantics absent |
| CN105 restrictions/settings gates |PARTIAL |Complete transaction, persistence and21.00 match |
| Privilege hypothesis assessment |PASS (UNKNOWN result) |No basis to claim alternative-port superiority |
| Reproduction and repository evidence |PASS when verification.json passes |Private matching input needed to rerun |

No firmware build or deployment was appropriate for P85. Vendor firmware is not published. See [open questions](open-questions.md) for minimum next evidence; no new physical measurements are authorized by this package.
