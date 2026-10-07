# P0075 attempts

## Transport qualification 1 — 2026-10-07 11:10 UTC

Operator confirmed sole Shelly RS485 master and normal DIP10000110. Created disabled-autostart temporary script8. It only queried UART handles100 and0; both threw in original mb_client mode. No send/configure/recv calls and no A1M bootloader traffic.

Serial.SetConfig to device-advertised js_uart1152008N1 returned restart_required=true. Aborted before raw-mode script startup, stopped own script, requested exact original Serial configuration. Restore also returned restart_required=true. Script.Delete timed out. Subsequent Sys status shows uptime36s versus2398792s before: an unexpected restart occurred; no reboot RPC was sent. Reset_reason changed3→4; numerical reason is recorded without unverified interpretation. Cause/causal operation unknown.

Follow-up reads verify original Serial config byte-for-JSON-equivalent, original7 scripts all stopped/disabled with temporary8 absent, A1M r3/API1/package3/controlIDLE registers68–71=3/1/3/0. Sys restart_required=false; both physical outputs false. Relays initial_state restore_last and match_input respectively. No output commands issued. JS free pool returned25200. Temporary-script used182/peak266/free25004 before interruption. Raw-mode UART mapping and binary safety remain unqualified.

Status BLOCKED_TRANSPORT pending separately reviewed Shelly restart permission; no firmware dump/read/probe was made. This counts as one supervised hardware transport attempt; two remain under the current package budget. Further operations await operator response. Raw RPC records and snapshot remain local only.

## Transport qualification 2 and discovery deployment — 11:13–11:17 UTC

Operator explicitly approved supervised Shelly reboots. Serial100 switched to js_uart115200 and controlled reboot performed. UART100 unavailable; UART0 exposes send/recv/configure. Qualification script used420/peak1064/free24766. No UART bytes sent. Script.Delete again timed out after Stop; restoration helper initially aborted on that exception, so exact saved Serial config was restored explicitly and an authorized reboot performed. Identity3/1/3/0 and original Serial config read back successfully. The local helper requires nested cleanup handling before reuse; it is not reusable production transport code.

Discovery bridge then deployed in own slot8, enable=false, after controlled mode transition/reboot. Node/Python focused tests pass. HTTP authenticated status seq0 returns idle, high_water0, empty RX/error. Script running, mem_used1946/peak2198/free23240, no errors. Only hardcoded5A transmission is possible; no0x57 endpoint. UART mapping established, binary transport and physical discovery still pending. READY_FOR_OPERATOR: physical DIP/power handoff requested; original10000110, requested00000000. No physical confirmation yet, no bootloader sends.

Initial passive expiry15min; after first request60s inactivity and3s transaction deadlines. No automatic discovery loop. Current Serial mode js_uart115200; normal Modbus intentionally unavailable until restoration. Stop own script, restore exact snapshot, reboot if requested by Serial API; leave disabled slot through reboot to avoid observed immediate-delete anomaly. Do not resume Modbus until operator confirms normal DIP. Raw session token and detailed records remain local only.

## Physical boot session1 — operator confirmed ready

Authenticated discovery seq1 transmitted exactly5A once, received12bytes7a00700300ff000008002014, sum8 verified. Decoded max_flash225280, max_eeprom255,erase_block2048,max_write_page8192. Physical read size/address contract remains unknown. Script memory after discovery used2128,peak4130,free23058.

Own script8 stopped and updated (not deleted); all uploaded source bytes read back and hash-checked. First fixed experimental frame57100000800008ef: hypothesized lengthLE16=16,addressLE32=08008000,sum8. Host sent one authenticated probe, script reports sent8,received0;3s window ended NO_RESPONSE. No retry or follow-on byte. This cannot distinguish unsupported command, missing CRC/header bytes, invalid absolute addressing or another layout. No application bytes extracted. Requires operator power resynchronization before another hypothesis. Normal communication restoration remains pending because operator currently has DIP00000000. Raw records local only.

Second fixed hypothesis with CRC32+sum8 prepared/tested/uploaded and script readback verified; passive idle sent0. No second physical attempt yet. Awaiting operator Procon-only power resynchronization, DIP remains00000000. New discovery must precede next hypothesis.

Operator requested individual zero bytes to complete possible outstanding parser input. Sent16 individual00 bytes, waiting at least1s for response after each; all sends reported1byte, total16. RX count remained0 throughout and on final delayed poll. Automatic bound reached; no further TX. This does not establish unsupported0x57 or parser reset. All raw/status/timestamp evidence local. Procon remains in operator-selected bootloader DIP00000000; Shelly remains js_uart115200. CRC variant still not sent.

Operator requested immediate57+zeros to test timeout hypothesis. Uploaded fixed bounded script and verified full source readback. One start sent57100000800008ef then16 separate00 bytes,24total accepted by UART.send,0RX. Actual relative TX timestamps: header7ms, first zero69ms, finalzero667ms. First gap62ms, later gaps39–41ms despite requested10ms timer. Result NO_RESPONSE after250ms final grace. No replay/reset/new discovery. This removes the prior minutes-long delay but does NOT rule out an inter-byte timeout shorter than62ms or stale parser state. Full trace and runtime health local. Test stopped automatically.

Operator authorizes one new5A in the current boot session, followed by the fixedCRC32 read hypothesis only if valid discovery returns. This explicitly replaces the earlier resynchronization precondition for this bounded test. A valid discovery demonstrates liveness/recognition, not proof of all internal parser state being reset.

Rediscovery succeeded: one5A returned7a00700300ff000008002014, same12bytes and validsum8. Bootloader responsive following previous57/zero tests; no physical reset needed to obtain this reply. Then one fixedCRC32 hypothesis571000008000086e992697b3 sent,12bytes accepted,0RX after3s. No retry/further commands. This does not identify why57is silent or prove read unsupported. Both uploaded scripts fully read-back verified. Raw results in local rediscovery-crc directory.

16-variant series completed: all16 sent once,0RX each after3s. All17 interleaved5A checks valid and identical. Script stopped. No device reboot,erase/program,control write or application extraction. See variant-series.md; raw logs local only.

## Independent research window — 12:10–12:26 UTC

Operator authorized one hour of independent work. Eight parser controls completed: 005A, 575A, 57005A and 0057005A yielded zero RX; 5A00, 5A57, 5A5A and 5A005A each yielded exactly one valid discovery reply. Nine interleaved standalone discoveries succeeded. This suggests first-byte/receive-group dispatch but does not prove NUL delivery or parser internals.

Three further fixed 16-candidate series tested wire address00008000, a length-associated zero-filled envelope, and alternative lengths/field padding. All48 candidates yielded zero bytes; each series had17 valid standalone discoveries. Together with the initial16-candidate series, the exact accounting is64 distinct read frames,8 controls,77 standalone discoveries. See standalone experiment report for complete request catalog and precise UTC intervals. No device reboot or reset was performed between these series.

The last series ended12:26:49 UTC; Script.Stop succeeded12:26:49.563088. Latest measured script memory used2114/peak4354/free23072 and system RAM free116744. No late data, short ACK, overflow or read payload was observed. Static archive research found no resident bootloader; public-source research found no complete read contract.

Operator chose physical restoration later after being asked to return Procon to normal DIP10000110. All further Procon traffic is paused. A proposed normal-mode raw-UART Modbus identity test remains unperformed. Current Serial isjs_uart1152008N1, ownslot8stopped/disabled, original scripts unchanged, last physical DIP00000000. Recovery statusWAITING_FOR_OPERATOR_RESTORE.

Offline review tightened the series adapter to halt immediately on a short UART.send instead of sending the remainder on a later timer tick. Every recorded live frame was accepted in full, so this does not invalidate or reinterpret historical counts. The refactored portable host has offline fake-transport coverage and was not rerun physically.

## Final restoration supersedes earlier pending state

After the operator confirmed normal DIP10000110 and a Procon-only restart, a fixed read-only Modbus FC04 request through raw UART at9600 8N1 returned13bytes with valid CRC16 and identity3/1/3/0. Eight transmitted bytes included NULs and the request checksum. This establishes that known binary request at9600; it does not qualify115200 short-ACK timing or all256byte values. Exact original Shelly Serial configuration was restored and an approved required reboot performed. The original seven script id/name/enable/running states were verified. Telemetry generations183 and188 advanced86→100; Procon identity remained3/1/3/0 and both Shelly outputs werefalse.

Removing the stopped temporary slot8 after that reboot caused a connection reset and another unexpected Shelly restart (observed uptime160→24). Slot8 was nevertheless removed. Serial, identity, script list and outputs were verified again afterward. No retry of deletion occurred. This extends the earlier cleanup anomaly: a reboot before deletion did not prevent it. Future sessions should retain a stopped/disabled slot and review removal separately. Final normal communication is restored; the firmware-read result remains BLOCKED_READ_PROTOCOL, with no dump or hash comparison.
