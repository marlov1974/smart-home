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
