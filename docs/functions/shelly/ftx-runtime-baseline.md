# Shelly FTX Runtime Baseline Function Catalog

## Scope

P0057 imported the current G1 FTX Shelly runtime into G2 under:

```text
src/shelly/ftx/
```

This catalog records the durable high-level entry points and safety-relevant functions for future G2 packages.

## Source Baseline

```text
source repo: marlov1974/shelly
source commit: 761cc4bc1c527d6bdffa0a0783f0cfd1761040f4
package: P0057
```

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

Last changed:
- P0059 removed the added dewpoint supply safety margin.

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

Last changed:
- P0058

## Local Device Telemetry

### telemetry payload/sample functions

Status: imported baseline

Sources:
- `src/shelly/ftx/scripts/*/telemetry_publisher_*`

Purpose:
- Publish local device status and power telemetry for dampers/brain/state consumption.

Last changed:
- Imported by P0057 from G1.
