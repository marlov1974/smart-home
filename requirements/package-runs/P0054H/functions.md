# P0054H Function Design

## New Functions

| function | purpose | inputs | outputs | side effects | tests |
|---|---|---|---|---|---|
| `run_p0054h_generation` | orchestrate source loading, row generation, persistence, metrics and evidence | feature DB path, evidence dir | `P0054HResult` | writes SQLite forecast table and evidence files | generation verification |
| `load_price_rows` | load local SE1 price rows | feature DB path | ordered price rows | none | indirect |
| `build_daily_windows` | create complete 168h forecast-origin windows under one split | price rows | window descriptors | none | indirect |
| `build_anchor_state` | compute strict prior-48h anchor/history state | origin, price map | anchor state | none | unit |
| `predict_price` | compute one target-hour forecast from pre-origin history | target row, origin, anchor state, price map | prediction and rule metadata | none | unit |
| `build_forecast_rows` | create persisted forecast-origin log rows without actual target prices | windows, price map | forecast rows | none | unit/schema |
| `validate_leakage` | verify cutoff, origin, horizon, anchor and training cutoff rules | forecast rows | leakage summary | none | unit |
| `coverage_by_split` | summarize target/origin split coverage | forecast rows | counts/ranges | none | generation verification |
| `evaluate_price_metrics` | compute validation/holdout forecast quality from actual prices | forecast rows, price map | metrics summary | none | generation verification |
| `compare_to_p0053cb` | compare validation/holdout metrics to existing P0053C-B source when present | SQLite connection, P0054H metrics | comparison summary | none | generation verification |
| `write_p0054h_evidence` | write required package evidence | summary, sample rows | path map | writes Markdown/JSON/CSV evidence | generation verification |

## Changed Functions

None.

## Removed Functions

None.

## Durable Function Catalog

`docs/functions/mac/spotprice-model-diagnostics.md` will be updated after implementation to record the new P0054H diagnostics module and its non-M4 contract.
