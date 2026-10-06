# P0069 changelog

Status: software-built-and-verified; physical M1 pending operator flash. User-visible behavior intended: FC04 input0 returns888 with fixed slave1/96008N1. No CN105 support or writable controls.

Added procon/firmware startup/linker/platform/parser; tools for pinned development setup, image validation, static original/updater analysis; sanitizer host tests and actual-ELF mocked-peripheral emulation; release BIN/ELF/MAP/disassembly/metadata/hash list. Updated Procon living docs, package review/design/function design, bootstrap manifest, function catalog and REPOSITORY_FILES.md. No unrelated G2 runtime edited. Existing dirty P0068 checkout untouched.

Verification: GCC warnings-as-errors; 64 CRC bit mutations, all256 unit IDs, exceptions/truncation/capacity checks, RTU gap/error/overflow/wrap recovery,20000 malformed packets under ASan/UBSan; six ARM emulation scenarios; ELF vector/load bounds; forced deterministic rebuild; original archive/BIN checksums. First ARM invocation failed because sandbox denied JIT; same test outside sandbox passed. Host simulation is not electrical proof.

Known uncertainty: exact chip/package/density, device bootloader implementation and physical baud/DE timing. User explicitly authorized inferred-MCU experiment and will flash externally. No live commands or writes performed. Runtime state of live Procon unchanged by Codex.

Knowhow promotion intentionally kept within procon/docs/TOOLCHAIN.md and HARDWARE.md: JIT sandbox behavior and evidence-based STM32 vector matching are local firmware-development lessons, not G2 Shelly runtime rules.

Next bootstrap: this changelog, procon/README.md, HARDWARE.md, RS485_MODBUS.md, RECOVERY.md, release README. After operator flash, read input0 only, record result; do not start M2/CN105 before success. File index updated for all additions.
