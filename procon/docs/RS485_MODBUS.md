# P0069 RS485 contract

Experimental M1: USART3 PC10/PC11AF7, PD2 high TX / low RX. Internal HSI16, BRR1667 (~9598baud), fixed96008N1, slave1. DIP and EEPROM configuration are deliberately not interpreted by this first application. Keep/restore existing DIP positions after vendor bootloading.

Supported: Modbus RTU function04, zero-based input address0, quantity1 ->888 (0x0378).

Request: `01 04 00 00 00 01 31 CA`
Response: `01 04 02 03 78 B9 E2`

Read-only existing Shelly path:
`http://192.168.86.85/rpc/MbRtuClient.ReadInputRegisters?id=100&sid=1&addr=0&qty=1`
Expected JSON values:[888]. This input-register read is FC04; naming an address H0 does not change its function code.

Bad CRC, other slave and broadcast: silence. Unsupported function: exception01. Unavailable address/range:02. Invalid quantity:03. No writable registers and no normal Procon telemetry. Frame gap4000us, invalid internal gap>1600us; UART errors/overflow discarded, recovery after silence. PD2 remains high until TC confirms last stop bit; bounded TX wait releases bus on failure. CN105 never initialized or transmitted.

Hardware readback pending operator flash. Six actual-ELF emulation scenarios passed with mocked UART/register behavior; this does not measure actual baud, transceiver or electrical timing.

## M1 r2 correction
Original0x080099CC/CE selects AdvancedInit0x38 (includes SWAP_INIT0x08);0x080099D2/E2 writes Swap0x8000 at UART handle+0x34. ST HAL UART_AdvFeatureInitTypeDef puts Swap there; USART_CR2_SWAP is bit15. Corrected firmware sets CR2=0x8000. Thus AF7 nominal TX/RX are exchanged: PC10 RX,PC11 TX. Initial M1 omitted this and timed out; it is superseded. Evidence is static and test-backed; successful physical readback remains pending. [ST HAL UART definitions](https://github.com/STMicroelectronics/stm32l4xx-hal-driver/blob/master/Inc/stm32l4xx_hal_uart.h).

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.

P0070: M1 r2 now hardware-confirmed; next experimental build adds CN10524008E1 on PA9/10AF7 and read-only compressor telemetry. See `../releases/P0070-compressor-r1/README.md` and `CN105.md`. Same conservative flash/RAM/vector limits and96KiB FF envelope. Physical CN105 result pending. No setting writes or physical flash by Codex.

## Verified hardware result — 2026-10-06

Operator flashed P0070 compressor r1 (firmware commit `391d903dc9e8197bfda9b83a93014788e06fced9`). Six read-only FC04 blocks at19:23:35–19:23:46 UTC (21:23 local) returned input0=888, input1=70, compressor20Hz, valid1 and sample age0–1s. Accepted CN105 replies increased109→115 and RX events2405→2537; protocol errors0, UART errors0, link1. This confirms continued CN105 updates through our firmware, not merely a cached Modbus constant. Frequency did not change during this short observation; correlation against the physical service display and long-duration stability have not been tested.

Raw evidence: `procon/analysis/live/20261006T192335Z-p0070-compressor.json`. No register/settings writes. This supersedes earlier pending-P0070 hardware notes. M3 bring-up and M4 first compressor telemetry are hardware-confirmed; brine/M5 remains future work. Exact MCU marking/density is still unknown. Immutable release artifacts retain their build-time metadata.

## P0071 brine candidate

Adds a separate read-only service27/28 state machine with exclusive CN105 transaction ownership, bounded retries and continued GET04 telemetry. Preserves P0070 registers0–15 (build marker71); adds16–67, with max16 registers per read. Raw completed payloads are retained per service; temperature candidates use reference-backed signed little-endian encoding and remain experimental. See [BRINE.md](BRINE.md) and `../releases/P0071-brine-r1/README.md`. Software tests pass; no P0071 hardware readings or physical flash yet. Previous P0070 hardware result remains valid historical evidence.

## P0071 r2 — operator-directed exclusive sequence

The operator explicitly changed the schedule after r1 only returned A3 status0. Send exactly one Hz GET04, then service27 including all retries, then service28 including all retries, and repeat. No Hz or other query is inserted between retries or between27and28. One request owns the link at a time; retain1s minimum retry cadence,10attempt limit,800ms reply timeout,1sTXqueue timeout and50ms turnaround. The prior20s cycle cooldown is removed. State4 now means DONE waiting for next Hz, not cooldown. Link-loss reconnect is deferred until both bounded service operations finish; then connection recovery restarts from Hz. This overrides the previous interleaved polling design under explicit user direction.

Hz freshness remains truthful: during a long service sequence it can exceed10s, so input3 becomes0 and input2 becomes65535 until the next normal response. Input4 exposes age. Do not call this an unexpected communication failure without checking the phase/counters. Brine validity/retention unchanged. Inputs0–67 unchanged except state4 semantics; new input68=2 identifies r2. Marker0=888 and build1=71 remain. Maximum16registers/read.

Native65s simulations assert every emitted request follows Hz→27→28, including not-ready,missing,corrupt,wrong-echo,terminal-status and timer-wrap cases. All12ARM cases pass; pending-service case emits only one Hz then five27 requests while Modbus responds; complete case reaches next Hz only after28. Checksums/frame whitelist, heartbeat and no flash/control writes remain tested. r2 hardware result pending; no temperature is hardware-confirmed. Physical attempt1 was r1, pending-only, evidence stored in analysis/live/20261006T200502Z-p0071-first-readback.jsonl.
