# P0069 operator flashing and recovery

The user performs all flashing physically on another computer. Codex performs no flash or register writes. M1 is an experimental candidate with inferred STM32L433 hardware, not hardware-verified firmware. The vendor bootloader itself is not in the archive: preservation is expected from the existing vendor application update path, not independently proven.

Use the unchanged vendor updater from reference/original and its complete `Procon Firmware Update Instructions (v1.3).pdf`. Keep original A1M_R5_Release_08008000.bin available on the flashing PC. Original hash:2ae03b0cdc684bcccbf9f5281878175f5ca53b144e3e32cc223159fcc4654766.

Vendor procedure: record current DIP settings, disconnect CN105 power, connect Windows USB-RS485, set all eight DIP switches OFF, select raw BIN and COM port, click Program, then connect CN105 as directed to enter resident bootloader. Wait for successful completion. Disconnect CN105, restore original DIP positions, reconnect for normal application startup. Follow the PDF if its wording differs; do not use mass erase/SWD or write address0x08000000.

Select releases/P0069-m1/procon-m1.bin for the experimental application, not the ZIP, ELF or original ZIP. File contains application bytes only, intended for existing updater's offset0 -> application base0x08008000 mapping. Do not manually prepend bootloader padding.

After startup, read input register0 via FC04/slave1/96008N1. Only expected value is888. No CN105 telemetry/control is supplied by M1. If no reply, first check updater reported success, restore DIP settings and normal RS485 connection, then restore unchanged original BIN using the same vendor procedure. Recovery on this particular device has not been performed in P0069. Do not treat a successful simulated read as a hardware recovery guarantee.

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.
