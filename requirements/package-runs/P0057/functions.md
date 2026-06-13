# Package P0057 Function Design

## Package

`P0057`

## Scope

Imported FTX Shelly runtime source under `src/shelly/ftx/`.

This is an import package. It does not add or change runtime function behavior. The function design records important imported entry points and safety-critical unchanged functions for future packages.

## New functions

None.

## Changed functions

None.

## Removed functions

None.

## Important unchanged functions

### calcVvx()

Reason for no change:
- Imported as current baseline. Brain-level VVX logic grants permission based on FTX enable state; final thermal decision remains local on the VVX device.

### decideOn()

Reason for no change:
- Imported as current baseline. The VVX executor decides local on/off from fresh intent, target, house temperature and outdoor temperature.

### calcVvxEfficiencyRaw()

Reason for no change:
- Imported as current baseline. Known limitation: the efficiency formula can produce misleading values when VVX is off and cooling is active. P0057 intentionally does not fix behavior.

### applyVvxRun()

Reason for no change:
- Imported as current baseline. Runtime run-status uses switch on plus measured VVX power threshold rather than RPM.

### buildDeviceIntent()

Reason for no change:
- Imported as current baseline. Brain writes per-device full-state intents, including local thermal snapshot for VVX.

### telemetry publisher payload()/sample() functions

Reason for no change:
- Imported as current baseline. Local devices publish concise status/power telemetry to dampers for brain/state use.

## Design deviations during implementation

None yet.
