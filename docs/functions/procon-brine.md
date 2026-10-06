# P0071 Procon service operations

service.c owns two retained sample records and IDLE/READY/WAIT_REPLY/WAIT_RETRY/COOLDOWN/LINK_DOWN states. svc_init resets; svc_link handles reconnect cancellation; svc_tick ages/invalidate/cache/cooldown; svc_due offers a request; svc_sent records attempt/start; svc_reply validates owner/echo/status and retains raw frames; svc_timeout/svc_bad_frame count/retry; svc_read exposes read-only map. Private pair/advance/retry implement endian and lifecycle. No heap or persistence.

cn105.c begin/release/disconnect arbitrate one transaction at a time; cn_feed still owns framing/checksum and routes A3 only after validation. cn_tick applies timeouts,normal priority,service retries and50ms turnaround. No blocking service callback. Main's response buffer remains37bytes; modbus_reply permits addresses0–67,max16words. Existing UART helper drains CN105 while RS485 TX waits. No platform/startup/linker change.

read_brine.py request_block/capture record only FC04 with UTC/raw data; decode_samples brackets payload with completion counters and reconstructs frames with explicit provenance. It never labels candidate temperatures hardware-correlated. Host and ARM cases cover package contracts; physical evidence pending. Detailed timings/map:../../procon/docs/BRINE.md.
