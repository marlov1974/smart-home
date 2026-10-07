# P0075 hardware report — 2026-10-07

Readback outcome: **BLOCKED_READ_PROTOCOL**. Restoration outcome: **RESTORED_VERIFIED_WITH_SHELLY_RESTART_ANOMALY**. No firmware dump, backup, new firmware, erase/program/EEPROM operation or heat-pump control change resulted from this package.

| Evidence | Result |
|---|---|
| Target and reference before maintenance | P0072 r3, API1, control API3, control idle; pinned immutable r3 BIN hash in findings.md |
| Shelly transport | Pro2 firmware2.0.0, Serial100 mode js_uart/115200/8N1, UART0 after separately approved reboot |
| Original configuration | mb_client/9600/8N1, mb_server address1; exact full snapshot retained privately |
| Script state | Original seven scripts were already stopped/disabled; only identified temporary slot8 used |
| Discovery | Valid 12-byte replies; 225280/255/2048/8192 decoded fields |
| Five completed research series | 64 distinct read frames, eight controls, 77 standalone discoveries, 149 transactions; 957 accepted TX bytes and 972 RX bytes |
| Read replies | Zero bytes for every read candidate; no 0x77/0x76; zero flash bytes captured |
| Latest measured memory | Script used2114/peak4354/free23072; system RAM free116744 bytes |
| Final stop | Script.Stop succeeded at 12:26:49.563088 UTC; no autonomous poller/TX loop |
| Physical handoff | Operator confirmed Procon-only restart and normal DIP10000110 |
| Final verification | CRC-valid raw-UART FC04 identity3/1/3/0, exact Serial restoration/readback, original scripts, advancing telemetry; see closure below |

All raw RPC/serial records, snapshots, generated secrets and exact restore request remain on the operator's Mac in the private P0075 session. Repository records contain sanitized measurements and our generated request hypotheses only. The earlier Script.Delete timeout/restart anomaly is retained in attempts.md; do not repeat deletion immediately after UART ownership. Stop/disable first, restore through the recorded handoff, and review cleanup after the approved reboot.

## Final closure

After the operator confirmed normal DIP10000110 and a Procon-only restart, a fixed read-only Modbus FC04 request through raw UART at9600 8N1 returned13bytes with valid CRC16 and identity3/1/3/0. Eight transmitted bytes included NULs and the request checksum. This establishes that known binary request at9600; it does not qualify115200 short-ACK timing or all256byte values. Exact original Shelly Serial configuration was restored and an approved required reboot performed. The original seven script id/name/enable/running states were verified. Telemetry generations183 and188 advanced86→100; Procon identity remained3/1/3/0 and both Shelly outputs werefalse.

Removing the stopped temporary slot8 after that reboot caused a connection reset and another unexpected Shelly restart (observed uptime160→24). Slot8 was nevertheless removed. Serial, identity, script list and outputs were verified again afterward. No retry of deletion occurred. This extends the earlier cleanup anomaly: a reboot before deletion did not prevent it. Future sessions should retain a stopped/disabled slot and review removal separately. Final normal communication is restored; the firmware-read result remains BLOCKED_READ_PROTOCOL, with no dump or hash comparison.
