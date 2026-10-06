# P0069 changelog

Status: software-built-and-verified; physical M1 pending operator flash. User-visible behavior intended: FC04 input0 returns888 with fixed slave1/96008N1. No CN105 support or writable controls.

Added procon/firmware startup/linker/platform/parser; tools for pinned development setup, image validation, static original/updater analysis; sanitizer host tests and actual-ELF mocked-peripheral emulation; release BIN/ELF/MAP/disassembly/metadata/hash list. Updated Procon living docs, package review/design/function design, bootstrap manifest, function catalog and REPOSITORY_FILES.md. No unrelated G2 runtime edited. Existing dirty P0068 checkout untouched.

Verification: GCC warnings-as-errors; 64 CRC bit mutations, all256 unit IDs, exceptions/truncation/capacity checks, RTU gap/error/overflow/wrap recovery,20000 malformed packets under ASan/UBSan; six ARM emulation scenarios; ELF vector/load bounds; forced deterministic rebuild; original archive/BIN checksums. First ARM invocation failed because sandbox denied JIT; same test outside sandbox passed. Host simulation is not electrical proof.

Known uncertainty: exact chip/package/density, device bootloader implementation and physical baud/DE timing. User explicitly authorized inferred-MCU experiment and will flash externally. No live commands or writes performed. Runtime state of live Procon unchanged by Codex.

Knowhow promotion intentionally kept within procon/docs/TOOLCHAIN.md and HARDWARE.md: JIT sandbox behavior and evidence-based STM32 vector matching are local firmware-development lessons, not G2 Shelly runtime rules.

Next bootstrap: this changelog, procon/README.md, HARDWARE.md, RS485_MODBUS.md, RECOVERY.md, release README. After operator flash, read input0 only, record result; do not start M2/CN105 before success. File index updated for all additions.

## Attempt2 update
Initial hardware verification failed: seven timeouts on input0. Operator confirms successful flash and restored wiring/DIP/power. Discovered definite UART configuration mismatch: original USART3 SWAP=1, M1 used0. r2 sets CR2_SWAP; no speculative stack change. Updated emulator requires correct wiring; old ELF fails, r2 passes all six scenarios and native tests. Release procon/releases/P0069-m1-r2, SHA256551772d8c5aee74dc084f1f0afc05ab65c85b5f7ad5ac32acf762d8feefa991e. Read-only live log: procon/analysis/live/20261006T175327Z-m1-readback.json. Operator r2 flash/readback pending. File index updated.

Final r2 operator steering: add500ms PC12 heartbeat and96KiB FF padding to clear original app footprint. Final r2 SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073; supersedes the intermediate unpublished2KiB r2 hash above. Seven ARM scenarios pass. Live r2 verification pending.
