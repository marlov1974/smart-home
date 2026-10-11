# P0081 — installation and physical mapping complete

VP1 was installed with firmware manifest `71b30837` after explicit operator approval. VP2 retains `7adaecf1`. Shelly is now in native Modbus client mode, 9600 8N1; the required configuration reboot was completed. Both pumps were verified powered on, operating in heating, configured for native heating curve (mode 2), with idle/clear application control state at the end. Final compressor readings were 22 Hz and 24 Hz. No heating setpoints or permissions were written during mapping.

## Physical coverage and quality

The bounded run completed from 2026-10-10 20:57 UTC to 22:38:53 UTC (local completion 2026-10-11 00:38:53), within its 7200-second cap. All 720 planned observations were captured: two separated passes over 256 zero-parameter direct GET codes and 104 documented read-only A3 codes. The preceding baseline passed 10/10 reads. Hazardous initialization/reset codes were excluded.

| Scope | Observations | Result per pass |
|---|---:|---|
| DIRECT 00–FF | 512 | 84 valid replies; 172 bounded no-responses |
| A3 service allowlist | 208 | All 104 replied: 93 established formats, 11 unhandled status formats |

Every code retained the same status classification across its two reads. No parser or UART errors occurred. The maximum observed compressor-telemetry age at before/after health checks was 6 seconds; this is not continuous measurement of the exclusive A3 transaction's internal gap. No new connect handshake was observed. Offline log audit passed exact request envelope, identity, request/result correlation, checksum, planned coverage and control-state checks. Health monitoring is not a comprehensive Mitsubishi fault decoder.

## Useful findings

- Direct 1E and 1F each returned valid all-zero data twice, approximately 33 minutes apart. They did not expose brine in this tested state. This does not prove every parameterized variant or future state is unused.
- Of the 84 responding direct codes, 21 had other data, 15 had only zero data and 48 had an FF/zero pattern (50–7E and C8). A response is not proof of a usable feature.
- A3/27 and /28 returned 4/4 in both passes, consistent with the established whole-degree brine interpretation. A3/17 target-frequency raw value changed 22→21; /19 pump-speed candidate changed 3810→3780. /18 remained raw 16, outside the manual's stated 0–10 display range: do not silently clamp or reinterpret it.
- A3/511=30, /506=29 and /540=15 repeated. The flow candidate agrees with direct GET14's 15. Direct GET0C supply/return changed 31.0/29.0→30.5/28.5 C between passes. Several optional sensor positions return identical default-looking values; actual sensor installation is not established by a valid reply.
- GET07's reference-decoded increasing consumed-energy candidate changed 477.0→477.3 in about 33 minutes. Units/calibration remain unverified. Its consumed-power byte stayed zero, so no meaningful instantaneous COP was calculated.
- GET01's clock advanced and reported 10 October; FTC version bytes decode as 21.00, matching A3/190 raw 0x2100. A1/A2 retained identical energy records dated 5 October. Those records are not present-day power or live COP.
- Unhandled A3 status 3 occurred on codes 100–105 and 550, status 4 on 0/107, and status 6 on 14/129. These are checksum-valid replies. API `UNSUPPORTED` here means an unhandled service status/format, not proof that the command is absent. Numeric/hex formats 1/2 are established; other display semantics remain unverified.

Raw replies changed for direct 01,03,05,07,0B,0C,13 and A3 16,17,19,48,508,534. Historical fault measurements remain separately labeled and must not be mistaken for live sensors.

## Implementation and verification

The isolated asynchronous API uses FC16 holding offset 600/count 8 for bounded GET submission and FC04 input 600–631 for coherent sticky results. Existing control offset 300 is unchanged. Request acceptance is separate from FTC completion; sequence, ownership, quarantine, retry/expiry, raw capture and validity are explicit. See `procon/modular/RAW_API.md`.

Only Common and Dispatcher changed in the OTA plan. BL2, layout and effect-regulator binaries were unchanged. Common uses 4280/12288 bytes and 216 bytes RAM; Dispatcher 672/4096 bytes and 8 bytes RAM. Mode remains 12280/12288 bytes. No claim of fitting a 2 KiB Common target is made.

Verification passed: full ASan/UBSan host suite, actual ARM API/regression tests, 2065 OTA interruption cases, fake Shelly transfer/helper checks, portable export binary equality, and seven final mapper tests. The two host follow-ups add durable submit/terminal logging and complete 104-code manual metadata. They do not change installed firmware; the physical runner used the earlier loaded host version. Its unchanged original records were enriched offline.

## Evidence and repository state

Private workspace evidence is under `P0081/install-vp1-20261010T204721Z`, `P0081/modbus-20261010T205218Z`, `P0081/live-baseline`, and `P0081/mapping-20261010T205704Z`. The mapping directory contains original JSONL, per-reading CSV, raw command maps, `service-values.csv` with observed words/min/max/change, derived `enriched-readings.jsonl`, `analysis.json`, `audit.json`, and final two-device snapshots. Raw evidence and identities are not exported to the standalone repository.

The adjacent `command-map.md` is the sanitized 360-code map. Portable source was initially published at `7f7ca23285c5f5c4ca5c1a4d9cb84549f14dfc1d`; final source/report publication is recorded in `verification.json`. Repository visibility remains unchanged (private). G2 retains the preexisting P0080 working changes; no unrelated G2 commit/push was made. `REPOSITORY_FILES.md` was updated and matches all 787 indexed paths.

Knowhow promotion created: `memory/knowhow/procon-async-mapping.md`, covering asynchronous acceptance/completion, Shelly restart handling, retained failure evidence and unhandled A3 formats. Old UART effect-test scripts must not assume the Shelly is still in UART mode.
