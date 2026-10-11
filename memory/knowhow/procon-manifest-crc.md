# P0080 — manifest identity and receive windows

Measured2026-10-09 in physical snapshot OTA: hashing a manifest including its own appended CRC32 and fixed trailer produced the same whole-buffer CRC for two different valid releases (c13b1aef). The prefix56 CRC changed9521f732→d9dd3c62. Never use a CRC over data plus its own CRC as a content/version identity. Validate the stored CRC over the original data and expose that data-only digest or an independent build identifier. This does not provide cryptographic authenticity.

A300ms host receive window was shorter than the full-set commit operation; the later ACK caused the unsolicited-RX guard to reject the next send. Keep the receiver open for the command's maximum processing time, including whole-image scans. Exact cached commit replay recovered without rewriting flash. Host now waits2s for COMMIT/EXIT and has a700ms delayed-ACK regression; BL2 identity fix remains pending. See requirements/package-runs/P0080/snapshot-live-report.md.

BL2 protocol2 follow-up implements the prefix56 digest, explicit status/wire
version bump and host metadata gate. Regression uses two valid manifests with
the same whole-buffer CRC and verifies stale-base rejection before erase.
Physical first installation authorized; normal boot qualification pending.

Physical normal boot now verified: protocol2 and prefixCRC d9dd3c62 match the release; three valid snapshots and healthy CN105 updates. A complete protocol2 OTA transaction remains a separate physical qualification.

Physical protocol2 full-set OTA now passed on D2 with D1 in acknowledged WAIT900s:199/199 frames, no manual recovery, prefix fingerprint correct after reset, telemetry verified. Two-second COMMIT/EXIT windows worked in this run. WAIT expiry response remains separately unverified.
