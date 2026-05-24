# P0016 Consistency Review

## Result

`WARN`

P0016 is implementable and inside the G2 pre-production package model, but it depends on live discovery of the supply UNI physical id and status/component shape before live writes. That uncertainty is explicitly acknowledged by the package and can be handled with stop gates before script deployment.

## Evidence Reviewed

- `README.md`
- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- Manifest read-order files through `P0014`
- `requirements/packages/P0016-supply-uni-telemetry-publisher-proof.md`
- `memory/infrastructure/devices.md`
- `memory/physical/ftx/sensors.md`
- `src/mac/tools/shelly_build/**`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/**`
- G1 reference files from `marlov1974/shelly` `origin/main` via read-only `git show`

## Consistency Findings

- Package scope is compatible with G2 source/build/deploy separation: source under `src/shelly/supply_uni`, built scripts under `build/shelly/supply_uni`, generated Shelly artifacts under `dep/s`.
- The package does not require production activation and keeps dampers as the development/planner receiver.
- The `tele.supply_uni` KVS contract follows the design principle that measurement-owning devices publish compact brain-local telemetry instead of creating another central poller.
- The package correctly forbids actuator/output/device-config changes. The intended Mac live-tool changes can remain limited to identity reads, script create/update/start/stop for `supply_uni_pub` and `supply_uni_refresh`, debug-log capture, and readback of `tele.supply_uni`.
- The package's "no `g2` runtime namespace" rule conflicts with older P0015 weather naming, but P0016 is explicitly a new runtime-contract rule and can be applied only to P0016 names without changing P0015.
- G1 reference source confirms the supply UNI component IDs and parsing roles:
  - `voltmeter:100` -> supply pressure
  - `input:2` -> supply RPM/frequency
  - `temperature:100` -> post VVX
  - `temperature:101` -> outdoor
  - `temperature:102` -> to outdoor
- G1 `master` confirms the 15 second tick and busy-skip pattern, but P0016 must not copy the full score dispatcher.

## Warnings / Assumptions

- The local G1 checkout is on a divergent setup branch, so G1 source was read from `origin/main` instead of the working tree.
- `ftx-supply-uni` has no documented physical Shelly id yet. Live verification must record it before live writes and update `memory/infrastructure/devices.md` only if the evidence is reliable.
- Supply UNI status shape must be discovered live. Implementation may support expected `Shelly.GetStatus` component keys, but live deployment must stop if the required values are not exposed.
- Remote KVS write from supply UNI to dampers is expected to work through Shelly `HTTP.POST`/JSON-RPC to `http://192.168.77.30/rpc`, but live evidence must verify it before considering the package complete.

## Stop Gates

Stop before live writes if:

- supply UNI endpoint cannot be identified safely
- dampers identity does not match `8813bfd99f54`
- supply UNI status does not expose the required values and no safe component read fallback is clear
- adapted scripts contain switch/relay/cover/output/device-config operations
- the live command list would exceed P0016 allowlists
