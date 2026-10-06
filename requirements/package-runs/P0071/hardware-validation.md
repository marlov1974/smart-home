# P0071 hardware attempt 1 — 2026-10-06

Operator reports flashed. Read-only Modbus verification captured30 sample groups/180FC04 reads at20:05:02–20:05:32UTC; no RPC failures. New user confirmation of flashing was treated as authorization to perform the follow-up read-only verification. No device register/settings writes.

All baseline blocks:888/build71,compressor20Hz,valid1,age0–2s. Normal reply count139→154,link1,UART/protocol errors0. Service replies152→162. Latest raw payloads observed: A3 00 1C 00 +12zero bytes, and A3 00 1B 00 +12zero bytes. Both service statuses remained0(pending); no completed samples, no decoded temperature. Retry gap1000ms within the active operation;20228ms observed across cooldown/start. Service28 retry count advanced1→8 then cooldown, exhaustion15→16, cycles7→8; next service27 started and retried. Repeated pending replies therefore reach finite exhaustion rather than freezing normal telemetry. Service-error counter0 excludes pending/exhaustion, which has its own counter.

No completed frames or display correlation exist. Zero payload data is not0C. Transport/scheduling respond; unresolved issue is why service computation never completes. Possible causes (not established): service-mode prerequisite, need for different transaction sequencing, or pending duration longer than10attempts. Do not select a cause from this capture alone. No firmware changes made during verification.

Evidence:procon/analysis/live/20261006T200502Z-p0071-first-readback.jsonl. Hardware attempts1/3; brine goal not achieved. LED was not separately reconfirmed this attempt.
