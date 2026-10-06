# P0069 verification — 2026-10-06

`make -C procon verify` PASS (outside sandbox for Unicorn JIT).
`python procon/tools/analyze_updater.py` PASS static IL only.
`git diff --check` PASS.
Original size/SHA256/ZIP CRC and extracted-member equality PASS.
Release/build BIN equality, SHA256SUMS and file index PASS.
Forced `make -B -C procon all` produced identical BIN SHA25680d74358b7e94eaecf674d1e85c8eb654110a10faebea2b76ef7eec4614638a6.

ELF:1704 bytes text,0 data,268 BSS. Candidate:2048 bytes,0x08008000–0x080087FF. Reset0x0800818D,SP0x20004000.

Host ASan/UBSan: CRC golden request,64 bit corruptions,256 slave IDs, invalid functions/ranges/quantities, truncated requests, output capacity guards,4000us frame gap, invalid2000us internal gap, UART error recovery,256-byte overflow,32-bit timer wrap,20000 malformed packets: PASS.

Actual ARM ELF with mocked peripheral registers:
- FC04/0/1:01 04 02 03 78 B9 E2.
- Bad CRC: silent.
- Broadcast: silent.
- FC06 write:01 86 01 83 A0 (illegal function).
- UART framing error: silent.
- Stalled TX: bounded timeout and PD2 released.
All cases verified startup vector base, UART BRR1667,PC10/11AF7,PD2 output,HSI16 clock selector,1MHz timer,inherited watchdog refresh and no CN105/flash writes.

Negative ELF mutation checks (temporary copies only): invalid SP, reset vector into0x08000000, PT_LOAD start below application base and PT_LOAD extending beyond0x0800C000 all rejected before objcopy.

Initial JIT invocation inside sandbox failed with illegal instruction. Identical test outside sandbox passed; full verification after relocating environment also passed. No hardware test performed. Fixed timing/electrical behavior, exact MCU marking and device bootloader internals remain unverified. M1 hardware milestone is pending operator.
