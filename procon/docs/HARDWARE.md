# P0069 hardware evidence

Status: inferred STM32L433xx. Operator explicitly permits an educated MCU assumption (2026-10-06); physical part marking, package and density are unverified. The first experimental build does not claim otherwise.

| Finding | Evidence | Confidence |
|---|---|---|
| L433 startup target | All 99 vector positions, including all 22 reserved zeros, match ST startup_stm32l433xx.s. Of 24 L4 templates compared, only L433 has zero reserved mismatches. | Strong inference |
| L4 peripheral map | RCC 0x40021000: AHB2ENR+0x4C, APB1ENR1+0x58, APB2ENR+0x60; PLLP=7 in original oscillator configuration | Strong inference, independent of vector match |
| RS485 USART3 | IRQ39 at 0x0800A24C -> 0x0800FE90 -> 0x08010AA4; port1 resolver 0x08009794 returns handle0x20000FF0; main stores peripheral0x40004800 there | Verified in reference code |
| PC10 RX / PC11 TX AF7 with SWAP=1 | USART3 MSP branch 0x0800A068–0x0800A0CE initializes GPIOC mask0xC00, AF7 | Verified in reference code; electrical wiring inferred |
| PD2 direction active high | 0x08010988 writes GPIOD pin4 high before TX; 0x080109F4 writes it low; factory RS485 test also toggles PD2 | Strong inference of DE/RE wiring |
| CN105 USART1 PA9/10 | Handle0x20000EE8 ->0x40013800, MSP mask0x600 AF7; separate RX/TX implementation | Verified separation in reference code; unused in M1 |

Authoritative comparison: [ST CMSIS L4 at pinned commit](https://github.com/STMicroelectronics/cmsis-device-l4/tree/ca0bfa2b8b68dc2994b27fba0a10dfd28d086ee1). [STM32L433RC product/memory](https://www.st.com/en/microcontrollers-microprocessors/stm32l433rc.html).

Initial broad F3/G4 hypotheses were rejected after inspecting RCC offsets, PLL fields and startup vectors. Do not reuse those initial family guesses. Trace artifacts are in ../analysis/.

## M1 r2 correction
Original0x080099CC/CE selects AdvancedInit0x38 (includes SWAP_INIT0x08);0x080099D2/E2 writes Swap0x8000 at UART handle+0x34. ST HAL UART_AdvFeatureInitTypeDef puts Swap there; USART_CR2_SWAP is bit15. Corrected firmware sets CR2=0x8000. Thus AF7 nominal TX/RX are exchanged: PC10 RX,PC11 TX. Initial M1 omitted this and timed out; it is superseded. Evidence is static and test-backed; successful physical readback remains pending. [ST HAL UART definitions](https://github.com/STMicroelectronics/stm32l4xx-hal-driver/blob/master/Inc/stm32l4xx_hal_uart.h).

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.

P0070: M1 r2 now hardware-confirmed; next experimental build adds CN10524008E1 on PA9/10AF7 and read-only compressor telemetry. See `../releases/P0070-compressor-r1/README.md` and `CN105.md`. Same conservative flash/RAM/vector limits and96KiB FF envelope. Physical CN105 result pending. No setting writes or physical flash by Codex.

## Verified hardware result — 2026-10-06

Operator flashed P0070 compressor r1 (firmware commit `391d903dc9e8197bfda9b83a93014788e06fced9`). Six read-only FC04 blocks at19:23:35–19:23:46 UTC (21:23 local) returned input0=888, input1=70, compressor20Hz, valid1 and sample age0–1s. Accepted CN105 replies increased109→115 and RX events2405→2537; protocol errors0, UART errors0, link1. This confirms continued CN105 updates through our firmware, not merely a cached Modbus constant. Frequency did not change during this short observation; correlation against the physical service display and long-duration stability have not been tested.

Raw evidence: `procon/analysis/live/20261006T192335Z-p0070-compressor.json`. No register/settings writes. This supersedes earlier pending-P0070 hardware notes. M3 bring-up and M4 first compressor telemetry are hardware-confirmed; brine/M5 remains future work. Exact MCU marking/density is still unknown. Immutable release artifacts retain their build-time metadata.
