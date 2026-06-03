# P0051 implementation design

## Package interpretation

P0051 discovers and ingests observed SE1-SE4 physical balance signals. The package will use eSett Open Data as the selected source and aggregate quarter-hour production/consumption values to hourly canonical rows.

## Source selection

Selected source:

```text
eSett Open Data API
base_url = https://api.opendata.esett.com
consumption = /EXP15/Consumption
production = /EXP16/Volumes
```

Svenska kraftnät is documented but not selected for ingestion because eSett provides the required SE1-SE4 machine-readable endpoint contracts directly.

## Database strategy

Use the existing local feature DB path from `spotprice_ml_model.core.DEFAULT_FEATURE_DB`.

Create/rebuild:

```text
physical_balance_hourly_raw_v1
physical_balance_hourly_v1
physical_balance_se1_se4_hourly_v1
```

Rows are deterministic and idempotent. The implementation drops/recreates the package-owned derived tables for this diagnostics package.

## Time strategy

Normalize source `timestampUTC` to UTC hour keys. Source quarter-hour rows are bucketed by hour and aggregated with arithmetic mean. Fixed-CET fields use the existing project convention:

```text
model_cet_timestamp = timestamp_utc + 1h all year
```

## Historical range

The package inspects current modeling range from `se3_se1_demand_response_analysis_v1` or earlier SE3-SE1 tables. It fetches the overlapping range from eSett in monthly chunks.

## Derived features

Canonical wide features include zone-level consumption, production, net load and north/south aggregates. `net_load = consumption - production`, positive meaning demand exceeds local production.

## Evidence strategy

Write all required P0051 evidence files. `component-attribution-summary.md` answers the 16 required questions explicitly.

## Tests

Unit tests cover response parsing, UTC normalization, fixed-CET fields, hourly aggregation, idempotent table persistence on an in-memory SQLite DB, SE1-SE4 mapping, net-load/north-south aggregates and forbidden path constants.

## Risks and uncertainty

- eSett data is quarter-hourly; P0051 creates hourly mean-MW observations, not hourly energy MWh.
- Full historical fetch depends on live eSett availability and rate limiting.
- Production by type is available in eSett production responses; consumption is split into metered/profiled/flex where present.
