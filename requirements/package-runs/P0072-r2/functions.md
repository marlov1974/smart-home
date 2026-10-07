# P0072 r2 functions

New control module: ctl_init resets RAM session; ctl_submit validates atomic command/sequence; ctl_tick ages lease; ctl_next offers next owned transaction; ctl_reply consumes only transaction-matched GET/SET evidence; ctl_timeout advances bounded recovery; ctl_read exposes status and original snapshot; ctl_busy reports pending control scheduling. Internal action planning/encoding/readback compares one documented field per step. No MMIO/flash/network side effects; CN105 module owns transmission.

cn_tick integrates control only outside service operations; cn_feed dispatches owner4 replies; cn_read exports revision2/capabilities/status and extendeddiagnostics. Modbus adds tightly scoped FC16, preserving no broadcasts/FC06. Snapshot reader accepts revision2 identity and additionalcontrolstatus. Add dedicated native/integration/ARM tests, docs and release. No unrelated GPIO/watchdog changes.

Added offline control_command.py encoder with exact validation/CRC; it sends nothing. ARM mock now models SET side effects and GET verification for an explicit control-test case; default whitelist still forbids every SET. Retry intervals are measured at first wire byte, not final byte, to exclude variable serialization latency. Flow action adds freshGET26 preflight before preserving DHW/mode fields.
