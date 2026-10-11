# Procon port choice

**Keep CN105 and extend its qualified commands first.** No demonstrated reason to move Procon to CNIT for normal heat control has emerged. UART1 diagnostics are useful, but CNIT binding and functional superiority are both unproved. UART6 appears to be room-receiver traffic, while UART0 appears to be storage; neither is an established complete alternative.

Two parity targets remain distinct:

1. All documented user/installer actions: incomplete on every inventoried path. Screen-local language/format/password presentation, file transfer, service actions and native settings sessions must be accounted for individually. A memory interface is not screen parity.
2. Needed L2 features: existing CN105 covers core mode/target and permission controls plus operational telemetry and forwarded service feedback. Configured pump levels have static settings routes but lack a completed externally observable transaction. Recovery/ownership and source limits remain separate obligations.

| Candidate relative to CN105 including settings sessions | Supported set relation |
|---|---|
|UART6 / candidateCNRF|Overlapping functions: room reports, limited target input, boost,holiday. No proved total subset because receiver status fields remain unlabeled; no superset|
|UART0 / candidateSD|Different file/log/import functions; relation unresolved for individual native settings. Not a proved interactive-control superset|
|D / candidateCN22|Overlap via shared modes/services, potentially broader settings; complete per-action difference unresolved|
|UART1 / candidateCNIT|Extra near-memory and draining-log access, plus diagnostic snapshots; no proved equivalent write ownership or normal-control parity. Incomparable at the demonstrated-command level, total sets unresolved|
|Source / candidateCN3C|Peer control and returned brine/Hz data; not an external-controller replacement contract|

No electrical migration is qualified. CNIT power/ground, logic levels, polarity, pinout, protection/isolation and duplex are unknown. OCH722A supply-pair voltages forCN105/CNRF and two-wireCN22 are not UART voltage ratings. Procon's interface must be measured against the actual destination; no passive paralleling of active transmitters. Exact MCU package/photo association is still needed before pin numbers.

UART1 normal8N2 differs from diagnostic8E1. Personality comes from06D8.bit7 and boot/configuration logic; sending an open-session packet does not change it. Its link owner/peer-loss consequences are unqualified. UART6 uses04/03 headers, not Procon's02/7A; unsolicited room reports and receiver ownership cannot be replaced by a GET poll loop. UART0's file-client role needs peer-server semantics and scheduler analysis. No master/slave/addressing, hot-switch, coexistence, reboot or failure recovery claim is transferred between these protocols.

Current measured release-p81 budget (bytes), not obsolete layout:

| Module | Flash used / slot | RAM used / reserved |
|---|---:|---:|
|BL2|6584 /8192|856 /4096|
|Common|4280 /12288|216 /2048|
|Dispatcher|672 /4096|8 /256|
|Mode|12280 /12288|992 /4096|
|Drift|2736 /4096|616 /2048|
|Service|1360 /4096|160 /1024|
|DebugCommand|72 /4096|0 /256|
|DebugTelemetry|208 /4096|0 /256|

BL2 exports cn_uart_init/receive/write/ready and owns physical UART configuration. A changed parity/pin/electrical protocol might need BL2 revision or a versioned ABI; it is not automatically Common-only OTA. Common would own new framing/session/arbitration; Dispatcher maps API commands; Service handles exclusive queries; Drift decodes telemetry. Mode has only8 flash bytes free in this measured release, so adding control logic there requires relocation/rebalancing. No new backend was built, hence incremental flash/RAM costs are **unmeasured**, not fabricated estimates. A100-byte diagnostic response needs at least100-byte frame storage if implemented monolithically; this lower bound does not include state/queues.

Recommendation order: finish CN105 settings handshake and neighboring-field semantics offline; retain existing production safeties/ownership; electrically identify CNIT only if diagnostics justify a separate adapter. An active bridge may eventually be justified by measured roles, but no present evidence warrants building one or migrating control.
