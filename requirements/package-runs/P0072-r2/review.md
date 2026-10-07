# P0072 r2 review — WARN

Explicit operator request: build deferred controls. Source23f2c94 synchronized; implement under P0072, not documentation-only P0074. Clone isolated from earlier readback evidence. Preserve telemetry addresses, A3 whole-operation exclusivity and native safety. No device writes or flash in this build.

External F1p pinned7687d11 defines SET41/basic32 masks power01,mode08,DHWtarget20,flow80 and controller34/boost01; GET26/09/28 permit readback. Generic61 handler in reference ignores payload, so it is only transport evidence: matched fresh GET is mandatory for application status. Physical SET correctness is pending operator-flashed testing; do not claim verified hardware controls.

Plan conservative atomic FC16 envelope; runtime snapshot before first write; explicit OFF/AUTO(restore)/FIXED_FLOW/DHW and target-only commands; one active session; lease30–1800s; no pump overrides. Restore only fields touched. Reject unsafe/unrecognized native starting states. Failures enter restoration, retain snapshot until confirmed. Power loss resets RAM: no invented persistent storage/bootloader writes; startup remains read-only. External operator must retain original settings; autonomous power-failure restoration remains unresolved and disclosed.
