# P0074 documentation conformance checker

Standalone tests/test_platform_spec.py has independently written crc16, packet, modbus_response and main functions. Inputs are docs/platform-spec.json, docs/verification-vectors.json and Markdown references. It checks reflected-bit CRC, profile response/exception/silence rules, additive CN105 framing/checksums, decode/matching expectations, exclusive retries, attempt limits, unsigned wrap, platform bounds/metadata and local links. It emits PASS or an assertion failure and has no firmware imports, network or device effects. Makefile test/host-test invoke it; hosted CI verifies the whole unchanged firmware suite as well.

Function definitions belong to the standalone repo; Smart Home stores package traceability only. This checker demonstrates documentation consistency, not hardware qualification or exhaustive protocol correctness.
