# P0072 r3 physical heating control — PASS for tested path

2026-10-07, operator-flashed r3 (identity3/1/3). Host base74ad7d8; later repository updateeb722f7 only adds plannedP0075, not executed here. This is P0072 live validation; no flash, bootloader experiment, firmware update, pump override or prohibition write was performed.

## Root cause confirmed

Passive GET28 payload `28 00 00 00 00 00 00 01 00 01 00 00 00 00 00 00`: cooling prohibitZone1=1 and cooling prohibitZone2=1. Heating, DHW, holiday, boost and server flags0. This explains r2's blanket-gate rejection; r3 correctly permits Zone1 heating without altering cooling flags. FAST/A3 diagnostics continued updating.

## Commands and restoration

Atomic FC16 offset300, envelope version2, magic49266. Exact requests/replies retained in compressed JSONL logs. Encoder records `sent:false` before dispatch; the following logged RPC request/response establishes actual transmission.

|Sequence|Command|Outcome|
|---|---|---|
|1|FIXED_FLOW38C,lease90s|Applied; mode1,flow3800 read back|
|2|AUTO|Restored mode2,flow2800; snapshot cleared|
|3|FIXED_FLOW38C,lease45s|Applied; lease expired, error7 as expected; automatic restore without AUTO|
|4|FIXED_FLOW38C,lease960s|Applied10:12:33.179UTC; held903.526s before AUTO|
|5|AUTO|Sent10:27:36.705UTC; restoration confirmed10:27:47.780UTC|

Saved original configuration for each session: power1,Zone1 mode2 (curve),reported flow target2800,DHW target5200,boost0. Only Zone1 mode/flow dimensions were touched (mask12). Final control words: state0,accepted5,applied5,error0,snapshot0,touched0,lease0,ACK12,readbacks27,restores3; last configuration matches original. No host renewal or extra command was sent during the long run. Final read-only follow-up around10:41UTC confirms idle control,mode2,target2800 and compressor0Hz. Native curve remains in charge; reported curve target can subsequently vary normally.

## Fifteen-minute response

Times UTC (Stockholm +2hours). Trial applied10:12:33,first coherent positive Hz10:18:21 (about5m48s later). This is an observed delay, not proof of a particular native timer. Flow began29C,dipped28C while circulating,rose past38C and peaked39.5C. Frequency0→42Hz then fell to26Hz near restoration. Water flow10–11L/min. Return28–34.5C. Brine inlet5–10C/outlet3–8C across the full long-run log; during established heating about5/3–4C. Immediately after AUTO,flow38.5C/return34.5C and brine5/4C; thermal inertia and native stopping behavior persist after a configuration change.

Derived water-side heat0–4981W (water assumption, uncalibrated; no electrical measurement, therefore no COP). Final long-run sample3065W. Statistics use only coherent valid values; generation changes during a multiblock read produce null and are excluded rather than treated as zero. API reports unavailable brine-pump state/step throughout. No new display correlation was performed.

CN105 GET04 count130→257 during long run; parser and UART errors stayed0,handshakecount1 unchanged. Brine generations and FAST values continued updating; no reset or communication regression observed. Total3 successful r3 validation phases after1 failed-safe r2 attempt; no further failed debug attempts.

## Scope and remaining limitations

Verified on this installation: FIXED_FLOW38C application, matched readback, explicit AUTO restoration, runtime lease restoration, heating response and continued telemetry. OFF,DHW boost,DHW target,reset/power-loss recovery and link-loss recovery were not physically tested. RAM-baseline loss on reset remains a known limitation; this result does not establish unattended safety or maximum thermal performance.

Logs are gzip-compressed JSONL with original timestamps and raw blocks. `p72-r3-summary.json` provides reproducible per-phase statistics. Archived harness contains the workstation import path used for the run; it is not a portable production controller. The existing knowhow entry about observable, operation-specific preconditions is confirmed; no new global knowhow entry needed.
