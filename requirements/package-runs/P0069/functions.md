# P0069 function design

- crc16(data,n): pure Modbus CRC16; golden request/response vectors and corruption tests.
- modbus_reply(request,n,response,capacity): bounded pure parser, returns bytes or zero; FC04/0/1 =>888; tests CRC, other units, broadcast, exceptions, truncation, capacities, fuzz.
- rtu_feed(state,byte,now,error): collect up to256 bytes, latch UART/inter-character errors and overflow; side effect state only; test malformed frames and recovery.
- rtu_poll(state,now,response,capacity): after4000us silence, reply or discard then reset; wrap-safe timestamps tested.
- Reset_Handler / Default_Handler: startup C initialization, exception halt with bus released; ARM emulator observes initialization.
- platform_init / clock_init: mask inherited IRQs, VTOR, HSI16, TIM2; MMIO only, no flash programming; emulator register expectations.
- uart_init / uart_receive / uart_send: USART3 PC10/11 and PD2 bounded TX wait, RX errors/echo flushing; emulator verifies bytes and DE ordering.
- micros / watchdog_refresh: timer read / inherited watchdog refresh; do not start watchdog.
- main: polling loop, no CN105; end-to-end ARM emulator request/response test.
- Python setup/build-check/analysis/test entry points: reproducible local tools, vector/literal and updater inspection, ELF/BIN bounds, known protocol scenarios; no network/device access during tests.

No existing runtime functions changed or removed. Any detailed helper functions remain within these responsibilities.
