# G2 Smart Home System Overview

G2 Smart Home is the next-generation whole-house control system.

It coordinates multiple subsystems as one energy, comfort and safety system:

- FTX ventilation
- VP1 / VP2 heat pumps
- floor heating
- floor cooling
- domestic hot water / VVB
- VVC
- brine loop, shunts and pumps
- spot-price and forecast optimization
- Home Assistant integration
- Mac-side forecasting, diagnostics and local tooling
- Shelly runtime control where low-level hardware control must remain local

## Runtime surfaces

G2 may run code in multiple environments:

```text
Mac             development, deploy, diagnostics, Codex/local tools, forecasts/lab projects
Home Assistant  visualization, user interface, dashboards and user-facing controls
Shelly          autonomous local runtime, local hardware control, fallback, deterministic edge logic
```

## Runtime responsibility principle

Shelly devices must be able to live without Mac or Home Assistant at runtime.

This does not mean every advanced optimization must run on Shelly. It means that a Shelly device that owns local hardware behavior must have enough local state, fallback and deterministic logic to remain safe and useful if Mac and Home Assistant are unavailable.

Home Assistant is primarily the visualization and user-interface surface. It may expose controls, display state and provide convenient user workflows, but G2 hardware safety and local runtime continuity must not depend on Home Assistant being up.

The Mac is primarily for development, build/deploy, diagnostics and controlled package execution. The Mac may also run forecasting, experimentation and lab projects, including projects that are adjacent to but not directly part of house runtime, such as spot-price forecast experiments. A Mac forecast or optimizer may improve G2 behavior, but Shelly runtime must define stale/fallback behavior when Mac-produced data is absent.

## Mac layer

Mac code is first-class G2 code.

Mac tools and Mac services are siblings:

```text
Mac tools:
  Shelly build/chunkify/deploy validation, diagnostics, package helpers

Mac services:
  spot forecast, weather forecast, ML/POC jobs, bridge/helpers
```

A package may update Mac and Shelly code together when they form one solution change.

Example:

```text
updated spot forecast service on Mac
+
updated Shelly client that consumes the new forecast contract
```

When a Shelly runtime consumes Mac-produced data, the package must define contract, freshness, stale handling and fallback behavior so the Shelly remains autonomous if the Mac service disappears.

## Deploy surfaces

Deployable artifacts live under:

```text
dep/m/   Mac
dep/ha/  Home Assistant
dep/s/   Shelly
```

Shelly paths are intentionally short. Shelly devices should fetch from `dep/s/` only.

## Development source

Development source lives under:

```text
src/
```

Expected high-level layout:

```text
src/mac/
src/shelly/
src/ha/
```

`src/` may be more developer-friendly than deploy paths. Build/copy/generation steps may later create `dep/` artifacts.

## Shelly source/build/deploy separation

Shelly source structure is not the same as Shelly deploy chunk structure.

G2 uses three layers for Shelly code:

```text
src/shelly/   logical source code
build/        complete built scripts
dep/s/        deployable registry, manifests, recipes and numeric chunks
```

Deploy chunks are generated transport artifacts and are split by size, not by logical source architecture.

## Operating goal

G2 must be designed to run for years without manual intervention.

This requires deterministic loops, explicit ownership, conservative fallbacks and observable state.
