# P0069 implementation design

Fresh freestanding Cortex-M4 source; no vendor application routines copied. Minimal register definitions for inferred STM32L433. Reset establishes stack, vector base and C data/BSS, masks inherited interrupts and stops SysTick. Clock switches to internal HSI16, avoids relying on unidentified external crystal. USART3 PC10/PC11 AF7 9600 8N1, PD2 low RX / high TX until complete shift-register transmission. TIM2 free-running 1 MHz supplies wrap-safe timing. Refresh inherited IWDG without starting it or modifying options.

Pure C CRC/Modbus and bounded RTU frame collector separated from MMIO. Max 256-byte frame, T1.5 1600 us, T3.5 4000 us for this fixed serial mode. Bad CRC/address/broadcast silent. Unsupported function exception 1, unavailable register exception 2, invalid quantity exception 3. Only FC04 address0 quantity1 succeeds. No writes or CN105.

Make-based reproducible ARM GCC build; Python validation/analysis tools; host and mocked-peripheral Unicorn tests. Linker limits app 0x08008000–0x0800BFFF, SRAM1 0x20000000–0x20003FFF. Output candidate padded to 2 KiB page boundary with 0xFF for vendor updater alignment. No bootloader bytes included. Static checks validate every load segment and all vector targets. Release explicitly records assumed hardware and untested physical operation.

Risks: chip/package inferred; bootloader absent; internal-clock serial tolerance untested; transceiver electrical settling unmeasured. Software tests cannot establish electrical communication or recoverability. No unrelated refactor.
