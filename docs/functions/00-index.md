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

`P0018` added `docs/functions/mac/weekly-home-optimizer-poc.md` for the Mac weekly heat, PPM and RH-policy lab POC.

`P0020` updated `docs/functions/mac/weekly-home-optimizer-poc.md` with the local browser/API server wrapper.

`P0021` updated `docs/functions/mac/weekly-home-optimizer-poc.md` with real-weather metadata and people-derived occupancy load.

`P0022` updated `docs/functions/mac/weekly-home-optimizer-poc.md` with the discrete DP heat optimizer and heat optimizer metadata.

`P0023` updated `docs/functions/mac/weekly-home-optimizer-poc.md` with the COP emulator and optimized-vs-flat heat electric cost comparison.

`P0024` updated `docs/functions/mac/weekly-home-optimizer-poc.md` with hourly spot planning, 2025 actual-price fixture loading and forecast-sum-preserving actual-price patching.

`P0025` updated `docs/functions/mac/weekly-home-optimizer-poc.md` with fixed 20-hour known spot horizon planning and forecast-vs-actual outcome diagnostics.

`P0026` added `docs/functions/mac/local-kvs-read-poc.md` for the read-only Mac local Shelly KVS.Get NAT helper.

`P0027` added `docs/functions/mac/local-operator-bridge.md` for the read-only MCP-shaped local JSON-RPC operator bridge that delegates to P0026.

`P0028` added `docs/functions/mac/local-operator-mcp.md` for the true MCP stdio adapter over the read-only P0027/P0026 bridge.

`P0029` added `docs/functions/mac/chatgpt-mcp-access.md` for the localhost Streamable HTTP MCP wrapper intended as a private target for Secure MCP Tunnel or another approved ChatGPT-compatible remote endpoint.

`P0030` added `docs/functions/mac/spotprice-history.md` for the Mac historical spotprice SQLite dataset and daily ingest job.

`P0031` added `docs/functions/mac/weather-history-dataset.md` for the Mac historical Open-Meteo weather SQLite dataset and daily ingest job.

`P0032` updated `docs/functions/mac/spotprice-history.md` with the SE1 system-proxy view and updated `docs/functions/mac/weather-history-dataset.md` with weather proxy groups and gradients.

`P0033` added `docs/functions/mac/spotprice-temperature-normalization.md` for the local temperature-normalized spotprice V2 training foundation feature-store builder.

`P0034` added `docs/functions/mac/spotprice-ml-normal-model.md` for the local M4 temperature-neutral normal spot model training and backtest tooling.

`P0035` added `docs/functions/mac/swedish-special-day-calendar.md` and updated the spotprice ML/normalization docs for M3A/M3B and M1-anchored residual M4.

`P0047` updated `docs/functions/mac/spotprice-model-diagnostics.md` with SE3-SE1 spread export, regime threshold and bottleneck diagnostics.

`P0048` updated `docs/functions/mac/spotprice-model-diagnostics.md` with SE3-SE1 bottleneck feature foundation, local modeling dataset persistence and exploratory two-stage diagnostics.

`P0049` updated `docs/functions/mac/spotprice-model-diagnostics.md` with SE3-SE1 reservoir/memory features, price-response proxies, day-type interaction diagnostics and horizon-by-horizon evidence.

`P0050` updated `docs/functions/mac/spotprice-model-diagnostics.md` with baseline-corrected SE3-SE1 residuals, local SE3 price-rank/top-N diagnostics and heat-pump pressure proxy analysis.

`P0051` updated `docs/functions/mac/spotprice-model-diagnostics.md` with eSett SE1-SE4 production/consumption ingestion, physical balance tables, net-load features and initial physical-signal diagnostics.

`P0052` updated `docs/functions/mac/spotprice-model-diagnostics.md` with SvK/Statnett SE1-SE4 transfer flow and import/export ingestion, capacity-source blocker handling, balance residual features and initial capacity/flow diagnostics.

`P0052A` updated `docs/functions/mac/spotprice-model-diagnostics.md` with token-safe ENTSO-E A09/A11/A61 ingestion, internal Swedish capacity/exchange/flow amendment, period-bound `P1M` parsing and sanitized evidence handling.

`P0052B` updated `docs/functions/mac/spotprice-model-diagnostics.md` with A61 capacity concept review, clipped long-period capacity expansion, metadata schema migration, representative ENTSO-E backfill and timestamp-normalized joins.

`P0052C` updated `docs/functions/mac/spotprice-model-diagnostics.md` with A61 capacity ceiling sanity checks against A09 scheduled exchange and A11 physical flow, contract classifications and worst-ratio evidence.

`P0053A` updated `docs/functions/mac/spotprice-model-diagnostics.md` with ENTSO-E A09/A11 internal Swedish historical backfill, net flow/exchange feature derivation and `physical_balance_flow_exchange_analysis_v1`.

`P0053B` updated `docs/functions/mac/spotprice-model-diagnostics.md` with forecast-safe SE1 consumption warmup diagnostics, direct-horizon modeling and 168h path metrics.

`P0053C` updated `docs/functions/mac/spotprice-model-diagnostics.md` with the shared forecast period policy and timestamp-UTC split boundary for SE1 consumption rebuilds.

`P0053C-A` updated `docs/functions/mac/spotprice-model-diagnostics.md` with the M4/P0045 global-split price-shape rebuild and local forecast-origin log contract.
