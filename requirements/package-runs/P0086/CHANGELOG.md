# P0086 changelog

2026-10-11: synchronized main to 6586d05 before package work; recorded review, design and function design. Added offline energy/A3 decoder, settings observer and preservation diff, explicit-profile UART1 codec/reader/log decoder, pinned operand checks and instruction-emulator proof.

Added focused qualification reports and physical handoff. Corrected P83's intermediate-versus-emitted BCD interpretation; identified query-induced rounding loss and 16-bit memory aliasing. Previous reports and production code remain unchanged. Updated catalog/knowhow and regenerated the index. Results and actual commands are recorded in verification.json. All fixtures are synthetic; no physical test or deployment occurred.

Before publication, main advanced with four P0087 registration commits. Fast-forwarded to c4b75ee while preserving P0086 changes and regenerated the shared file index. No package scope conflict or source conflict occurred. P0087 was read as the new bootstrap entry but not executed.
