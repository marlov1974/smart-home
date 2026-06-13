# P0063 Review

## Classification

WARN

## Evidence

- Repository was synchronized before this package run.
- `ftx-dampers` at `http://192.168.86.240:8030/` reports device id `shellypro1pm-8813bfd99f54`.
- `ftx-vvx` at `http://192.168.86.240:8040/` reports device id `shellypro1pm-8813bfdaa0c0`.
- Both devices have a `state_v1_8_0` script, but only dampers has `Number 202`.
- Dampers currently reports:
  - `Number 202 = 54`
  - `ftx.state.run.vvx = 0`
  - `ftx.state.hist = {r0:53.8,r1:53.8,r2:53.8}`

## Consistency Result

The request is consistent with P0058 and P0062: the G2 source contains the desired guard, but the live HA-facing dampers state script has not been refreshed. The package is live-write scoped and therefore classified as `WARN`, not `PASS`.

## Safety Boundary

This package will only deploy and start `state_v1_8_0` on dampers. It will not deploy or start brain/executor scripts and will not write to `ftx-vvx`.
