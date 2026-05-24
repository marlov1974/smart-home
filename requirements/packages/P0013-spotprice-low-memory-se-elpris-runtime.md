# Package P0013: Spotprice low-memory se.elpris runtime

## Status
completed

## Package order
P0013

## Primary area
G2 / Shelly runtime / Mac deploy tooling / spotprice low-memory autonomous runtime

## Decision summary

P0012 correctly attempted to switch `spotprice_v0_9_0` toward the intended G1 dampers spotprice template, but live verification failed on dampers because the elprisetjustnu JSON response caused Shelly memory pressure / `out_of_memory` before the script could complete KVS writes.

The architectural goal remains:

```text
Shelly must be able to live without Mac or Home Assistant at runtime.
```

Mac remains the installer/deployer/orchestrator for deployment and verification, but the deployed Shelly spotprice script must be autonomous after deployment.

P0013 creates a low-memory Shelly spotprice runtime using:

```text
https://se.elpris.eu
```

Prefer the compact hourly endpoint variant:

```text
https://se.elpris.eu/api/v1/prices/YYYY/MM-DD_SE3.json?avg24
```

This should reduce Shelly heap pressure by parsing a compact `p` price array instead of the larger elprisetjustnu object list.

## Context from previous packages

P0011 proved:

- Mac-side deploy works
- RPC upload chunking works
- large script upload can be split into in-memory RPC chunks
- live log capture works
- KVS verification works

P0012 proved:

- repo sync process now works
- correct old G1 dampers template was identified
- direct elprisetjustnu JSON parsing is too memory-heavy or otherwise unsafe for dampers in the attempted form
- failed-package cleanup/evidence process is required

P0013 must build forward from that evidence rather than continuing the failed P0012 implementation in place.

## Target script

Script name:

```text
spotprice_v0_9_0
```

Runtime source should live under:

```text
src/shelly/spotprice/
```

The script must be deployable by the existing Mac live deploy tool using in-memory RPC upload chunks.

## Runtime autonomy requirement

After deploy, `spotprice_v0_9_0` must be able to run on Shelly without Mac or Home Assistant.

Mac may be used only for:

- building
- uploading/deploying
- starting/stopping during controlled live test
- reading logs
- reading KVS for verification

Mac must not be required for normal runtime spotprice fetch once the script is installed.

## Source/API model

Use `se.elpris.eu` as the low-memory spotprice source.

Preferred URL format:

```text
https://se.elpris.eu/api/v1/prices/YYYY/MM-DD_SE3.json?avg24
```

Rationale:

- compact payload suitable for small devices
- `avg24` gives 24 hourly values
- 24 hourly values can be reduced to 12 two-hour values by averaging pairs
- easier parsing: find the compact `p` array and parse numeric values

If Codex finds that `avg24` is unavailable or unsuitable, it may use the compact 96-value endpoint, but it must document why and still keep memory use low.

## Date selection policy

Spot prices for tomorrow are not reliably available until after early afternoon.

P0013 must avoid failing simply because tomorrow is not published yet.

Design a deterministic date policy, for example:

```text
if local hour >= 14:
  try tomorrow
else:
  fetch today
```

The exact policy must be documented in `requirements/package-runs/P0013/design.md`.

P0013 may include a fallback from tomorrow to today only if it can be implemented without causing unsafe memory pressure. If fallback requires two large HTTP responses in memory, do not implement fallback; choose a time-based single request instead.

## KVS contract

P0013 must write and verify:

```text
hp.price.2h
hp.price.date
hp.price.area
hp.price.status
hp.price.updated
```

Expected meanings:

```text
hp.price.2h      12 comma-separated two-hour total price values
hp.price.date    date the prices apply to, YYYY-MM-DD
hp.price.area    SE3
hp.price.status  ok on success, otherwise a concise error status
hp.price.updated local timestamp when script updated KVS
```

Do not reintroduce the P0011 Tibber/fallback keys as current contract:

```text
hp.price.source
hp.price.debug
hp.price.debug.len
```

Those keys may remain in historical P0011 evidence only.

## Price calculation model

Keep the dampers spotprice calculation model from the correct G1 template unless Codex documents a package-scoped reason to change it:

- price area `SE3`
- VAT handling
- retailer markup / variable cost
- energy tax
- grid model: flat or time tariff
- high-load months/weekdays/hours
- 12 two-hour final values

The script must be low-memory and Shelly-friendly even if this requires simpler code style than normal desktop JavaScript.

## Memory strategy

P0013 should explicitly design for low heap pressure:

- compact source payload
- avoid `JSON.parse` if manual parser is safer
- avoid retaining large response body longer than necessary
- avoid building large intermediate arrays if possible
- parse only the `p` array values needed
- use short helper functions and bounded strings
- write only final compact KVS values

If the implementation uses `JSON.parse`, the design must justify that the compact payload is small enough and live verification must confirm no memory failure.

## Chunking policy

Do not remove Mac RPC upload chunking.

P0013 continues the distinction:

```text
RPC upload chunks:
  required transport mechanism for Mac direct deploy of large scripts.
  Created in Mac memory by shelly_live.

Repo deploy chunks:
  optional artifacts for future Shelly-side pull/install models.
  Not required for normal Mac-as-installer deploy.
```

P0013 should not make `dep/s/ch/**` mandatory for Mac direct deploy. If build still generates repo chunks because the current build tool does so, Codex may leave them as generated artifacts but must not treat them as the runtime deployment source for the live test.

## Dampers live-test boundary

Allowed live actions:

- read device status
- read script list/status
- create/update/start/stop only `spotprice_v0_9_0`
- upload `spotprice_v0_9_0` using bounded RPC upload chunks
- read or stream debug log
- read only the documented spotprice KVS keys
- `spotprice_v0_9_0` may perform its own HTTP request to `se.elpris.eu`
- `spotprice_v0_9_0` may write only the documented spotprice KVS keys

Forbidden live actions:

- no device setting changes
- no Wi-Fi/network/MQTT/Bluetooth/cloud changes
- no component/config changes
- no actuator/output/switch/cover/relay RPC calls
- no real damper control code
- no script names other than `spotprice_v0_9_0`
- no Shelly-side installer implementation
- no Mac-side KVS writes except optional explicit cleanup of documented spotprice keys if design requires it

## Non-goals

- No production scheduling yet.
- No Home Assistant integration.
- No FTX/heating/damper control.
- No Shelly-side installer.
- No device setting or component changes.
- No external Python packages.
- No broad multi-device registry yet.

## Invariants

- Python standard library only for Mac tools.
- Shelly runtime must remain autonomous after deployment.
- Mac remains installer/deployer, not runtime dependency.
- RPC upload chunks must remain supported.
- Live log and KVS verification must have timeouts.
- P0013 must not use actuator/output/switch/cover/relay RPCs.
- Historical P0011/P0012 evidence must remain intact.

## Files to inspect

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `requirements/packages/P0011-mac-rpc-chunked-upload-and-spotprice-kvs-test.md`
- `requirements/package-runs/P0011/logs/live-dampers-spotprice.md`
- `requirements/packages/P0012-correct-spotprice-template-and-clean-deploy-artifacts.md`
- `requirements/package-runs/P0012/**` if present locally after cleanup
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `src/shelly/spotprice/**`
- correct G1 reference source: `marlov1974/shelly/devices/dampers-8813bfdaa0c0/scripts/spotprice.js`
- `https://se.elpris.eu` documentation or endpoint behavior, if network access is available

## Files allowed to change

- `src/shelly/spotprice/**`
- `build/shelly/spotprice/**`
- `dep/s/**` only for generated artifact cleanup/regeneration decisions documented in `design.md`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/shelly_live/**`
- `docs/functions/**`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/knowhow/**`
- `requirements/package-runs/P0013/**`
- `requirements/packages/P0013-spotprice-low-memory-se-elpris-runtime.md`

## Forbidden changes

- no G1 repository changes
- no real FTX runtime source changes outside copied/adapted G2 spotprice test source
- no Shelly-side installer implementation
- no device configuration changes
- no actuator/output control code
- no external Python package dependencies
- no broad refactor outside Mac deploy/build tooling and spotprice test source needed for P0013
- do not rewrite or delete P0011/P0012 package-run evidence

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0013/review.md
requirements/package-runs/P0013/design.md
requirements/package-runs/P0013/functions.md
```

Use the P0007 phase-gate model.

The design must include sections:

```text
Low-memory se.elpris source model
Date selection policy
Corrected KVS contract
Memory strategy
Repo chunks vs RPC upload chunks
Live dampers verification plan
Failed-package cleanup if verification fails
```

## Live test/debug policy

Live testing allowed: yes, dampers only

Live write actions allowed: yes, but only for:

- creating/updating/starting/stopping `spotprice_v0_9_0`
- `spotprice_v0_9_0` writing its documented spotprice KVS keys

Shelly log capture required: yes

KVS read verification required: yes

Max implementation/debug attempts: 3

If verification fails after 3 attempts, Codex must run failed-package cleanup as defined in `memory/05-package-lifecycle.md`:

- keep package-run evidence
- update package status to a failed/stopped state if appropriate
- revert unverified current-state implementation changes unless explicitly safe/useful
- commit/push evidence-only failure record when safe
- leave the working tree clean or report why cleanup is blocked

Codex must stop immediately if:

- it cannot safely identify the dampers endpoint
- it cannot use or validate the se.elpris source model
- a required live command exceeds the allowed action list
- the adapted spotprice script contains actuator/output/relay/switch/cover/device-config behavior

## Test cases

### TC1: se.elpris source is used
Given the P0013 spotprice source
When tests inspect or run build fixtures
Then the source uses `se.elpris.eu` and does not use Tibber or the large direct elprisetjustnu object-list parser as the primary runtime source.

### TC2: Date selection avoids unavailable tomorrow before publish window
Given current local time before the selected tomorrow-publish threshold
When the script builds its URL
Then it targets today, not tomorrow.

Given current local time after the threshold
When the script builds its URL
Then it may target tomorrow according to documented policy.

### TC3: Correct KVS contract
Given the P0013 spotprice source
When tests inspect its KVS keys
Then it writes/verifies `hp.price.2h`, `hp.price.date`, `hp.price.area`, `hp.price.status`, `hp.price.updated` and does not require P0011 debug/source keys.

### TC4: Low-memory parser
Given a compact se.elpris response body with 24 hourly values
When parser logic processes it
Then it produces 12 two-hour values without JSON.parse unless design justifies JSON.parse.

### TC5: RPC chunked upload remains active
Given the built script
When Mac deploy uploads it
Then it uses bounded in-memory RPC upload chunks and records chunk size/count.

### TC6: Live dampers deploy/log/KVS
Given `spotprice_v0_9_0` is built
When the tool deploys and starts it on dampers
Then log evidence shows the se.elpris fetch path and KVS verification passes for the corrected keys.

### TC7: No forbidden operations
Given the P0013 live boundary
When reviewing tool code, package-run evidence and log evidence
Then there are no device setting changes and no actuator/output/relay/cover/switch/component/network/MQTT/Bluetooth/cloud operations.

### TC8: Failed cleanup if needed
Given live verification fails after 3 attempts
When Codex stops
Then it preserves evidence, reverts unverified current-state implementation changes, commits evidence-only failure if useful and leaves the working tree clean.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/spotprice/manifest.json --build-root build/shelly/spotprice --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/spotprice --dep-root dep/s --role spotprice_v0_9_0
git diff --check
```

For live dampers test, Codex must document the exact command it ran, target endpoint, upload chunk size, upload chunk count, log timeout, KVS keys read, KVS values or safe summaries, final script status and whether memory pressure occurred.

## Runtime health checks

During live test, check and record:

- target endpoint used
- selected URL/date policy
- upload chunk size and count
- script list/status after deploy
- start/stop result
- bounded log excerpt
- KVS read results for corrected spotprice keys
- memory-related log lines if present
- absence of forbidden RPC calls in package/tool/log evidence

## Deployment plan

No production deployment. This is a controlled live runtime test on dampers only.

## Rollback plan

P0013 may leave `spotprice_v0_9_0` installed and stopped as harmless test evidence, or remove only `spotprice_v0_9_0` if the package-run design chooses cleanup.

Codex must not remove or alter unrelated scripts.

If the package fails verification, follow the failed-package cleanup process and do not leave unverified current-state source/artifacts committed as the runtime truth.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- se.elpris URL model
- date selection policy
- corrected allowed KVS key list
- memory strategy
- repo chunk vs RPC upload chunk decision
- files changed
- tests run
- live test command and target endpoint
- upload chunk size and count
- log evidence path
- KVS evidence path or section
- verification results
- commit SHA after push, or evidence-only stopped commit SHA if failed
- uncertainty
- diff summary

## Completion notes

Implemented and live-verified on dampers.

- Source: `se.elpris.eu` compact `avg24` endpoint.
- Date policy: today before 14:00 local, tomorrow at or after 14:00 local.
- KVS contract: `hp.price.2h`, `hp.price.date`, `hp.price.area`, `hp.price.status`, `hp.price.updated`.
- Live attempt: passed on first try with 4 RPC upload chunks of 1500 bytes.
- Final live state: `spotprice_v0_9_0` installed and stopped on dampers with `status=ok`.
- No `out_of_memory` observed in bounded live evidence.
