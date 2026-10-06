# P0071 hardware attempt2 — r2 completed service responses

Operator reports r2 flashed. Separate FC04 raw input68 returned2, confirming r2. Read-only capture2026-10-06T20:23:03.789–20:23:48.098UTC:45sample groups,270successfulFC04 calls, no RPC failures. Input0/1=888/71 throughout. No device register/settings writes. LED not separately reconfirmed.

Both channels now repeatedly complete with status2 and raw little-endian0x0005. Retained full payloads:
-27: A3 00 1B 02 05 00 00 00 00 00 00 00 00 00 00 00
-28: A3 00 1C 02 05 00 00 00 00 00 00 00 00 00 00 00

Completed27 count4→9, completed28 count4→8; matching service responses52→101, finished cycles4→8. Service errors0,exhaustions0,UART/protocol errors0. Within-operation request-start gap1000ms. Some samples cross a completion; helper marks those incoherent and omits their decoded candidate, while raw blocks remain preserved. Valid coherent samples always raw5 for both. Signed whole-degree reference decoding therefore yields experimental5C/5C. Physical Mitsubishi display027/028 comparison was requested and remains pending; do not mark temperature calibration/correlation complete.

Hz20 while fresh; normal reply count5→9. Counter pauses during service operations then increments at cycle boundary, consistent with exclusive schedule (not a direct wire trace). One age10s sample honestly reports65535/valid0 before next refresh; no false0Hz interpretation. Brine completion availability is now hardware-demonstrated. r1 interleaving yielded pending-only; r2 exclusive schedule yields completions, supporting sequencing as the cause, without a controlled A/B reversal.

Evidence:procon/analysis/live/20261006T202303Z-p0071-r2-readback.jsonl. Hardware attempts2/3. No firmware changes during validation. Full package hardware pass still awaits display correlation and separately confirming heartbeat. Original r1 observations remain in first-readback log and changelog.

Operator display comparison: in response to the question about current Mitsubishi information027/028, operator replied exactly "5". This matches both captured raw5/reference-decoded5C values at this operating point. The response did not separately label each channel; do not infer independent inlet/outlet mapping, negative-temperature behavior or full-range calibration from this single-point agreement. Display comparison is now recorded; no additional firmware change.
