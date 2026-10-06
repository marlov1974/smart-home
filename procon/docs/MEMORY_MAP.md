# P0069 memory map

Original: 96,692 bytes mapped at0x08008000, exclusive end0x0801F9B4. Vector SP0x20010000, reset Thumb0x0800A341. Reset helper0x0800A330 explicitly writes VTOR0x08008000.

Inferred L433 family supports128/256KiB flash and64KiB SRAM (48KiB SRAM1 plus16KiB SRAM2). Exact fitted density/package unverified. M1 uses only16KiB flash [0x08008000,0x0800C000) and16KiB SRAM1 [0x20000000,0x20004000), with2KiB minimum stack reserve. It does not depend on SRAM2 aliasing.

Candidate: raw1704 bytes, padded2048 bytes (one2KiB page), address range[0x08008000,0x08008800). Stack0x20004000, reset0x0800818D. Code never unlocks/programs/erases flash. ELF checker rejects flash load segments below application base or outside conservative bounds.

[0x08000000,0x08008000) is the inferred resident bootloader reservation. Device-side bootloader is absent from supplied archive; its erase implementation has NOT been disassembled or independently verified. Existing vendor updater use and application VTOR support the boundary inference.
