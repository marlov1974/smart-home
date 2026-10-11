# Ranked functional port assignments

These are working assignments, not a pinout. New continuity/scope measurements: zero. OCH722A printed p11/p12/p63 names the connectors independently of software paths.

| Rank / path | Working connector / role | Positive evidence | Counterevidence / unresolved discriminator |
|---|---|---|---|
|1 UART2|CN105 external interface|FC/02/7A protocol, exact public/P81 frames, working Procon; physical manual labels WiFi adapter|No independent MCU-pin continuity; alternate02 families unqualified|
|1 UART6|CNRF wireless receiver|Eight indexed room temperatures, limited target/boost/holiday inputs, reports of native status; manual explicitly calls CNRF wireless receiver|Pairing/identity/battery not yet named; no captured04/03 traffic or pin trace on CNRF|
|1 UART0|SD/storage controller, candidateCN108|16 named settings files, dated log path,512-byte blocks; manual CN108 and LED4 SD|Could be a file-service bridge with SD behind it; need LED/card-detect path and board continuity|
|2 D bit path|CN22 main remote|Broad native settings/service convergence; two-wire manual CN22; separate timer/GPIO framing|CN3C/internal control remains alternative until outgoing and incoming field families fully bound; not UART by elimination|
|2 source software path|CN3C control-board link|Native heat/temperature request serializer; shared forwarded service machinery for compressor/brine; manualCN3C FTC/C.B.|RX transport-to-service chain now bound (source-link.md); active profile and full outbound schemas unresolved; no source-board firmware here|
|3 UART1|CNIT service/diagnostics|Memory, draining logs, diagnostic snapshots, maintenance loops; two personalities|No CNIT protocol description or physical binding; cannot exclude another internal/service connection|

The user specifically suggested an underboard responsible for brine. That matches the already demonstrated forwarding boundary for decimal services17/18/19/27/28/52. Do not assign such values to FTC-local sensor calculations just because FTC relays them. CN3C is explicitly an FTC/C.B. transmission link (0–24VDC label on p63); this is not evidence of TTL compatibility.

Neither CNIT's abbreviation nor its signal levels/pinout are established by the available evidence; leave “IT” unexpanded. The supplied M16C photos (R5F3651TNFC and R5F364AENFB markings) belong in the FTC-board investigation, not automatically Procon. Exact photo-to-board/revision/package association remains necessary; do not use a100-pin pinout for the128-pin candidate.

MAC-597IF-E was connected to CNRF and did not work. With UART6's04/03 room protocol now found, wrong-port installation is a stronger explanation than protocol equivalence. Still, this is an inference rather than a captured failure diagnosis. No cable change is proposed as part of this offline package.
