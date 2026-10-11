# P0081 implementation design

Keep P0080 ABI/layout/BL2 and existing FC16/300 intact. Introduce FC16/600 count8 diagnostic envelope; FC04/600..631 sticky snapshot. Implement bounded private state in common/cn105.c, through existing cn_command/cn_read exports; dispatcher routes diagnostic submits using existing debug_command veneer. No new export or layout.

Envelope: magic81d1, API1, opcodeFD, nonzero16-bit monotonically increasing ID, kind1 DIRECT/2 A3, code8/16-bit, zero, zero. Optional parameters unsupported. Busy/conflicting ID rejected; identical latest request idempotent. Hardware A3 allowlist mirrors vetted manual list.

Schedule diagnostic only after completed background A3 and full FAST round. Once A3 begins, retry exclusive at1000ms up to10 attempts;800ms reply timeout;50ms turnaround. Queue+operation expires30s; disconnect aborts. Block control submits during pending diagnostic and diagnostics during control missions. Terminal status sticky; raw complete CN105 frame preserved, malformed frame marked invalid. Late identical wire replies cannot be cryptographically distinguished (CN105 has no sequence), so quarantine after each operation and document limitation.

Host utility: native Shelly Modbus client, explicit capability/identity/mission/scheduling gates, conservative pacing, two separated passes, baseline subset before full enumeration, JSONL/checkpoint/CSV/report, stop-file and runtime cap. No auto mode switch. Read-only baseline available before activation.

Tests: real CN105 and Modbus frames, CRC/wrong echo/timeout/duplicate/stale/conflict/A3 high code/exclusion, arbiter regressions, full host/ARM and OTA compatibility/slot sizes; mocked CLI256 enumeration, resume, stop, status and reports.
