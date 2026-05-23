# Package P0010 Review Evidence

## Package

`P0010`

## Result

PASS

## Files Checked

- `AGENTS.md`
- `README.md`
- `memory/bootstrap-manifest.json`
- mandatory bootstrap files listed by the manifest
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/infrastructure/devices.md`
- `memory/infrastructure/router-nat.md`
- `memory/knowhow/shelly.md`
- `memory/knowhow/codex.md`
- `requirements/packages/P0008-g2-shelly-build-deploy-tools.md`
- `requirements/packages/P0009-shelly-build-wrapper-and-metadata.md`
- `requirements/packages/P0010-shelly-deploy-tool-and-log-listener.md`
- `src/mac/tools/shelly_build/**`
- `tests/mac/tools/shelly_build/**`
- `src/shelly/fixture/**`
- G1 context for dampers endpoint and Shelly RPC patterns:
  - `/Users/marcus.lovenstad/dev/shelly/AGENTS.md`
  - `/Users/marcus.lovenstad/dev/shelly/devices/dampers-8813bfdaa0c0/README.md`
  - `/Users/marcus.lovenstad/dev/shelly/memory/components/shelly/03-rpc-patterns.md`
  - `/Users/marcus.lovenstad/dev/shelly/memory/ftx-digitalt/02-device-topology.md`
- Shelly official Gen2 Script/RPC documentation for method names and JSON-RPC shape.

## Consistency Review

P0010 is consistent with the current repository truth.

P0008/P0009 provide deterministic built Shelly scripts and generated deploy chunks, but no Mac-side live deploy/log harness. P0010 adds that missing Mac-side tooling without implementing the Shelly-side installer or changing real runtime source.

The package's live-write boundary is narrow and explicit. It permits only the `hello_v1_0_0` script lifecycle on the dampers device and read-only status/log access. That is consistent with the dampers lab-device description and the local hardware safety rules.

The dampers endpoint is identifiable from G2 infrastructure memory:

```text
ftx-dampers / 192.168.77.30 / http://192.168.86.240:8030/
```

## Assumptions

- Operator-side NAT endpoint `http://192.168.86.240:8030/` is the correct live target for P0010.
- The device is Shelly Gen2+ and supports `Script.List`, `Script.Create`, `Script.PutCode`, `Script.Start`, `Script.Stop`, `Script.Delete`, and `Shelly.GetStatus`.
- The fixture role can be renamed to `hello_v1_0_0` for this package so the built script name matches the required live script name.
- Leaving or removing `hello_v1_0_0` after the live test is a design choice allowed by the package rollback plan.

## Decision

Continue implementation.
