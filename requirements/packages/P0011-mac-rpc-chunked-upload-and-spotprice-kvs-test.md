# Package P0011: Mac RPC chunked upload and spotprice KVS test

## Status
planned

## Package order
P0011

## Primary area
G2 / Mac tooling / Shelly live deploy tooling / spotprice test

## Decision summary

P0010 proved that the Mac can deploy an inert Shelly script to dampers, start it and observe `hello world` in the Shelly debug log.

P0011 extends the Mac-as-installer path by proving that the Mac can upload a larger script using in-memory RPC upload chunks and verify the script through log output and KVS reads.

The next live test script is:

```text
spotprice_v0_9_0
```

It should be based on the existing G1 spot price fetch code and should use the same spot price KVS contract as G1. Dampers has no production KVS state that this test can damage, so this package may allow the G1 spotprice-owned KVS keys, but Codex must identify and document the exact allowed KVS keys before live execution.

Before deploying `spotprice_v0_9_0`, P0011 must remove the P0010 test residue script `hello_v1_0_0` from dampers.

## Solution model

There are now two distinct chunk concepts:

```text
repo/deploy chunks:
  dep/s/ch/** files for future Shelly-side pull/install models

RPC upload chunks:
  temporary Mac-memory chunks used to send large scripts to Shelly over RPC
```

P0011 focuses on RPC upload chunks. It should not rely on pre-generated `dep/s/ch/**` files for Mac direct deploy.

Mac direct deploy flow:

```text
read built script
split script into bounded RPC upload chunks in memory
ensure target script slot exists
clear/replace script code safely
send chunks by RPC
verify script code/list/status when possible
start script
listen to debug log
read allowed KVS keys
store package-run evidence
```

## Current behavior

P0010 can upload and run `hello_v1_0_0` on dampers and observe logs. It does not yet prove upload of a script large enough to require chunked RPC transport, and it does not verify script output through KVS.

## Problem

Shelly RPC request size is expected to be limited in practice. Large scripts may not be safely uploaded in one RPC call. The Mac installer/orchestrator therefore needs chunked upload behavior even if repo chunk artifacts are not used for normal Mac deploy.

## Target behavior

Create or extend Python 3 standard-library Mac tooling so it can:

- remove only `hello_v1_0_0` from dampers as P0010 cleanup
- build or prepare `spotprice_v0_9_0`
- upload `spotprice_v0_9_0` to dampers using bounded in-memory RPC chunks
- use a conservative default upload chunk size, e.g. 1500 bytes unless Codex documents a better tested value
- start `spotprice_v0_9_0`
- capture bounded debug-log evidence
- read and verify the G1 spotprice KVS keys written by the script
- leave `spotprice_v0_9_0` installed and stopped unless package-run design chooses a safer cleanup
- record live-test evidence under `requirements/package-runs/P0011/`

Codex must inspect the G1 spotprice code before implementation and document:

- source file(s) copied or adapted
- KVS keys used by the G1 spotprice script
- any changes required to make the script safe for dampers
- the expected KVS verification criteria

If Codex cannot identify the G1 spotprice source and KVS contract, it must stop with `STOP` or `WARN` before live execution.

## Script naming rule

P0011 live deployment may only create/update/start/stop/delete these script names:

```text
hello_v1_0_0
spotprice_v0_9_0
```

`hello_v1_0_0` may only be stopped/deleted as P0010 cleanup.

`spotprice_v0_9_0` is the only script that may be uploaded and started by this package.

No `g2-` script names are allowed.

## Dampers live-test boundary

Allowed live actions:

- read device status
- read script list/status
- stop/delete only `hello_v1_0_0` during initial cleanup
- create/update/start/stop only `spotprice_v0_9_0`
- upload code to `spotprice_v0_9_0` using bounded RPC chunks
- read or stream debug log
- read only the documented G1 spotprice KVS keys
- if needed, delete only the documented G1 spotprice KVS keys if P0011 design explicitly chooses cleanup

Forbidden live actions:

- no device setting changes
- no Wi-Fi/network/MQTT/Bluetooth/cloud changes
- no component/config changes
- no actuator/output/switch/cover/relay RPC calls
- no real damper control code
- no script names other than `hello_v1_0_0` cleanup and `spotprice_v0_9_0`
- no KVS writes from Mac except optional cleanup of documented spotprice-owned keys if explicitly designed
- no Shelly-side installer implementation

## Non-goals

- No production spotprice integration.
- No Home Assistant integration.
- No FTX/heating/damper control.
- No Shelly-side installer.
- No device setting or component changes.
- No external Python packages.
- No general multi-device registry yet.

## Invariants

- Python standard library only.
- Mac deploy remains the installer/orchestrator path.
- RPC upload chunks are temporary transport chunks, not repo source structure.
- The script upload chunk size must be bounded and documented.
- The package must not use actuator/output/switch/cover/relay RPCs.
- Live log and KVS verification must have timeouts.
- The allowed KVS key list must be documented before live execution.

## Knowledge updates

Update if needed:

- `memory/knowhow/shelly.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `docs/functions/mac/shelly-live-deploy-tool.md`
- `docs/functions/mac/shelly-build-tool.md`

## Files to inspect

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `requirements/packages/P0010-shelly-deploy-tool-and-log-listener.md`
- `requirements/package-runs/P0010/logs/live-dampers-hello.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- G1 spotprice source in local `dev/shelly` or repository source
- G1 spotprice KVS documentation or implementation

## Files allowed to change

- `src/mac/tools/**`
- `tests/mac/tools/**`
- `src/shelly/fixture/**`
- `src/shelly/spotprice/**`
- `build/shelly/**`
- `dep/s/**` only if Codex documents why generated repo chunks are still needed for this package
- `docs/functions/**`
- `memory/knowhow/**`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `requirements/package-runs/P0011/**`
- `requirements/packages/P0011-mac-rpc-chunked-upload-and-spotprice-kvs-test.md`

## Forbidden changes

- no G1 repository changes
- no real FTX runtime source changes outside copied/adapted G2 spotprice test source
- no Shelly-side installer implementation
- no device configuration changes
- no actuator/output control code
- no external Python package dependencies
- no broad refactor outside Mac deploy/build tooling and test source needed for P0011

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0011/review.md
requirements/package-runs/P0011/design.md
requirements/package-runs/P0011/functions.md
```

Use the P0007 phase-gate model.

The design must include a specific section:

```text
G1 spotprice source and KVS contract
```

with source paths, allowed KVS keys and live verification criteria.

## Live test/debug policy

Live testing allowed: yes, dampers only

Live write actions allowed: yes, but only for:

- stopping/deleting `hello_v1_0_0`
- creating/updating/starting/stopping `spotprice_v0_9_0`
- `spotprice_v0_9_0` writing its documented G1 spotprice KVS keys

Shelly log capture required: yes

KVS read verification required: yes

Max implementation/debug attempts: 3

Codex must stop immediately if:

- it cannot safely identify the dampers endpoint
- it cannot identify the G1 spotprice source/KVS contract
- a required live command exceeds the allowed action list
- the spotprice script contains actuator/output/relay/switch/cover/device-config behavior

## Test cases

### TC1: Cleanup P0010 hello residue
Given dampers contains `hello_v1_0_0`
When P0011 live test starts
Then the tool stops and deletes only `hello_v1_0_0` and verifies it is gone.

### TC2: Chunked upload uses multiple RPC chunks
Given the `spotprice_v0_9_0` built script is larger than the configured upload chunk size
When the Mac deploy tool uploads it
Then it sends multiple bounded RPC upload chunks and records the chunk count.

### TC3: Chunked upload rejects oversized chunk configuration errors
Given an invalid upload chunk size
When upload is attempted
Then the tool fails clearly before live writes.

### TC4: Spotprice script deploys and starts
Given `spotprice_v0_9_0` is built
When the tool deploys it to dampers
Then script list/status shows `spotprice_v0_9_0` present.

### TC5: Log evidence is captured
Given `spotprice_v0_9_0` runs
When the tool listens to `/debug/log`
Then expected spotprice progress or success text appears within the timeout.

### TC6: KVS evidence is verified
Given `spotprice_v0_9_0` runs successfully
When the Mac reads documented spotprice KVS keys
Then expected spotprice KVS data is present and parseable according to criteria documented in `design.md`.

### TC7: No forbidden operations
Given the P0011 live boundary
When reviewing tool code, package-run evidence and log evidence
Then there are no device setting changes and no actuator/output/relay/cover/switch/component/network/MQTT/Bluetooth/cloud operations.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest <spotprice manifest> --build-root build/shelly --dep-root dep/s
git diff --check
```

For live dampers test, Codex must document the exact command it ran, target endpoint, upload chunk size, upload chunk count, log timeout, KVS keys read, KVS values or safe summaries, and final script status.

## Runtime health checks

During live test, check and record:

- target endpoint used
- script list/status before cleanup
- `hello_v1_0_0` cleanup result
- upload chunk size and chunk count
- script list/status after deploy
- start/stop result
- bounded log excerpt
- KVS read results for documented spotprice keys
- absence of forbidden RPC calls in package/tool/log evidence

## Deployment plan

No production deployment. This is a controlled live test on dampers only.

## Rollback plan

P0011 may leave `spotprice_v0_9_0` installed and stopped as harmless test evidence if documented in completion notes, or remove only `spotprice_v0_9_0` if the package-run design chooses cleanup.

P0011 must remove `hello_v1_0_0` at the start as P0010 cleanup.

Codex must not remove or alter unrelated scripts.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- G1 spotprice source path(s)
- allowed KVS key list
- files changed
- tests run
- live test command and target endpoint
- upload chunk size and count
- log evidence path
- KVS evidence path or section
- verification results
- commit SHA after push
- uncertainty
- diff summary

## Completion notes

Filled after implementation.
