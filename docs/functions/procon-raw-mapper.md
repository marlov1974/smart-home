# P0081 asynchronous diagnostic functions

cn_command validates isolated81d1 requests, enforces idempotency/sequence and excludes active control. cn_tick schedules a diagnostic at a complete service boundary; diagnostic A3 retains exclusive ownership across retries. cn_feed correlates frame/checksum/code and service number; terminal states retain raw bytes. cn_read exposes the600 schema through existing ABI. modbus_reply gates exact FC16/600 separately from control300.

raw_mapper.envelope/plan constrain direct and manual service codes. Shelly.preflight/health/snapshot require identity, native client mode, idle controls and coherent results. scan bounds submissions/polls, observes stop/expiry and writes resumable evidence. report differentiates raw observations from manual hypotheses. No arbitrary write/control transport exposed by the mapping CLI. See procon/modular/RAW_API.md and requirements/package-runs/P0081.
