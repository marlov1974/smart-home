# Package P0012: Correct spotprice template and clean deploy artifacts

## Status
planned

## Package order
P0012

## Primary area
G2 / Mac tooling / Shelly live deploy tooling / spotprice correction and cleanup

## Decision summary

P0011 successfully proved Mac-side in-memory RPC upload chunking, live log capture and KVS verification on dampers. However, it used the wrong G1 spotprice source as the G2 test template.

The correct G1 template is:

```text
marlov1974/shelly/devices/dampers-8813bfdaa0c0/scripts/spotprice.js
```

P0012 replaces the G2 spotprice test source with that correct template, updates the KVS contract, re-runs the chunked Mac deploy test on dampers and cleans up deploy artifacts/policy that no longer match the Mac-as-installer model.

## Correct template characteristics

The correct G1 dampers spotprice script:

- uses `elprisetjustnu.se`, not Tibber
- uses `PRICE_AREA = "SE3"`
- fetches 96 quarter-hour values
- converts them into 12 two-hour price blocks
- adds variable charges/tax/grid tariff model
- stores final values in KVS
- does not require a Tibber token

Expected script name in G2:

```text
spotprice_v0_9_0
```

## Correct KVS contract

P0012 must update the G2 spotprice test contract to these keys from the correct template:

```text
hp.price.2h
hp.price.date
hp.price.area
hp.price.status
hp.price.updated
```

Remove P0011-specific Tibber/fallback keys from the G2 spotprice test contract unless Codex finds they are still required by the correct template:

```text
hp.price.source
hp.price.debug
hp.price.debug.len
```

## Cleanup model

P0012 should clean up the mismatch left by P0011 without erasing useful package evidence.

Historical P0011 evidence must remain as package history. Do not rewrite P0011 evidence to pretend it used the correct source.

Current-state source/artifacts should be corrected.

Cleanup targets:

- replace current G2 `spotprice_v0_9_0` source with an adaptation of the correct G1 dampers template
- update tests and docs that reference the old P0011 Tibber/fallback KVS contract
- rebuild built spotprice artifacts
- ensure Mac live deploy uses in-memory RPC upload chunks from the built script
- remove or stop treating repo `dep/s/ch/**` chunks as required for Mac-direct deploy
- remove stale generated artifacts only when they are clearly obsolete and regenerated/unused

## Chunking policy

P0012 must make the chunk distinction explicit in docs and/or tool behavior:

```text
RPC upload chunks:
  required transport mechanism for Mac direct deploy of large scripts.
  Created in Mac memory by shelly_live, default around 1500 bytes.

Repo deploy chunks:
  optional artifacts for a future Shelly-side pull/install model.
  Not required for normal Mac-as-installer deploy.
```

P0012 must not remove the RPC upload chunking functions.

P0012 may keep repo chunk generation support in the build tool, but should avoid making generated `dep/s/ch/**` files mandatory for Mac direct deploy. If Codex changes defaults or artifact policy, it must document the decision in design and tests.

## Current behavior

P0011 produced a working `spotprice_v0_9_0` test that used a Tibber-based/fallback implementation. That proved chunked deploy and KVS verification but is not the desired spotprice template.

P0011 live evidence showed:

```text
upload_chunk_bytes=1500
upload_chunk_count=6
status=no_token
source=fallback
price_count=12
```

This should be superseded by a correct elprisetjustnu-based test in P0012.

## Target behavior

Create/update G2 so that:

- `spotprice_v0_9_0` is based on the correct G1 dampers script
- Mac deploy still uploads `spotprice_v0_9_0` using in-memory RPC chunks
- live dampers test fetches or attempts to fetch from `elprisetjustnu.se`
- log evidence shows the correct script behavior, e.g. URL fetch/progress/status
- KVS verification reads the corrected KVS key list
- `hp.price.2h` contains 12 comma-separated values when successful
- `hp.price.area` equals `SE3` when successful
- `hp.price.status` indicates the final outcome
- `spotprice_v0_9_0` is stopped after verification
- no actuator/output/device-setting operations occur

## Non-goals

- No production spotprice scheduling.
- No Home Assistant integration.
- No FTX/heating/damper control.
- No Shelly-side installer.
- No device setting or component changes.
- No external Python packages.
- No broad registry/deploy-plan implementation yet.

## Invariants

- Python standard library only.
- Mac remains the installer/orchestrator path.
- RPC upload chunks remain in the Mac live deploy tool.
- Repo chunks are optional unless a future package reintroduces Shelly-side pull/install.
- P0012 must not use actuator/output/switch/cover/relay RPCs.
- Live log and KVS verification must have timeouts.
- Historical P0011 evidence remains intact as historical evidence.

## Files to inspect

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `requirements/packages/P0011-mac-rpc-chunked-upload-and-spotprice-kvs-test.md`
- `requirements/package-runs/P0011/review.md`
- `requirements/package-runs/P0011/logs/live-dampers-spotprice.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `src/shelly/spotprice/**`
- local or remote G1 source: `devices/dampers-8813bfdaa0c0/scripts/spotprice.js`

## Files allowed to change

- `src/shelly/spotprice/**`
- `build/shelly/spotprice/**`
- `dep/s/**` only for cleanup/regeneration decisions documented in `design.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `docs/functions/**`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/**`
- `requirements/package-runs/P0012/**`
- `requirements/packages/P0012-correct-spotprice-template-and-clean-deploy-artifacts.md`

## Forbidden changes

- no G1 repository changes
- no real FTX runtime source changes outside copied/adapted G2 test source
- no Shelly-side installer implementation
- no device configuration changes
- no actuator/output control code
- no external Python package dependencies
- no broad refactor outside Mac deploy/build tooling and spotprice test source needed for P0012
- do not rewrite or delete P0011 package-run evidence

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0012/review.md
requirements/package-runs/P0012/design.md
requirements/package-runs/P0012/functions.md
```

Use the P0007 phase-gate model.

The design must include sections:

```text
Correct G1 spotprice source
Corrected KVS contract
Repo chunks vs RPC upload chunks cleanup decision
Live dampers verification plan
```

## Live test/debug policy

Live testing allowed: yes, dampers only

Live write actions allowed: yes, but only for:

- creating/updating/starting/stopping `spotprice_v0_9_0`
- `spotprice_v0_9_0` writing its corrected spotprice KVS keys

Shelly log capture required: yes

KVS read verification required: yes

Max implementation/debug attempts: 3

Codex must stop immediately if:

- it cannot safely identify the dampers endpoint
- it cannot read the correct G1 spotprice template
- a required live command exceeds the allowed action list
- the adapted spotprice script contains actuator/output/relay/switch/cover/device-config behavior

## Test cases

### TC1: Correct source template is used
Given the G1 dampers spotprice source
When P0012 updates G2 spotprice source
Then the G2 source uses the elprisetjustnu-based logic and does not use the P0011 Tibber-token/fallback implementation.

### TC2: Correct KVS contract
Given the corrected G2 spotprice source
When tests inspect its KVS keys
Then it writes/verifies `hp.price.2h`, `hp.price.date`, `hp.price.area`, `hp.price.status`, `hp.price.updated`.

### TC3: RPC chunked upload remains active
Given the corrected built script
When Mac deploy uploads it
Then it uses multiple bounded in-memory RPC upload chunks when the script exceeds the configured upload chunk size.

### TC4: Live dampers deploy and log
Given `spotprice_v0_9_0` is built
When the tool deploys it to dampers
Then log evidence shows the corrected script running and attempting/performing elprisetjustnu fetch.

### TC5: Live KVS verification
Given `spotprice_v0_9_0` runs successfully
When the Mac reads corrected spotprice KVS keys
Then the values are present and parseable according to criteria documented in `design.md`.

### TC6: No forbidden operations
Given the P0012 live boundary
When reviewing tool code, package-run evidence and log evidence
Then there are no device setting changes and no actuator/output/relay/cover/switch/component/network/MQTT/Bluetooth/cloud operations.

### TC7: Historical evidence preserved
Given P0011 evidence exists
When P0012 completes
Then P0011 package-run evidence remains in place and P0012 documents the correction as superseding current source, not rewriting history.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
git diff --check
```

For live dampers test, Codex must document the exact command it ran, target endpoint, upload chunk size, upload chunk count, log timeout, KVS keys read, KVS values or safe summaries, and final script status.

## Runtime health checks

During live test, check and record:

- target endpoint used
- upload chunk size and count
- script list/status after deploy
- start/stop result
- bounded log excerpt
- KVS read results for corrected spotprice keys
- absence of forbidden RPC calls in package/tool/log evidence

## Deployment plan

No production deployment. This is a controlled live correction test on dampers only.

## Rollback plan

P0012 may leave `spotprice_v0_9_0` installed and stopped as harmless test evidence, or remove only `spotprice_v0_9_0` if the package-run design chooses cleanup.

Codex must not remove or alter unrelated scripts.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- correct G1 source path
- corrected allowed KVS key list
- repo chunk cleanup/default decision
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
