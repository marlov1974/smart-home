/* P0069; register definitions cross-checked with ST stm32l433xx.h. */
#include "platform.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RCC 0x40021000u
#define GPIOC 0x48000800u
#define GPIOD 0x48000c00u
#define UART 0x40004800u
#define TIM2 0x40000000u

void watchdog_refresh(void) { REG(0x40003000u) = 0xaaaau; }

static void clock_init(void) {
    REG(RCC) |= 1u << 8; /* HSI16 ON */
    while (!(REG(RCC) & (1u << 10))) watchdog_refresh();
    REG(RCC + 8) = (REG(RCC + 8) & ~3u) | 1u;
    while ((REG(RCC + 8) & 12u) != 4u) watchdog_refresh();
    /* Now on 16 MHz: AHB, APB1 and APB2 divide by 1. Keep flash latency. */
    REG(RCC + 8) &= ~0x3ff0u;
}

void platform_init(void) {
    __asm volatile("cpsid i" ::: "memory");
    REG(0xe000e010u) = 0; /* Inherited SysTick off. */
    for (unsigned i = 0; i < 8; ++i) {
        REG(0xe000e180u + 4u * i) = 0xffffffffu;
        REG(0xe000e280u + 4u * i) = 0xffffffffu;
    }
    REG(0xe000ed04u) = (1u << 25) | (1u << 27); /* Pending SysTick/PendSV clear. */
    REG(0xe000ed08u) = 0x08008000u;
    __asm volatile("dsb\nisb" ::: "memory");
    /* Original TIM2 ISR toggles PC12: expose application heartbeat. */
    REG(RCC + 0x4c) |= 4u;
    (void)REG(RCC + 0x4c);
    REG(GPIOC + 0x18) = 1u << 28;
    REG(GPIOC + 4) &= ~(1u << 12);
    REG(GPIOC + 0x0c) &= ~(3u << 24);
    REG(GPIOC) = (REG(GPIOC) & ~(3u << 24)) | (1u << 24);
    clock_init();
    REG(RCC + 0x58) |= 1u; /* TIM2 clock */
    (void)REG(RCC + 0x58);
    REG(RCC + 0x38) |= 1u;
    REG(RCC + 0x38) &= ~1u;
    REG(TIM2) = 0;
    REG(TIM2 + 0x28) = 15; /* 16MHz / 16 => 1MHz */
    REG(TIM2 + 0x2c) = 0xffffffffu;
    REG(TIM2 + 0x14) = 1; /* latch prescaler */
    REG(TIM2 + 0x10) = 0;
    REG(TIM2) = 1;
}

uint32_t micros(void) { return REG(TIM2 + 0x24); }

void uart_init(void) {
    REG(RCC + 0x4c) |= 12u; /* GPIOC and GPIOD */
    (void)REG(RCC + 0x4c);
    REG(GPIOD + 0x18) = 1u << 18; /* PD2 inactive before selecting output mode */
    REG(GPIOD + 4) &= ~(1u << 2);
    REG(GPIOD + 8) &= ~(3u << 4);
    REG(GPIOD + 0x0c) &= ~(3u << 4);
    REG(GPIOD) = (REG(GPIOD) & ~(3u << 4)) | (1u << 4);
    REG(GPIOC + 0x24) = (REG(GPIOC + 0x24) & ~0xff00u) | 0x7700u;
    REG(GPIOC + 4) &= ~0xc00u;
    REG(GPIOC + 8) = (REG(GPIOC + 8) & ~0xf00000u) | 0xf00000u;
    REG(GPIOC + 0x0c) &= ~0xf00000u;
    REG(GPIOC) = (REG(GPIOC) & ~0xf00000u) | 0xa00000u;
    REG(RCC + 0x58) |= 1u << 18;
    (void)REG(RCC + 0x58);
    REG(RCC + 0x38) |= 1u << 18;
    REG(RCC + 0x38) &= ~(1u << 18);
    REG(UART) = 0;
    REG(RCC + 0x88) = (REG(RCC + 0x88) & ~0x30u) | 0x20u; /* HSI16 */
    REG(UART + 4) = 1u << 15; /* Original board swaps RX/TX: PC10 RX, PC11 TX. */
    REG(UART + 8) = 0; /* no DMA or HW DE */
    REG(UART + 0x0c) = 1667; /* round(16000000/9600) */
    REG(UART + 0x20) = 0xffffffffu;
    REG(UART + 0x18) = 8; /* flush stale RX */
    REG(UART) = 13; /* UE | RE | TE, 8 bits, no parity, oversample16 */
}

int uart_receive(uint8_t *byte, int *error) {
    uint32_t status = REG(UART + 0x1c);
    if (!(status & 0x2fu)) return 0;
    *error = (status & 15u) != 0;
    *byte = (status & 0x20u) ? (uint8_t)REG(UART + 0x24) : 0;
    if (*error) REG(UART + 0x20) = status & 15u;
    return 1;
}

static int wait_uart(uint32_t mask) {
    uint32_t start = micros();
    while (!(REG(UART + 0x1c) & mask)) {
        watchdog_refresh();
        if (micros() - start > 10000u) return 0;
    }
    return 1;
}

int uart_send(const uint8_t *bytes, size_t n) {
    REG(UART) &= ~4u; /* mute local echo */
    REG(GPIOD + 0x18) = 4;
    uint32_t start = micros();
    while (micros() - start < 10u) watchdog_refresh();
    int ok = 1;
    for (size_t i = 0; i < n; ++i) {
        if (!wait_uart(0x80u)) { ok = 0; break; }
        REG(UART + 0x28) = bytes[i];
    }
    if (!wait_uart(0x40u)) ok = 0; /* TC, not only TXE */
    REG(GPIOD + 0x18) = 1u << 18;
    REG(UART + 0x18) = 8;
    REG(UART + 0x20) = 15;
    REG(UART) |= 4u;
    return ok;
}

void heartbeat(uint32_t now) {
    static uint32_t last;
    if (now - last >= 500000u) {
        REG(GPIOC + 0x14) ^= 1u << 12;
        last = now;
    }
}
