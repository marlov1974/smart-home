# P0069 hardware evidence

Status: inferred STM32L433xx. Operator explicitly permits an educated MCU assumption (2026-10-06); physical part marking, package and density are unverified. The first experimental build does not claim otherwise.

| Finding | Evidence | Confidence |
|---|---|---|
| L433 startup target | All 99 vector positions, including all 22 reserved zeros, match ST startup_stm32l433xx.s. Of 24 L4 templates compared, only L433 has zero reserved mismatches. | Strong inference |
| L4 peripheral map | RCC 0x40021000: AHB2ENR+0x4C, APB1ENR1+0x58, APB2ENR+0x60; PLLP=7 in original oscillator configuration | Strong inference, independent of vector match |
| RS485 USART3 | IRQ39 at 0x0800A24C -> 0x0800FE90 -> 0x08010AA4; port1 resolver 0x08009794 returns handle0x20000FF0; main stores peripheral0x40004800 there | Verified in reference code |
| PC10 TX / PC11 RX AF7 | USART3 MSP branch 0x0800A068–0x0800A0CE initializes GPIOC mask0xC00, AF7 | Verified in reference code; electrical wiring inferred |
| PD2 direction active high | 0x08010988 writes GPIOD pin4 high before TX; 0x080109F4 writes it low; factory RS485 test also toggles PD2 | Strong inference of DE/RE wiring |
| CN105 USART1 PA9/10 | Handle0x20000EE8 ->0x40013800, MSP mask0x600 AF7; separate RX/TX implementation | Verified separation in reference code; unused in M1 |

Authoritative comparison: [ST CMSIS L4 at pinned commit](https://github.com/STMicroelectronics/cmsis-device-l4/tree/ca0bfa2b8b68dc2994b27fba0a10dfd28d086ee1). [STM32L433RC product/memory](https://www.st.com/en/microcontrollers-microprocessors/stm32l433rc.html).

Initial broad F3/G4 hypotheses were rejected after inspecting RCC offsets, PLL fields and startup vectors. Do not reuse those initial family guesses. Trace artifacts are in ../analysis/.
