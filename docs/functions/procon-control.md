# P0072 r2 control contracts

`ctl_command` validates the entire eight-word envelope before mutation, gates sequence/idempotence/renewal and accepts one leased session. `ctl_tick` handles wrap-safe expiry; `ctl_due` emits snapshot, one-dimensional SET, preservation preflight and verification GET actions only when CN105 ownership permits. `ctl_reply/ctl_timeout` require matching readback, mark potential changes before SET and retain the baseline across failed restoration. `ctl_read` exposes state/sequence/error/lease/snapshot diagnostics. `ctl_init` clears RAM and sends no reset-time guessed write.

`modbus_handle` accepts only exact addressed FC16 offset300/count8 after output-capacity validation. `cn105` schedules control outside complete A3 operations. No raw SET tunnel or native safety override. `control_command.py` only encodes offline bytes and never opens a network or serial connection.

[API and limitations](../../procon/docs/CONTROL_API.md). Native and actual-ELF simulations cover application and restoration; hardware verification remains pending. RAM lease is not power-loss-safe.

P0072 r3: `ctl_observe` retains matched GET28 payload/generation/age, including passive FAST polling. `gate28` uses operation-relevant binary flags and rejects unknown encodings, preserving rejection metadata. `ctl_read` exposes283–298; `ctl_tick` saturates sample age. Existing SET encoders/restoration are unchanged.
