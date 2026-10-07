# P0072 Procon MVP function contracts

`tele_init/tick/invalidate/accept/read` own20-value cache, ages/generations, reference-backed decoders, range checks and raw FAST payloads. Pure API values have no actuation. `get/combine/brine` propagate validity and calculate signed differences/water W with int64 intermediate, invalid source/skew rejection. See procon/docs/MVP_API.md for exact field/units contract.

`cn_tick/begin/feed` sequence seven FAST GETs, validate response query ownership, then defer all other traffic through one complete service operation. `svc_start_cycle/advance/due/reply` use round-robin code table27/28 with finite10attempt operations and1s cadence. Native and actual-ELF tests assert outgoing whitelist and exclusion, timeout/wrap, malformed replies, simultaneous UART paths.

`read_mvp.capture/main` log timestamped FC04 blocks only, bracketing values/raw reads with generation+status. That statement applied to r1. Revision 2 adds the explicitly gated control API described in [procon-control.md](procon-control.md); the read helper remains read-only.
