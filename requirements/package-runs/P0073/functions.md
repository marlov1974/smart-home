# P0073 function design

Original inventory extractor: accept optional privately held original BIN, verify hash; scan descriptors/headers, classify table membership; dispatch/payload influence analysis with bounded original-code emulation; produce only numeric/semantic JSON conclusions. External extractor: pinned repo source paths, enumerate parsers/setters/service/enum definitions with provenance; normalize facts and retain conflicts without copying code blocks. Coverage reports count every parsed descriptor/register definition and unresolved mapping.

Standalone build/setup: portable pinned toolchain download and checksum, isolated venv; build host and firmware tests without proprietary inputs. Release tool produces own BIN/ELF/MAP/disassembly/checksums/source metadata after tests/determinism. Final review adds release ELF debug-path stripping, MAP path normalization and packaged-artifact host-path rejection; exercised by hosted CI. Sanitizer inventories explicit candidate files and blocks secrets, private paths, prohibited reference binaries/manuals/dumps. Helper default host removed; explicit operator target required.

Firmware functions unchanged. Public docs and private package evidence store scope, provenance and release blockers. No actuator or visibility functions.
