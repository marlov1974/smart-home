# P0075 write reference and return to0x57 — 2026-10-07

## Result

The write controls established negative ACK and finite handling of an incomplete0x53 packet. They did **not** establish a successful write. One correct-format eight-byte FF attempt inside pinned r3 padding returned72. No erase, application-code replacement, EEPROM or heat-pump control was attempted.

| Request/control | Direct result | First RX after first TX |
|---|---|---:|
| 0x50 after discovery | 7A, cached discovery tag | 160ms |
| Full0x53, badCRC/validsum | 72 | 1985ms |
| 0x50 immediately following above, no intervening discovery | 72, cached write failure | 168ms |
| Full0x53, goodCRC/badsum | 72 | 1648ms |
| Full0x53, correct format,8FF | 72; no successful programming proof | 2048ms |
| BadCRC control19+1, actual gap91ms | 72 | 1882ms |
| Same, actual gap210ms | 72 | 1845ms |
| Same, actual gap1017ms | 72 | 1863ms |
| Same, intended gap3500ms | 72 **before tail**; only19bytes sent | 1692ms |

The first0x50 result was initially classified as unknown by the conservative adapter and stopped it. The classifier was updated/tested before any0x53 transmission, preserving the observation as a cached ACK rather than a write-success response. No automatic retransmission occurred.

Then three fixed reads were each preceded by discovery and followed directly by0x50: single57; eight-byte57100000800008ef; twelve-byte571000008000086e992697b3. Every read returned zero bytes over3seconds; every following0x50 returned7A. No discovery was inserted between each read and its cache check.

The difference supports an absent/disabled0x57 hypothesis, but cannot prove it. A reader may validate or record status differently. Unknown parameters/session requirements remain possible. The incomplete0x53 experiment shows that this write path can reject before the missing last byte arrives; it does not establish a universal timeout or transfer those semantics to reads. Times are observed through Shelly scheduling, not wire-level measurements. A correctly framed72 can reflect already programmed/ECC state, alignment/size or erase prerequisites rather than bad packet format.

## Verification and final state

46 offline write-adapter cases and27 read/ACK cases pass, as does the complete existing make readback-test target. The previously verified firmware source and image are unchanged; no extra ARM rerun is needed for these isolated research scripts. Raw timestamps, serial/RPC records and generated session secrets remain private on the Mac. Standalone write-reference-experiments.md owns the exact packet catalog and detailed accounting.

All work on the line is stopped. Ownslot8 is stopped and disabled; it will be retained rather than deleted, because earlier deletion caused Shelly restarts. Serial remainsjs_uart1152008N1 and the last operator-confirmed Procon DIP is00000000. The operator explicitly deferred the physical return to10000110/restart until this evening. Status: **WAITING_FOR_OPERATOR_RESTORE** and **BLOCKED_READ_PROTOCOL**. No background polling or future automatic experiment is scheduled.

After the operator confirms physical restoration: restore the exact saved Serialmb_client9600/8N1 configuration, perform only its already approved required Shelly reboot, retain ownslot stopped/disabled, and verify identity3/1/3/0 plus advancing telemetry. No Modbus requests before that physical confirmation. Current lesson stays package-local; no unsupported global rule about read support or MCU identity is promoted.
