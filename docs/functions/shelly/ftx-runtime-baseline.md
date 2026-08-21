# Shelly FTX Runtime Baseline Function Catalog

## Scope

P0057 imported the G1 FTX Shelly runtime into G2 under:

```text
src/shelly/ftx/
```

This catalog records durable high-level entry points, current local-device behavior and safety-relevant functions for future G2 packages.

## Source Baseline

```text
source repo: marlov1974/shelly
source commit: 761cc4bc1c527d6bdffa0a0783f0cfd1761040f4
package: P0057
```

Later G2 packages changed selected behavior after the import. Current source in `src/shelly/ftx/` is stronger truth than the original P0057 import description.

## Current Local Device Topology

Current source contains runtime roles for:

```text
supply-fan
extract-fan
heat-dimmer
cool-dimmer
dampers
vvx
```

The former standalone supply/extract/process UNI devices are not part of the current runtime-role structure. Current supply/extract Pro devices read their Sensor Add-On components locally and publish selected telemetry to peer devices.

## Brain Runtime

### calculateBrain()

Status: imported baseline

Source:
- `src/shelly/ftx/brain/main.js`

Purpose:
- Runs one FTX decision cycle by calculating target, ventilation, failsafe, thermal and VVX signals, then building final per-device intent.

Side effects:
- None directly; output is written later by `writeTargetToHouse()` and `writeIntent()`.

Last changed:
- Imported by P0057 from G1.

### calcTarget()

Status: active

Source:
- `src/shelly/ftx/brain/feature-target.js`

Purpose:
- Calculates house target, house dewpoint, minimum supply temperature and initial target-to-house signals.

Contract:
- `dewpoint_house_c` is calculated from house temperature and RH.
- `min_supply_temp_c` uses calculated dewpoint directly against the absolute `TARGET_TO_HOUSE_MIN_C` floor.
- P0059 removed the previous extra dewpoint safety margin.
- P0060 lowered `TARGET_TO_HOUSE_MIN_C` from `14.0 C` to `12.0 C`.

Last changed:
- P0060 lowered the absolute minimum supply floor to `12.0 C`.

### calcVvx()

Status: imported baseline

Source:
- `src/shelly/ftx/brain/feature-vvx.js`

Purpose:
- Sets VVX permission signal from FTX enable state.

Contract:
- Brain-level VVX signal is permission, not final switch state.
- Local VVX executor makes the final thermal on/off decision.

Last changed:
- Imported by P0057 from G1.

### buildDeviceIntent()

Status: imported baseline

Source:
- `src/shelly/ftx/brain/output.js`

Purpose:
- Builds a full per-device intent object with source, timestamp, mode, inhibit flag and actuator target.

VVX-specific contract:
- Adds `target_to_house_c`.
- Adds temperature snapshot `{out_c, house_c}` used by the local VVX executor.

Last changed:
- Imported by P0057 from G1.

## L2 Fan Executors

### supply/extract executor apply flow

Status: current baseline

Sources:
- `src/shelly/ftx/scripts/supply-fan/executor_supply_fan_v0_1_0.js`
- `src/shelly/ftx/scripts/extract-fan/executor_extract_fan_v0_1_0.js`

Purpose:
- Apply the latest valid fan intent to local `light:0` output.

Contract:
- Intent is read from local KVS.
- Requested output is clipped to `0..100%`.
- Executor is idempotent when local output already matches requested state.
- Intent older than `300 s` is rejected and no new output command is applied.
- Rejecting stale intent does not itself reset the current physical output; the device remains at the already-applied local light state unless another local mechanism changes it.

Architectural note:
- This means current fan L2 behavior naturally holds the last applied physical output if L3 disappears, although the executor does not treat an indefinitely old intent as valid for reapplication after reboot or other local state loss.

## L2 Heat/Cool Executors

### targetPct()

Status: current baseline

Sources:
- `src/shelly/ftx/scripts/heat-dimmer/executor_heat_dimmer_v0_1_0.js`
- `src/shelly/ftx/scripts/cool-dimmer/executor_cool_dimmer_v0_1_0.js`

Purpose:
- Convert the current local thermal target and locally cached process telemetry into an incremental `light:0` percentage adjustment.

Heat contract:
- Reads `ftx.tel.thermal.heat` from local KVS.
- Uses `target_to_house_c` and measured `to_house`.
- Moves local output by `8%` per execution outside a `0.2 C` hold band.

Cool contract:
- Reads `ftx.tel.thermal.cool` from local KVS.
- Uses `target_to_house_c` and measured `to_house`.
- Moves local output by `5%` per execution outside a `0.2 C` hold band.

Fallback:
- If target or `to_house` is unavailable, executor falls back to intent `act.pct` when present, otherwise current local brightness.

Current autonomy limitation:
- Both heat and cool reject intent older than `300 s`.
- When intent becomes stale, the executor skips without changing the already-applied output.
- Therefore current code preserves the last physical percentage when L3 disappears, but it does **not** continue actively regulating indefinitely against the last temperature target.
- A future L2-architecture package should decide whether the durable setpoint itself should remain valid until explicitly replaced, while peer telemetry freshness is handled separately.

## Local Peer Telemetry

### telemetry_publisher_supply_fan_v0_1_0.js

Status: current baseline

Source:
- `src/shelly/ftx/scripts/supply-fan/telemetry_publisher_supply_fan_v0_1_0.js`

Purpose:
- Read supply-side actuator/sensor components locally and distribute current telemetry to consumers.

Local measurements include:

```text
input:100        pressure signal
light:0          local fan actuator state
temperature:100  to_house
temperature:101  post_vvx
temperature:102  out
temperature:103  brine
temperature:104  brine_post_shunt
temperature:105  hotwater
temperature:106  hotwater_post_shunt
```

Direct peer publication:

```text
ftx.tel.dev.sup      -> 192.168.77.30 / dampers coordination host
ftx.tel.thermal.cool -> 192.168.77.13 / cool-dimmer
ftx.tel.thermal.heat -> 192.168.77.12 / heat-dimmer
```

Transport:
- direct HTTP/RPC `KVS.Set`
- no MQTT broker required
- no L3 process required for the peer telemetry path

### telemetry_publisher_extract_fan_v0_1_0.js

Status: current baseline

Source:
- `src/shelly/ftx/scripts/extract-fan/telemetry_publisher_extract_fan_v0_1_0.js`

Purpose:
- Read extract/house-side actuator/sensor components locally and publish aggregate telemetry.

Local measurements include:

```text
input:100        pressure signal
input:101        house ppm-like air-quality signal
light:0          local fan actuator state
temperature:100  to_outdoor
temperature:105  house
humidity:105     house RH
```

Direct publication:

```text
ftx.tel.dev.ext -> 192.168.77.30 / dampers coordination host
```

## VVX Device Runtime

### decideOn()

Status: imported baseline

Source:
- `src/shelly/ftx/scripts/vvx/executor_vvx_v0_1_0.js`

Purpose:
- Decides local VVX switch target from fresh intent, target temperature, outdoor temperature and house temperature.

Contract:
- Deny/off if `act.on` is false.
- Deny/off if target or temperature snapshot is missing.
- For cooling need, VVX turns on only if outdoor air is warmer than house air by the help margin.
- For heating need, VVX turns on only if outdoor air is colder than house air by the help margin.
- Otherwise hold/off.

Last changed:
- Imported by P0057 from G1.

### Future local VVX power-fault protection

Status: durable requirement; not yet implemented

Operator observation:
- During summer operation the rotating VVX physically jammed/stuck.
- In that failure state measured electrical power was approximately `70 W`.
- Normal observed running power is approximately `30 W`.

Required L2 safety behavior:
- When VVX is commanded/running, its local device controller must monitor measured active power.
- Normal accepted running-power window is currently defined as `25..35 W` inclusive.
- Measured running power below `25 W` or above `35 W` must be treated as a local VVX fault condition.
- On detection of such a fault, L2 must stop/de-energize the VVX locally without depending on L3, Home Assistant, Mac or network availability.
- The fault condition should be made observable upward for diagnostics/alarms.

Design work still required before implementation:
- define startup grace time before enforcing the power window
- define how long an out-of-range reading must persist before trip, to reject transients/noise
- define fault latching and reset/retry policy
- distinguish commanded-off power semantics from commanded-on/running power semantics
- decide whether repeated trips should lock out automatic restart until explicit operator reset

Architectural classification:
- This belongs to L2 hardware protection. Upper layers may request VVX operation, but they must not be able to override this local protection.

## State Runtime

### applyVvxRun()

Status: imported baseline

Source:
- `src/shelly/ftx/state/run-process.js`

Purpose:
- Derives `ctx.run.vvx` from VVX actuator telemetry.

Contract:
- VVX is considered running when switch is on and measured power is at least the configured threshold.
- VVX RPM is not used in the current baseline.

Last changed:
- Imported by P0057 from G1.

### calcVvxEfficiencyRaw()

Status: imported baseline

Source:
- `src/shelly/ftx/state/perf-vvx.js`

Purpose:
- Calculates raw VVX efficiency from four temperatures, clips supply/extract side values and averages them.

Known limitation:
- The raw formula is only meaningful when VVX is running. P0058 gates the feature-level output to `0` when `ctx.run.vvx` is false.

Last changed:
- P0058 gated reported VVX efficiency by run state.

### calcVvxEfficiencyFeature()

Status: active

Source:
- `src/shelly/ftx/state/perf-vvx.js`

Purpose:
- Calculates and stores reported VVX efficiency on the state context.

Contract:
- If `ctx.run.vvx` is false, reported VVX efficiency is `0` and smoothing history is reset to zero.
- If `ctx.run.vvx` is true, uses the existing four-temperature efficiency calculation and smoothing history.
- P0062 applies the same stopped-VVX zero guard to the legacy duplicate `feature-vvx-efficiency.js` path so source-level behavior is unambiguous even outside the current recipe path.

Last changed:
- P0058/P0062
