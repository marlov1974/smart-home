# P0069 M1 r2 — pin swap, heartbeat and full old-app erasure

Flash **procon-m1.bin** from this directory with the existing vendor updater. Size **98304 bytes (96KiB)**. The first M1 release is superseded but preserved.

Changes:
- USART3 CR2_SWAP=1, matching original instructions0x080099CC–0x080099E8: PC10 RX,PC11 TX. Initial M1 omitted this and all seven live reads timed out.
- PC12 toggles every500ms (one full blink/second). Original firmware toggles the same GPIO in TIM2 ISR. Physical LED connection/polarity remains to be confirmed.
- File padded with0xFF through0x0801FFFF, covering all pages occupied by original96692-byte application. Vendor updater erases according to file length. This avoids leaving old application bytes in that footprint; it does not claim to erase an unknown whole flash chip. Bootloader bytes below0x08008000 are not included.

Expected: **9600 8N1,slave1,FC04,input0,quantity1 =>888**. Reply01 04 02 03 78 B9 E2. No CN105. Initial stack/vector convention unchanged from M1.

BIN SHA256: `1ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073`. Executable image 1816 bytes; remainder0xFF. Experimental inferred STM32L433 profile; physical r2 readback pending operator.

Old ELF fails corrected wiring-aware emulator; r2 passes native sanitizers and seven ARM emulator scenarios including two heartbeat edges. ELF load bounds remain16KiB while erase envelope is96KiB. Keep original BIN for recovery; restore DIP positions and reconnect RS485 after vendor flash. See ../../docs/RECOVERY.md and original vendor PDF.
