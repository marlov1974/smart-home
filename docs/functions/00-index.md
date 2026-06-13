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
  contracts/
    ftx-intent-contract.md
```

## Rules

- Document externally important or cross-package relevant functions.
- Keep package-specific plans in `requirements/package-runs/<Pxxxx>/functions.md`.
- Do not include temporary implementation thoughts unless they represent the final durable design.
- Update `Last changed` when a package changes function behavior or contract.

## Package history

Created by `P0007-codex-phased-package-build-process`.

`P0017` through `P0025` created and evolved the Mac spot forecast and weekly optimizer lab docs. These moved to `marlov74/Market-Simulator` in `P0061`.

`P0026` added `docs/functions/mac/local-kvs-read-poc.md` for the read-only Mac local Shelly KVS.Get NAT helper.

`P0027` added `docs/functions/mac/local-operator-bridge.md` for the read-only MCP-shaped local JSON-RPC operator bridge that delegates to P0026.

`P0028` added `docs/functions/mac/local-operator-mcp.md` for the true MCP stdio adapter over the read-only P0027/P0026 bridge.

`P0029` added `docs/functions/mac/chatgpt-mcp-access.md` for the localhost Streamable HTTP MCP wrapper intended as a private target for Secure MCP Tunnel or another approved ChatGPT-compatible remote endpoint.

`P0030` through `P0056` created and evolved the Mac market-history, weather-history, spotprice ML, physical-balance and consumption-forecast diagnostics docs. These moved to `marlov74/Market-Simulator` in `P0061`.

`P0057` added `docs/functions/shelly/ftx-runtime-baseline.md` for the imported FTX Shelly runtime baseline from G1.

`P0058` updated `docs/functions/shelly/ftx-runtime-baseline.md` with the VVX efficiency run-state gate.

`P0059` updated `docs/functions/shelly/ftx-runtime-baseline.md` with the no-extra-margin dewpoint minimum supply contract.

`P0060` updated `docs/functions/shelly/ftx-runtime-baseline.md` with the 12.0 C absolute minimum supply floor.

`P0061` moved Mac market-simulator function docs and package history to `marlov74/Market-Simulator`.
