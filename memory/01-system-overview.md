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
Mac             forecasting, ML/POC, diagnostics, developer tooling, Codex
Home Assistant  orchestration, UI, integrations, automations where appropriate
Shelly          local hardware control, fallback, deterministic edge logic
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

`src/` may be more developer-friendly than deploy paths. Build/copy/generation steps may later create `dep/` artifacts.

## Operating goal

G2 must be designed to run for years without manual intervention.

This requires deterministic loops, explicit ownership, conservative fallbacks and observable state.
