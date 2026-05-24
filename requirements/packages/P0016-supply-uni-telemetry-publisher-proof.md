# Package P0016: Supply UNI telemetry publisher proof

## Status
planned

## Package order
P0016

## Primary area
Shelly runtime / telemetry publishing / poll replacement

## Decision summary

P0016 creates the first local telemetry publisher proof for the future replacement of the G1 central `poll` model.

The first target is:

```text
ftx-supply-uni / 192.168.77.20
```

P0016 builds two Shelly scripts for the supply UNI device:

```text
supply_uni_pub
supply_uni_refresh
```

`Supply_uni_pub` is a long-lived local telemetry publisher. It reads local values from its own Shelly status every 15 seconds, compares them to the last successfully sent snapshot held in RAM, and writes a complete compact snapshot to the planner/development device when any configured value changes enough.

`Supply_uni_refresh` is a one-shot mini-master/refresher. It restarts `supply_uni_pub` once per hour so the publisher sends a fresh full snapshot even if no value crossed a delta threshold.

P0016 is a proof of the future distributed telemetry model:

```text
G1 central poll:
  one runtime host fetches all values from all devices

Future model:
  each measurement-owning device reads itself and publishes its own compact snapshot when useful
```

P0016 must not build a new central poller.

## Naming rule

Runtime names, script names and KVS keys must not use `g2` as a prefix or namespace.

`G2` may be used in package discussion to distinguish the new architecture from G1, but durable runtime contracts should survive G1 retirement without broad renaming.

Allowed examples:

```text
supply_uni_pub
supply_uni_refresh
tele.supply_uni
```

Forbidden examples:

```text
g2.supply_uni_pub
g2.tele.supply_uni
g2.replan.request
```

## Current behavior

G1 currently has a central `poll` script on the current G1 runtime host. It reads multiple devices over the network, parses values, derives telemetry and writes central KVS.

G1 supply parsing is the implementation reference for component IDs and interpretation:

```text
marlov1974/shelly/rt/poll/feature-supply.js
```

Relevant G1 supply UNI values:

```text
SUPPLY_DP_ID = 100
SUPPLY_RPM_ID = 2
TEMP_POST_VVX_ID = 100
TEMP_OUTDOOR_ID = 101
TEMP_TO_OUTDOOR_ID = 102
```

G1 supply UNI parsed roles:

```text
pa
temp_post_vvx
temp_outdoor
temp_to_outdoor
rpm
```

G1 master is the scheduling inspiration. It uses a 15 second tick cadence, but P0016 must not recreate the full G1 master/score dispatcher.

## G1 inspiration sources

Codex must inspect these G1 files read-only:

```text
marlov1974/shelly/rt/recipes/p.json
marlov1974/shelly/rt/poll/base.js
marlov1974/shelly/rt/poll/numbers.js
marlov1974/shelly/rt/poll/feature-supply.js
marlov1974/shelly/rt/poll/output.js
marlov1974/shelly/rt/poll/main.js
marlov1974/shelly/rt/master/base.js
marlov1974/shelly/rt/master/run.js
marlov1974/shelly/rt/master/main.js
```

Codex must document which parts are copied, adapted or intentionally not copied in `requirements/package-runs/P0016/design.md`.

## Target live devices

Source/publisher device:

```text
logical/infrastructure role: ftx-supply-uni
stable LAN address: 192.168.77.20
operator NAT URL: http://192.168.86.240:8020/
physical Shelly id: unknown until verified
```

Planner/development receiver device:

```text
logical/infrastructure role: ftx-dampers
stable LAN address: 192.168.77.30
operator NAT URL: http://192.168.86.240:8030/
physical Shelly id: 8813bfd99f54
```

Dampers is used as the current development/planner receiver because it is the established low-risk development device.

Codex must verify the live identity/status of both endpoints before live writes. If supply UNI physical Shelly id is not yet documented, Codex must record the verified id in package evidence and update the device registry/memory if the finding is reliable.

## Telemetry KVS contract

Remote KVS key on dampers/planner receiver:

```text
tele.supply_uni
```

Value shape:

```json
{
  "t": 1234567890,
  "supply_pa": 0,
  "outdoor": 0,
  "post_vvx": 0,
  "to_outdoor": 0,
  "supply_rpm": 0
}
```

Rules:

- KVS key identifies the source/signal group; value must not include source/device name.
- No schema version field for P0016.
- No sequence field for P0016.
- `t` is timestamp and is included for troubleshooting and future freshness/stale logic.
- Values should remain human-readable.
- Do not add units, labels or nested status objects to the KVS value.
- Keep the serialized JSON compact enough for Shelly KVS constraints.

Suggested units/format:

```text
supply_pa    Pa, integer or small number
outdoor      Celsius, one decimal if available
post_vvx     Celsius, one decimal if available
to_outdoor   Celsius, one decimal if available
supply_rpm   RPM, integer
```

## Delta-trigger policy

`supply_uni_pub` compares current local values to the last successfully sent snapshot held in RAM.

If any value crosses its publish threshold, the script publishes the complete current snapshot, not just the changed value.

Initial thresholds:

```text
supply_pa    10 Pa
outdoor      1.0 C
post_vvx     1.0 C
to_outdoor   1.0 C
supply_rpm   100 RPM
```

Comparison is against the last successfully reported snapshot, not the last measured value.

If remote write fails, do not update `last_sent`; retry can happen on a later tick.

## Publisher runtime model

`supply_uni_pub`:

```text
on start:
  read local status
  publish full snapshot to tele.supply_uni
  store last_sent in RAM
  start repeating 15 second tick

each tick:
  if previous tick still running, skip this tick
  read local status
  parse supply UNI values
  compare to last_sent
  if any delta threshold crossed:
    write full snapshot to dampers KVS tele.supply_uni
    on success update last_sent in RAM
  if no threshold crossed:
    do nothing
```

Expected time budget:

```text
local Shelly.GetStatus / local component reads: < 1s normally
parse and compare: fast
remote KVS.Set to dampers: < 1-3s normally
expected whole tick: < 5s
tick interval: 15s
```

Hard guard:

```text
No overlapping ticks. If a tick is still running, the next tick logs a short skip and exits.
```

## Refresher runtime model

`supply_uni_refresh`:

```text
one-shot script
stop supply_uni_pub
wait briefly
start supply_uni_pub
self-stop
```

This is the mini-master part of P0016.

The package must document how hourly restart is achieved or left as manual/future scheduling if Shelly-side hourly scheduling is not implemented in P0016.

Desired steady-state behavior:

```text
supply_uni_pub running long-lived
supply_uni_refresh can be started hourly to force a fresh snapshot
```

If `supply_uni_refresh` runs and restarts `supply_uni_pub`, the restarted publisher must send a full snapshot on start even if no value changed.

## Local value reading

Preferred first implementation:

```text
Shelly.GetStatus on the local supply UNI device
```

The script should parse relevant components from that local status object.

If `Shelly.GetStatus` does not expose the needed values or is too large/unsuitable, Codex may use component-specific local RPC calls, but must document the reason and component IDs.

Expected component IDs from G1 reference:

```text
voltmeter:100        supply differential pressure / Pa source
input:2              supply fan RPM/frequency source
temperature:100      post_vvx
temperature:101      outdoor
temperature:102      to_outdoor
```

Codex must verify live status shape before relying on these IDs.

## Remote write model

Publisher writes to dampers using Shelly RPC-over-HTTP or another verified Shelly RPC mechanism:

```text
KVS.Set key=tele.supply_uni value=<snapshot>
```

The exact RPC/HTTP call must be discovered and documented in design/evidence.

Remote write target is dampers only for P0016.

## Allowed live actions

On `ftx-supply-uni` only, P0016 may:

- read device info/status/config
- create/update/start/stop only `supply_uni_pub`
- create/update/start/stop only `supply_uni_refresh`
- read debug log with timeout
- call local read-only status/component RPCs
- allow `supply_uni_pub` to read local values and write remote KVS to dampers
- allow `supply_uni_refresh` to stop/start only `supply_uni_pub`

On `ftx-dampers` only, P0016 may:

- read device info/status
- allow remote `KVS.Set` for key `tele.supply_uni`
- read back `tele.supply_uni`

## Forbidden live actions

P0016 must not:

- change actuator/output/switch/relay/cover state
- change device settings/config except script create/update/start/stop for the two allowed scripts
- write any KVS key other than `tele.supply_uni` on dampers
- write any KVS on `ftx-vvx`
- deploy anything to the current G1 runtime host
- touch `ftx.weather.act` or any G1 production KVS contract
- implement planner logic
- implement system-status/diagnostic brain logic
- implement Home Assistant integration
- implement production activation
- change G1 repository files

## Non-goals

- No full poll replacement.
- No planner brain implementation.
- No system-status brain implementation.
- No cross-device telemetry fanout beyond dampers receiver.
- No Pro Sensor Add-on support yet.
- No Home Assistant visualization.
- No rollback/version switch implementation.
- No production scheduling.

## Invariants

- Python standard library only for Mac tooling.
- Runtime names/KVS keys must not use `g2`.
- Source/build/deploy separation must be preserved.
- Mac direct deploy reads complete built scripts from `build/shelly/**` and uses in-memory RPC upload chunks.
- No actuator/output changes.
- Package-run evidence required.
- Knowhow promotion must be considered in final report.
- Pre-production commit/push policy applies after successful verification.

## Files to inspect

G2:

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/01-system-overview.md`
- `memory/02-design-principles.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/identity-and-registry.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/infrastructure/devices.md`
- `memory/physical/ftx/sensors.md`
- `memory/knowhow/shelly.md`
- `src/mac/tools/shelly_build/**`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/**`
- `src/shelly/weather/**` as recent one-shot/runtime reference
- `src/shelly/spotprice/**` as recent HTTP/runtime reference

G1:

- `marlov1974/shelly/rt/recipes/p.json`
- `marlov1974/shelly/rt/poll/base.js`
- `marlov1974/shelly/rt/poll/numbers.js`
- `marlov1974/shelly/rt/poll/feature-supply.js`
- `marlov1974/shelly/rt/poll/output.js`
- `marlov1974/shelly/rt/poll/main.js`
- `marlov1974/shelly/rt/master/base.js`
- `marlov1974/shelly/rt/master/run.js`
- `marlov1974/shelly/rt/master/main.js`

## Files allowed to change

- `src/shelly/supply_uni/**`
- `build/shelly/supply_uni/**`
- `dep/s/**` only for generated supply UNI artifacts
- `src/mac/tools/**` only for deploy/readback support needed by P0016
- `tests/mac/tools/**`
- `docs/functions/**`
- `memory/infrastructure/devices.md` if supply UNI physical Shelly id is reliably verified
- `memory/physical/ftx/sensors.md` only if live evidence corrects supply UNI measurement mapping
- `memory/knowhow/**` if new reusable Shelly runtime lessons are learned
- `requirements/package-runs/P0016/**`
- `requirements/packages/P0016-supply-uni-telemetry-publisher-proof.md`

## Forbidden changes

- no G1 repository changes
- no Home Assistant changes
- no planner/system-status brain implementation
- no actuator/output control code
- no production activation
- no external Python package dependencies
- no broad refactor outside supply UNI publisher/live deploy support needed for P0016
- do not rewrite previous package-run evidence

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0016/review.md
requirements/package-runs/P0016/design.md
requirements/package-runs/P0016/functions.md
```

The design must include sections:

```text
G1 poll/master inspiration analysis
Supply UNI live status/component discovery
Telemetry KVS contract
Delta-trigger policy
Publisher runtime model
Refresher runtime model
Remote KVS write model
Live verification plan
No-central-poll boundary
No-G2-runtime-name boundary
```

## Live test/debug policy

Live testing allowed: yes, supply UNI and dampers only.

Live write actions allowed:

On supply UNI:

- create/update/start/stop `supply_uni_pub`
- create/update/start/stop `supply_uni_refresh`

On dampers:

- `supply_uni_pub` writing only `tele.supply_uni`
- readback of `tele.supply_uni`

Shelly log capture required: yes.

KVS read verification required: yes.

Max implementation/debug attempts: 3.

Codex must stop immediately if:

- it cannot safely identify supply UNI or dampers
- supply UNI local status does not expose the required values and component-specific read fallback is unclear
- remote KVS.Set to dampers cannot be verified safely
- any required live command exceeds the allowed action list
- adapted scripts contain actuator/output/relay/switch/cover/device-config behavior

## Test cases

### TC1: G1 inspiration documented
Given G1 poll/master source
When Codex writes `design.md`
Then it documents the G1 parts used as inspiration and what is intentionally not copied.

### TC2: Supply UNI status parsing
Given a fixture local Shelly status shape matching supply UNI
When parser tests run
Then it extracts `supply_pa`, `outdoor`, `post_vvx`, `to_outdoor`, and `supply_rpm`.

### TC3: Snapshot size and shape
Given current supply UNI values
When a snapshot is serialized
Then it contains only `t`, `supply_pa`, `outdoor`, `post_vvx`, `to_outdoor`, `supply_rpm` and remains compact.

### TC4: Delta trigger
Given `last_sent` and current values
When one signal crosses its threshold
Then publisher sends the complete snapshot.

Given values that do not cross thresholds
Then publisher does not send.

### TC5: Failed remote write does not update last_sent
Given a remote KVS.Set failure
When publisher tick completes
Then `last_sent` remains unchanged so a later tick may retry.

### TC6: Busy guard
Given a tick is already running
When another timer tick fires
Then publisher skips the overlapping tick and logs a short busy marker.

### TC7: Refresher restart
Given `supply_uni_pub` exists
When `supply_uni_refresh` runs
Then it stops and starts only `supply_uni_pub` and self-stops.

### TC8: Live supply UNI publish to dampers
Given `supply_uni_pub` is deployed on supply UNI
When it starts
Then it writes `tele.supply_uni` on dampers and readback matches expected shape.

### TC9: No forbidden operations
Given package code and evidence
When reviewed
Then no actuator/output/device-config/Home Assistant/G1 production operations occurred.

## Verification commands

Codex must define final commands in design, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/supply_uni/manifest.json --build-root build/shelly/supply_uni --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/supply_uni --dep-root dep/s --role supply_uni_pub
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/supply_uni --dep-root dep/s --role supply_uni_refresh
git diff --check
```

Live evidence must document:

- supply UNI endpoint and identity/status evidence
- dampers endpoint and physical id verification
- local status/component shape used for parsing
- scripts created/updated on supply UNI
- upload chunk size/count for each script
- log evidence for publisher start/tick/publish
- log evidence for refresher stop/start/self-stop if tested live
- final script states
- `tele.supply_uni` readback on dampers
- absence of actuator/output operations

## Expected final live state

If successful:

```text
supply_uni_pub installed and running or intentionally stopped according to design
supply_uni_refresh installed and stopped
tele.supply_uni present on dampers with latest supply UNI snapshot
no actuator/output state changed
```

Codex must document whether `supply_uni_pub` is intentionally left running after P0016 or stopped as a proof artifact.

## Rollback plan

If verification fails after allowed attempts, follow failed-package cleanup:

- preserve package-run evidence
- update package status to stopped/failed-live if appropriate
- revert unverified current-state implementation changes unless evidence-only commit is intended
- leave or remove only `supply_uni_pub` and `supply_uni_refresh` according to design/evidence
- do not touch unrelated scripts or KVS

If an incorrect KVS key was written, Codex may only remove it if the package design explicitly allowed that cleanup and the key is unambiguously owned by P0016.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- G1 poll/master inspiration summary
- supply UNI live identity/status summary
- dampers identity verification
- telemetry KVS contract
- local status/component mapping used
- delta thresholds
- files changed
- tests run
- live commands and target endpoints
- upload chunk size/count
- log evidence path
- KVS readback summary
- final live state
- knowhow promotion created/updated/skipped
- commit SHA after push, if successful
- uncertainty
- diff summary

## Completion notes

Filled after implementation.
