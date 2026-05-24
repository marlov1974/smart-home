# Mac Layer

Mac code is first-class G2 code.

Deploy/build tools are Mac solutions, just like forecast services and diagnostics.

## Mac responsibilities

The Mac layer may contain:

- Shelly build/deploy tooling
- deploy validation
- package/test runners
- spot price forecast services
- weather forecast processing
- ML/POC experiments
- diagnostics and live-device probes
- Home Assistant bridge/helpers where appropriate
- Codex/local developer workflows

## Tools vs services

Mac tools are run manually, by Codex, by tests or by package workflows.

Examples:

```text
shelly build/chunkify
shelly deploy validation
package evidence helpers
```

Mac direct-deploy tools may use bounded in-memory RPC upload chunks as a transport detail. Those chunks are not repo source architecture and are separate from generated Shelly repo deploy chunks under `dep/s/**`.

Mac services run continuously or on schedule.

Examples:

```text
spot price forecast
weather forecast
ML/forecast jobs
```

Both belong to the Mac layer.

## Source layout

Recommended source layout:

```text
src/mac/
  tools/
    shelly_build/
      build.py
      validate.py
      chunkify.py

  services/
    spot_forecast/
      main.py
      model.py
      output.py

    weather_forecast/
      main.py
      openmeteo.py
      output.py

  diagnostics/
    shelly_probe/
```

## Deploy layout

Mac deploy artifacts live under:

```text
dep/m/
```

Examples:

```text
dep/m/tools/shelly_build/
dep/m/services/spot_forecast/
dep/m/launchd/
```

## Tooling language

Initial G2 deploy/build tooling should use:

```text
Python 3 standard library only
```

Reasons:

- stable on Mac
- easy for Codex to write and debug
- good JSON/file/checksum support
- no Node/npm dependency
- easy to run in CI later

## Cross-environment packages

A package may update both Mac and Shelly artifacts.

Example:

```text
P0017-improve-spot-price-forecast

Mac:
  update spot_forecast service

Shelly:
  update plant-main spot forecast client

Contract:
  update forecast schema/fallback behavior
```

Package scope follows solution behavior, not repo directory boundaries.

## Contract rule

When a Mac service produces data consumed by Shelly or Home Assistant, the package must define or update the data contract:

- schema version
- units
- stale behavior
- fallback behavior
- compatibility/rollout order
- rollback implications
