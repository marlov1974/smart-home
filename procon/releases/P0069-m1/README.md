# P0069 M1 — experimental test firmware

Flash file: **procon-m1.bin**,2048 bytes. STM32L433 family is inferred; exact marking and hardware operation are unverified. User authorized this MCU assumption and performs flashing from a separate PC. Vendor updater/device bootloader address translation is inferred, not independently verified. See ../../docs/RECOVERY.md and original vendor PDF.

Expected after flash: **9600 8N1, slave1, function04, input address0, quantity1 =>888**. Request `01 04 00 00 00 01 31 CA`; reply `01 04 02 03 78 B9 E2`. This first firmware supplies no other Procon/CN105 features.

Use the existing Procon updater with the raw BIN. Record/restore DIP positions per vendor instructions. Keep unchanged original A1M_R5_Release_08008000.bin for recovery. Do not prepend bytes or perform full-chip erase. Application base0x08008000; padded exclusive end0x08008800. No flash/EEPROM writes in this application.

SHA256 BIN: `80d74358b7e94eaecf674d1e85c8eb654110a10faebea2b76ef7eec4614638a6`.

Passed: warning-free ARM build, native protocol/framing tests with sanitizers,20000 malformed packets, six actual-ELF emulation cases with mocked peripherals, image bounds/vectors and deterministic rebuild. Physical Modbus operation remains untested.

Contents: BIN for updater; ELF/MAP/disassembly for debugging; JSON build facts; SHA256SUMS. Source in ../../firmware; reproducible setup/build in ../../docs/TOOLCHAIN.md. Original firmware preserved separately in ../../reference/original.
