# Function Catalog Index

This folder contains cross-package function documentation.

The catalog describes the current durable function-level design of G2 code. It is not package-run scratchpad and not an exhaustive generated API reference.

Use it for functions whose behavior matters across packages, runtime roles, contracts, tests or future Codex work.

## Relationship to package-run function design

For code packages, Codex should write package-local function design before implementation:

```text
requirements/package-runs/<Pxxxx>/functions.md
```

After implementation, Codex should update the cross-package function catalog when functions are created, changed, removed or become important for future packages.

## Suggested structure

```text
docs/functions/
  00-index.md
  TEMPLATE.md
  shelly/
    weather.md
    supply-uni-publisher.md
    installer.md
    ftx-brain.md
    ftx-driver.md
  mac/
    shelly-build-tool.md
    shelly-live-deploy-tool.md
    shelly-device-management-tool.md
    weather-contract-tool.md
    spot-forecast.md
  contracts/
    spot-forecast-contract.md
    ftx-intent-contract.md
```

## Rules

- Document externally important or cross-package relevant functions.
- Keep package-specific plans in `requirements/package-runs/<Pxxxx>/functions.md`.
- Do not include temporary implementation thoughts unless they represent the final durable design.
- Update `Last changed` when a package changes function behavior or contract.

## Package history

Created by `P0007-codex-phased-package-build-process`.

`P0017` added `docs/functions/mac/spot-forecast.md` for the Mac spot period index service.
