# P0063 Live deploy FTX state VVX efficiency guard

## Goal

Deploy the current G2 FTX state script to the live FTX dampers device so `VVX efficiency` is forced to `0` when `ftx.state.run.vvx` is `0`.

## Background

P0058 fixed the active state recipe path in source. P0062 also fixed the legacy feature path. Live dampers still reports a non-zero `Number 202` while `ftx.state.run.vvx` is `0`, which means the source fix has not been deployed to the HA-facing virtual component host.

## Scope

Allowed source/tool changes:

- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- package-run evidence under `requirements/package-runs/P0063/**`
- generated build evidence under `build/shelly/ftx/**` if needed

Allowed live target:

- `ftx-dampers`
- device id suffix `8813bfd99f54`
- NAT endpoint `http://192.168.86.240:8030/`

Allowed live writes:

- upload code to existing script `state_v1_8_0`
- start script `state_v1_8_0`
- writes performed by `state_v1_8_0` itself:
  - `Number.Set` for FTX state virtual numbers `201`, `202`, `203`
  - `KVS.Set` for FTX aggregate state keys already written by the state script

Forbidden live actions:

- no output/relay/switch writes outside the existing state script behavior
- no executor script upload/start
- no `brain` script upload/start
- no writes to `ftx-vvx` unless a later package explicitly allows it
- no G1 repository edits

## Required Verification

Before live deploy:

- prove the built state script contains the `!ctx.run || !ctx.run.vvx` guard
- verify the live endpoint identity matches `ftx-dampers`
- verify `Number 202` exists on dampers

After live deploy:

- verify script start completes with `state DON`
- verify `Number 202` is `0` when `ftx.state.run.vvx` is `0`
- verify `ftx.state.hist` is `{r0:0,r1:0,r2:0}` when `ftx.state.run.vvx` is `0`
- run relevant unit tests
- run `git diff --check`

## Commit/Push Authorization

If verification passes and the diff is inside package scope, this package authorizes commit and push.
