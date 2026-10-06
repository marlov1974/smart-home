# P0069 implementation design

Fresh freestanding Cortex-M4 source; no vendor application routines copied. Minimal register definitions for inferred STM32L433. Reset establishes stack, vector base and C data/BSS, masks inherited interrupts and stops SysTick. Clock switches to internal HSI16, avoids relying on unidentified external crystal. USART3 PC10/PC11 AF7 9600 8N1, PD2 low RX / high TX until complete shift-register transmission. TIM2 free-running 1 MHz supplies wrap-safe timing. Refresh inherited IWDG without starting it or modifying options.

Pure C CRC/Modbus and bounded RTU frame collector separated from MMIO. Max 256-byte frame, T1.5 1600 us, T3.5 4000 us for this fixed serial mode. Bad CRC/address/broadcast silent. Unsupported function exception 1, unavailable register exception 2, invalid quantity exception 3. Only FC04 address0 quantity1 succeeds. No writes or CN105.

Make-based reproducible ARM GCC build; Python validation/analysis tools; host and mocked-peripheral Unicorn tests. Linker limits app 0x08008000–0x0800BFFF, SRAM1 0x20000000–0x20003FFF. Output candidate padded to 2 KiB page boundary with 0xFF for vendor updater alignment. No bootloader bytes included. Static checks validate every load segment and all vector targets. Release explicitly records assumed hardware and untested physical operation.

Risks: chip/package inferred; bootloader absent; internal-clock serial tolerance untested; transceiver electrical settling unmeasured. Software tests cannot establish electrical communication or recoverability. No unrelated refactor.

## Attempt 2 — 2026-10-06
Seven live FC04 reads after operator-confirmed flash/reconnect/reset timed out. Serial settings verified96008N1. Static evidence at0x080099CC/CE and0x080099D2/E2 establishes AdvancedInit flags0x38 and Swap0x8000 at handle+0x34; ST HAL structure identifies USART_CR2_SWAP. Correct USART3 CR2 bit15 only; retain initial SP, clocks, UART baud and PD2. Update mocked wiring to require SWAP before UART RX/TX; prove old ELF fails and corrected ELF passes. Preserve immutable first release, publish separate P0069-m1-r2.

Operator steering during attempt2: first updater erases only2KiB and LEDs are dark. Add PC12 heartbeat, a pin toggled by original TIM2 ISR0x0800A210–0x0800A222. This is M1 startup diagnosis, not M2 telemetry. Fill BIN with0xFF to98304bytes, spanning0x08008000–0x0801FFFF (original96692-byte app rounded to2KiB pages). Keep executable link region16KiB and bootloader excluded. This clears the previous application footprint, not unproven entire chip capacity. Extend bounds checker and LED emulator test.
