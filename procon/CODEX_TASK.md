# Codex task — Smart Home / Procon

Work inside this existing Smart Home repository. The `procon/` directory is a subproject. Do not create a nested Git repository.

Work autonomously on the user's Mac. Detect and install required local tooling, preferably through Homebrew, and document exact versions and commands in `docs/TOOLCHAIN.md`.

## Milestone 1

Build a minimal clean-room replacement application which:
1. preserves the existing Procon bootloader/update/recovery path if verified possible;
2. starts on the exact MCU;
3. initializes only hardware required for RS485;
4. implements minimal Modbus RTU compatible with the Smart Home project's existing reader/test tooling;
5. uses the original serial settings and slave/unit addressing;
6. supports the actual operation used to read input register 0;
7. always returns decimal 888 (0x0378) for input register 0;
8. contains no CN105 implementation yet.

Do not broaden M1 until it works on hardware.

## Reference firmware gate

The user will provide `Proon Firmware Update Tool (v3.1.05).zip`. Store an immutable copy under `procon/reference/original/`.

Expected application:
- `A1M_R5_Release_08008000.bin`
- 96,692 bytes
- SHA-256 `2ae03b0cdc684bcccbf9f5281878175f5ca53b144e3e32cc223159fcc4654766`
- application base `0x08008000`

Verify these before analysis. Never modify the reference ZIP/BIN in place.

## Analysis order

1. Parse vector table.
2. Verify initial SP and Reset_Handler.
3. Identify exact MCU/family; do not stop at Cortex-M4.
4. Establish flash/RAM map and bootloader/application boundary.
5. Identify clock setup required for RS485.
6. Identify RS485 UART/USART.
7. Identify baud, parity, stop bits and slave address.
8. Identify RS485 transceiver DE/RE GPIO if required.
9. Trace RX/TX bottom-up from peripheral registers.
10. Establish the actual Modbus request used by existing Smart Home tooling.
11. Implement clean firmware.

For every finding record address, evidence, callers/callees, peripheral/RAM accesses, and confidence: verified / strong inference / hypothesis. Never silently promote a hypothesis to fact.

## Tooling

Detect existing tools before installing. Install what is useful: ARM GCC/binutils and/or LLVM, CMake, Ninja/Make, Python, Ghidra, radare2/rizin, xxd/hexdump. Use OpenOCD only if a physical debug interface is identified and needed. Document everything in `docs/TOOLCHAIN.md`.

## Clean firmware

Prefer new source rather than copied opaque routines. Suggested layout:

```
firmware/
  linker.ld
  CMakeLists.txt
  startup/
  include/
  src/main.c
  src/clock.c
  src/uart_rs485.c
  src/modbus_rtu.c
  src/crc16.c
```

No RTOS or dynamic allocation for M1.

## Safety gate before first flashable BIN

Do not hand the user a replacement BIN until exact MCU/flash geometry, bootloader/application boundary, updater behavior, vector-table placement and linker bounds are verified. Maintain a recovery procedure and immutable original. Produce ELF, MAP, BIN, SHA-256, disassembly, and automated checks for image base/bounds/bootloader overlap.

## Required living docs

Maintain `KNOWN_FACTS.md`, `EXPERIMENT_HISTORY.md`, `PROJECT_PLAN.md`, `MEMORY_MAP.md`, `HARDWARE.md`, `RS485_MODBUS.md`, `ORIGINAL_FW_MAP.md`, `TOOLCHAIN.md`, `RECOVERY.md`, and `DECISIONS.md`.

## Milestones

M0 original restored and communication verified.
M1 clean replacement returns Input Register 0 = 888.
M2 add uptime, Modbus request count and build marker.
M3 CN105 bring-up.
M4 read one known CN105 value such as compressor frequency.
M5 Geodan A3 service 27/28 brine temperatures.

Work evidence-first: observe -> prove -> document -> modify.
