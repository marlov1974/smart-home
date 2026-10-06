# Project plan

## Phase A
Verify exact MCU, memory/bootloader boundary, clocks, RS485 UART, serial settings, transceiver direction GPIO and original Modbus behavior.

## Phase B
Minimal clean application: startup + clock + RS485 UART + Modbus RTU CRC/parser. Input Register 0 returns 888.

## Phase C
Add uptime, Modbus request count and build marker.

## Phase D
Only after stable Modbus, bring up CN105.

## Phase E
Read one known CN105 value, then implement Geodan A3 service 27/28.

Do not combine several unverified hardware subsystems in the first bring-up image.

## P0069 status

PhaseA: strong L433/pin mapping inference; exact physical device and device bootloader remain unavailable. Operator permits inferred MCU. PhaseB: source, build, static checks, native tests and compiled-ARM simulation complete. Deliver experimental candidate to operator; M1 not hardware-complete until FC04 input0 yields888. PhasesC–E remain deferred.

P0069 attempt2: initial M1 hardware readback failed with seven timeouts. Shelly settings96008N1 verified; operator confirmed flash/reconnect/DIP/reset. Original USART3 SWAP=1 was omitted in M1; r2 corrects only CR2 bit15 and passes enhanced wiring-aware emulator. Physical r2 test pending.

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.

## P0070 — 2026-10-06

M1 r2 hardware pass: operator reports blinking; five consecutive FC04 raw input0 reads returned888. Evidence: `analysis/live/20261006T190106Z-m1-r2-readback.json`. This supersedes older pending-M1 status.

P0070 adds USART1 read-only ATW connect/GET0x04. Input0 stays888; input1=70, input2=Hz or65535 unknown/stale; input3 validity, input4 age and further counters. UART/packet errors are visible. CN105 electrical communication remains unverified until operator flashes P0070 and live values are captured. No device setting writes by this package. Firmware tests pass; hardware milestone M3/M4 remains pending.
