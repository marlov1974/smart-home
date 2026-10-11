# P0085 hardware matrix — PARTIAL

Sources/version convention: [sources](sources.md). Signals and rails are separate; no direct wiring instructions are inferred.

| Port | Actual connected device | Intended role | Pins / rails documented by S1 | Transceiver / CPU peripheral | Wiring confidence |
|---|---|---|---|---|---|
| CN22 blue | Main display, operator-confirmed | Main remote controller |2 contacts;10.4–13.7V DC across the connection |Specific transceiver and MCU pins UNKNOWN; D-path assignment remains unproved |CONFIRMED role and reported connection; PCB traces absent |
| CN105 red | Procon, operator-confirmed and P81 traffic |WiFi or adapter |5 contacts; pins1–2 supply11.5–13.2V DC; remaining pin directions/logic levels not established here |UART2, S2 registers0268–026F, vectorsFFD3C/FFD40; physical line conditioning UNKNOWN |STRONG combined static/physical identification; no continuity measurement |
| CNRF white |WiFi adapter reportedly attached; likely installer miswiring per latest correction |Wireless receiver (e.g. PAR-WR51R-E per S3) |5 contacts; pins1–2 supply11.5–13.2V DC; signal pinout UNKNOWN |UNKNOWN. Do not assign UART0/1 just because UART2 is used |Role CONFIRMED; working MELCloud link withdrawn/unverified |
| CNIT blue |Present, no connected device established |Unspecified in Geodan drawings reviewed |5 contacts on p11; supply, ground and signals UNKNOWN |UNKNOWN; service/diagnostic interface is a hypothesis, no traced PCB connection |Presence CONFIRMED; purpose PARTIAL/UNKNOWN |
| CN3C blue (alternative) |Internal FTC/control-board link in S1 |FTC–refrigerant-control communication |3 positions shown; test signal0–24V DC |D-path is one candidate; UART or discrete circuit ownership UNKNOWN |Documented role; prevents premature D=CN22 attribution |

Equal pin counts and equal documented supply ranges do not prove equal pinouts, UARTs or permissions. The two attached photos earlier in the conversation show Procon circuitry, not sufficient FTC connector-to-MCU routing. No chip-level transceiver identification is justified from them.
