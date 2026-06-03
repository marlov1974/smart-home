# P0052 implementation design

## Package interpretation

P0052 adds the grid-exchange layer after P0051's production/consumption ingestion. Because auth-free historical capacity is not available from the discovered sources, this package will implement a WARN result: ingest available SvK/Statnett observed flow and import/export data, document capacity as blocked, and make all capacity/utilization features nullable unless their inputs exist.

## Implementation structure

Create `src/mac/services/spotprice_model_diagnostics/p0052.py` using Python standard library only, following the P0051 diagnostic module style.

The module will:

- read P0051/modeling overlap from local SQLite,
- determine a conservative SvK/Statnett available overlap,
- fetch quarter-hour flow-map snapshots,
- parse directed border flows and SE1-SE4 import/export rows,
- aggregate quarter-hour values to hourly mean MW,
- persist long and wide tables,
- validate coverage, uniqueness, direction conventions and joins to P0051,
- compute initial non-model diagnostics against SE3 and SE3-SE1,
- write all required evidence files.

## Intended database tables

`transfer_capacity_flow_raw_v1`

Raw normalized quarter-hour source rows from SvK/Statnett. This table stores flow rows and zone import/export rows. It does not invent capacity rows.

`transfer_capacity_flow_hourly_v1`

Canonical hourly mean MW rows with the P0052 long-format contract: timestamp, fixed-CET fields, source, dataset, from/to area, border, measure, unit, method labels, source update time and quality flag.

`transfer_capacity_flow_se1_se4_hourly_v1`

Wide hourly modeling table for internal Swedish border flows, external Swedish border flows, SE1-SE4 import/export/net import, south/north pressure, balance residuals, flow-based era fields and nullable capacity-derived fields.

## Intended changes

Files to add or update:

- `src/mac/services/spotprice_model_diagnostics/p0052.py`
- `tests/mac/services/spotprice_model_diagnostics/test_p0052.py`
- `requirements/package-runs/P0052/*`
- `requirements/packages/P0052-se1-se4-transfer-capacity-flow-and-import-export-discovery.md`
- `docs/functions/mac/spotprice-model-diagnostics.md`
- `docs/functions/00-index.md`
- possibly `memory/knowhow/spotprice.md` if source/API behavior is durable enough to promote.

Files intentionally not changed:

- Shelly, Home Assistant, KVS, deployment artifacts and production model paths.
- Existing P0051 tables other than read-only joins.
- Continental price-pressure backlog.

## Data handling

Source timestamp identity is requested by epoch milliseconds in SvK's `ticks` query parameter. Responses include `LastUpdated` as epoch milliseconds. Each requested quarter-hour tick is normalized to UTC from the requested tick and stored as source observation time. Fixed-CET fields follow P0042/P0051: `model_cet_timestamp = timestamp_utc + 1h` all year.

Quarter-hour MW values are aggregated to hourly mean MW. Missing quarter-hours remain visible through coverage evidence and `quality_flag`.

Flow direction convention follows the SvK map component:

```text
value for border A_B means A -> B
-value for border A_B means B -> A
```

Zone import/export uses the SvK response's `ElectricalAreas` import/export values for SE1-SE4 when present. If needed, tests also verify deriving import/export from directed border flows.

## Deliberate refactoring decisions

No shared abstraction will be extracted from P0051 in this package. Some timestamp and persistence helpers are repeated to keep P0052 scoped and avoid destabilizing verified earlier packages.

## Test strategy

Unit tests will cover:

- source response parsing,
- timestamp normalization and fixed-CET fields,
- directed border mapping,
- import/export aggregation and net import,
- balance residual formula,
- utilization null/zero handling,
- flow-based era flag,
- idempotent persistence,
- joins to a P0051-shaped physical table,
- forbidden path assertions.

Live verification will run the P0052 module against the local feature database and SvK/Statnett endpoint. If network access fails in sandbox, rerun with approved network access.

## Risks and uncertainties

- SvK's endpoint is a web/control-room contract rather than a formal open API; it may be less stable than ENTSO-E.
- Capacity is blocked without ENTSO-E token-backed access or another machine-readable source.
- Source history appears partial. P0052 must not backfill missing older history with synthetic values.
- The data source labels flows from Statnett but does not prove whether the values are physical flows or scheduled commercial exchanges. Evidence must label them as SvK/Statnett control-room flows and avoid mixing them with capacity concepts.
