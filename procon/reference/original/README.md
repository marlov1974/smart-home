# Original Procon reference — imported 2026-10-06

The user supplied this original v3.1.05 archive. Keep ZIP and BIN byte-for-byte unchanged.

- Archive: `Proon+Firmware+Update+Tool+(v3.1.05).zip`
- Application: `A1M_R5_Release_08008000.bin`, 96,692 bytes
- Application SHA-256: `2ae03b0cdc684bcccbf9f5281878175f5ca53b144e3e32cc223159fcc4654766`
- Initial stack pointer: `0x20010000`
- Reset vector: `0x0800A341` (Thumb entry `0x0800A340`)

Validation passed: complete ZIP CRC check, expected application size/hash, and equality between the extracted BIN and its ZIP member. See `IMPORT_MANIFEST.json` for archive hash and provenance. These checks establish reference identity, not MCU identity or flash safety.

The archive also retains the vendor updater and `Procon Firmware Update Instructions (v1.3).pdf`. The vendor procedure uses a Windows PC and USB-to-RS485 adapter, all eight DIP switches OFF during bootloading, and CN105 connection to power the device at the prescribed step. Original DIP positions must be recorded and restored. Consult the complete vendor PDF before attempting recovery. This procedure has not been executed or verified on this device in this import.

No replacement image was generated and no live device was changed. Exact MCU, flash geometry, bootloader preservation and updater erase behavior remain to be established before a replacement BIN can be delivered. Importing the reference does not complete M0 or M1.
