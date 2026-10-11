# P0089 function design

- controls.ownership: prior owner, request/release/fault gates -> selected owner; pure model of CE9C8, including invalid owner normalization.
- controls.inhibit_status: local/remote masks and owner -> selected status; preserve previous status for invalid owner.
- controls.counter_step: enabled0/1 -> byte counter and state, invalid preserves; explicit wrap.
- controls.demand_selection: raw p13 staging/override -> selected minimum; no percent/kW claim.
- controls.target35: payload/profile/prior target slots -> separate heating/cooling zone storage, FFFF disabled/ignored.
- codec.frame/parse: explicit FC type/payload, bounded22 bytes and sum check. No implicit production-ready packet planning.
- codec.a3: parse raw format, selector and value without invented scalar meaning; reject maintenance in read planning.
- models.ServiceObserver: explicit owner, pending/cache/freshness/cancelled status, no guessed firmware rearm.
- models.SettingsObserver: explicit synthetic events; preserve applied flag through abort/timeout; block unqualified category apply.
- report.build/render: evidence-backed field catalog,47-block work ledger, route backlog and Swedish readable reports; deterministic outputs and schema checks.

No transport methods, shared helper edits or production changes. Tests tied to branch semantics and artifact conservation.

Added target32 (B9AD0/B9BFE bounded store slice) and coupled_modes (BBE92 table-based requested-mode slice) to test mode context, two-zone routing and profile-dependent coupling. Neither models full selected/effective target publication.
