# Function design

New cn_init/feed/tick/tx_byte/tx_sent/read: bounded parser, scheduler and readonly register snapshot; inputs byte/error/time, outputs whitelisted serial bytes/cache, volatile RAM only. UART errors invalidate partial packet; stale cache gives65535 not0. Host tests cover parsing/timing/encoding and register values.
New cn_uart_init/receive/ready/write: USART1 PA9/10AF7,24008E1,HSI16; direct MMIO, no DMA/IRQ. CN service drains bounded RX and emits at most1TX byte, invoked main loop and Modbus wait path. ARM emulation checks UART/GPIO settings and coexistence.
Changed main: larger response buffer, CN initialization/service, millisecond clock accumulation. Changed modbus_reply: bounded multiregister diagnostic reads with request count, preserveCRC/exceptions. Changed image metadata/Makefile: P0070 release names, add modules/tests; unchanged linker/startup. Cross-package catalog updated after tests.
