# P0069 review — WARN

Clean worktree synchronized to origin/main 1bd3214. Prior local import commit had identical tree; switched to remote commit without modifying files. Existing dirty P0068 checkout untouched. Continuing active Procon thread with package bootstrap (memory/08-context-bootstrap-modes.md).

Reference hash and size pass. STM32L433 startup reserved vector pattern matches exactly across all 99 entries; 23 other L4 patterns differ. Register layout, PLL initialization and SRAM2 address independently agree with L4. Exact part/package/flash-density not proven. User permits an educated MCU assumption. New linker will conservatively use only 16 KiB application flash at 0x08008000 and 16 KiB SRAM1; no flash controller writes.

RS485 USART3 PC10/PC11 AF7, PD2 active high direction evidenced in original application. Vendor updater IL accepts raw BIN and sends erase/write offsets starting at zero; device translates offsets. Bootloader itself is not included in the original application, so preservation is an evidence-based expectation of the existing vendor update path, not independently proven. Candidate clearly labeled experimental. M0 restoration and M1 hardware verification remain operator-dependent.
