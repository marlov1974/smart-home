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
Mac             forecasting, ML/POC, diagnostics, developer tooling, Codex, build/deploy tools
Home Assistant  orchestration, UI, integrations, automations where appropriate
Shelly          local hardware control, fallback, deterministic edge logic
```

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
