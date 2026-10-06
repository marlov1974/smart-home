# Decisions

- Keep this project under the existing Smart Home repository; no nested `.git`.
- First clean-room milestone is RS485/Modbus register 0 = 888.
- CN105 is deferred until M1/M2 are stable.
- Preserve failed reverse-engineering experiments rather than silently reusing their assumptions.

- P0069 operator owns physical flashing from separate computer. User explicitly allows guessed/inferred MCU; use evidence-backed STM32L433 profile and label uncertainty.
- Use HSI16 and polling-only USART3 for M1, fixed96008N1/slave1, PD2 direction. No EEPROM access, CN105 or flash writes.
- Conservative16KiB app/16KiB SRAM linker,2KiB padded candidate; retain original recovery files. Software pass is distinct from hardware milestone completion.
