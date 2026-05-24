# P0016 Function Design

## Shelly Runtime: `src/shelly/supply_uni/supply_uni_pub.js`

### `log`

- Status: new
- Purpose: prefix concise publisher log lines.
- Inputs: message.
- Outputs: none.
- Side effects: writes to Shelly debug log.
- Test coverage: live log verification.

### `num`, `round1`, `clip`, `intClip`, `tempClip`, `abs`

- Status: new
- Purpose: normalize local sensor values to bounded compact telemetry.
- Inputs: raw numeric values and bounds.
- Outputs: normalized numbers.
- Side effects: none.
- Test coverage: source/contract tests via Mac parser equivalent and live readback ranges.

### `comp`, `num4`, `tempValue`

- Status: new, adapted from G1 helper style.
- Purpose: locate status components and extract numeric values across known Shelly field aliases.
- Inputs: local status object and component/field names.
- Outputs: component object or numeric value.
- Side effects: none.
- Test coverage: supply status fixture parser test.

### `parseSupplyStatus`

- Status: new
- Purpose: parse local `Shelly.GetStatus` into the P0016 telemetry snapshot fields.
- Inputs: local status object and timestamp.
- Outputs: snapshot object with `t`, `supply_pa`, `outdoor`, `post_vvx`, `to_outdoor`, `supply_rpm`.
- Side effects: none.
- Test coverage: fixture parser test and live status evidence.

### `changedEnough`

- Status: new
- Purpose: compare current snapshot against last successful snapshot using P0016 thresholds.
- Inputs: current snapshot and previous snapshot.
- Outputs: boolean.
- Side effects: none.
- Test coverage: delta-trigger unit tests through Mac mirror helper and live logs.

### `writeRemoteSnapshot`

- Status: new
- Purpose: write the full snapshot to dampers `tele.supply_uni` with remote JSON-RPC.
- Inputs: snapshot and callback.
- Outputs: callback success boolean.
- Side effects: `HTTP.POST` to dampers `/rpc` for `KVS.Set`.
- Test coverage: live KVS readback.

### `tick`

- Status: new
- Purpose: one publisher cycle with busy guard, local status read, parse, delta check and optional remote publish.
- Inputs: none.
- Outputs: none.
- Side effects: local `Shelly.GetStatus`, optional remote KVS write, logs, updates RAM `lastSent` on success.
- Test coverage: live logs and readback.

### `startPublisher`

- Status: new
- Purpose: start immediate and repeating publisher ticks.
- Inputs: none.
- Outputs: timer id stored in RAM.
- Side effects: starts Shelly timer.
- Test coverage: live script state and logs.

## Shelly Runtime: `src/shelly/supply_uni/supply_uni_refresh.js`

### `log`

- Status: new
- Purpose: prefix refresher logs.
- Inputs: message.
- Outputs: none.
- Side effects: writes to Shelly debug log.
- Test coverage: live log verification.

### `findScriptByName`

- Status: new
- Purpose: find `supply_uni_pub` and self script ids from `Script.List`.
- Inputs: script list and script name.
- Outputs: script object or null.
- Side effects: none.
- Test coverage: live refresher verification.

### `selfStop`

- Status: new
- Purpose: stop `supply_uni_refresh` after completion.
- Inputs: none.
- Outputs: none.
- Side effects: calls `Script.Stop` for own id.
- Test coverage: final script state.

### `runRefresh`

- Status: new
- Purpose: stop/restart only `supply_uni_pub`, then self-stop.
- Inputs: none.
- Outputs: none.
- Side effects: `Script.Stop`/`Script.Start` for `supply_uni_pub`, logs, self-stop.
- Test coverage: live log and script-state verification.

## Mac Live Tool: `src.mac.tools.shelly_live.core`

### `verify_supply_snapshot`

- Status: new
- Purpose: validate `tele.supply_uni` shape, exact field set and numeric ranges.
- Inputs: KVS value.
- Outputs: normalized summary.
- Side effects: none.
- Test coverage: unit tests.

### `supply_snapshot_changed`

- Status: new
- Purpose: mirror the publisher delta thresholds in Mac tests/review.
- Inputs: current and previous supply snapshots.
- Outputs: boolean.
- Side effects: none.
- Test coverage: unit tests for below-threshold and threshold-crossing changes.

### `read_supply_uni_kvs`, `wait_for_supply_uni_kvs`

- Status: new
- Purpose: bounded read/poll of `tele.supply_uni` on dampers.
- Inputs: dampers base URL, timeouts and opener.
- Outputs: raw KVS value and validated summary.
- Side effects: read-only `KVS.Get`.
- Test coverage: fake RPC tests.

### `verify_supply_status_shape`

- Status: new
- Purpose: validate that live supply UNI status exposes the required components before deploy.
- Inputs: local status object.
- Outputs: parsed summary.
- Side effects: none.
- Test coverage: fixture unit tests.

### `deploy_supply_uni`

- Status: new
- Purpose: deploy/update/start P0016 publisher and refresher, verify logs and dampers KVS readback.
- Inputs: supply base URL, dampers base URL, built script paths, expected log text and timeouts.
- Outputs: evidence object.
- Side effects: allowed script create/update/start/stop on supply UNI, debug-log reads, dampers KVS readback.
- Test coverage: fake RPC/log orchestration test and live verification.

### `main`

- Status: changed
- Purpose: add CLI command for P0016 live verification.
- Inputs: argv.
- Outputs: process exit code and evidence text.
- Side effects: runs live P0016 verification when invoked.
- Test coverage: lower-level unit tests.

## Cross-Package Catalog Updates

- Update `docs/functions/mac/shelly-live-deploy-tool.md` because the live write allowlist and KVS read boundary change.
- Add `docs/functions/shelly/supply-uni-publisher.md` for the new durable publisher/refresher runtime behavior.
