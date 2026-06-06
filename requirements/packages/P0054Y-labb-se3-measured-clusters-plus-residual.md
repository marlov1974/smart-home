# Package P0054Y: LABB SE3 measured clusters plus residual consumption series

## Status

planned

## Package order

P0054Y

## Label

```text
LABB
```

This package is local research work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Create the practical SE3 geographic consumption series design after P0054W found that monthly/profiled MGA series could not be located with the available sources.

The current workable design is:

```text
A. measured 15m/60m MGA load:
   split into 16 interpretable clusters using the earlier climate x urban/load design

B. missing monthly/profiled load:
   one SE3 residual series
   residual = ENTSO-E SE3 actual total load - sum(measured 15m/60m MGA load)
```

This creates a complete SE3 decomposition while preserving the fact that measured MGA data only covers a minority of the total SE3 load.

P0054Y prepares series for later forecasting. It must not claim that measured MGA clusters alone represent full SE3 consumption.

## Required input sources

### Total SE3 target

Use corrected ENTSO-E actual total load:

```text
table: entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
```

### Measured MGA load

Use P0054W loaded measured MGA data:

```text
esett_mga_consumption_native_v1
and/or derived hourly view/table if created defensibly
```

Only use settlement/resolution classes that are actually measured 15m/60m or safely classified as hourly/15m settled measured load.

Do not include unknown settlement or monthly/profiled as measured.

## Critical background

P0054W/P0054W clarifications found or assumed:

```text
measured 15m/60m MGA data exists
monthly/profiled MGA consumption series could not be found after available search
measured-only coverage is about 23% of SE3 total consumption
therefore measured-only bottom-up is incomplete
```

P0054Y must explicitly preserve this limitation.

## Series to create

Create, validate and document these hourly series:

```text
1. 16 measured-MGA cluster series
2. 1 SE3 residual monthly/profiled/missing-load series
3. optional total reconstructed series = sum(16 measured clusters) + residual
```

The residual series is not directly observed monthly/profiled load. It is a calculated balancing residual:

```text
se3_residual_consumption_mw = entsoe_se3_consumption_mw - sum_measured_mga_clusters_mw
```

Suggested residual label:

```text
SE3_RESIDUAL_MONTHLY_PROFILED_UNOBSERVED
```

## Cluster design

Use 16 clusters for measured 15m/60m MGAs:

```text
4 climate/geography groups x 4 urban/load-structure groups
```

Climate/geography groups:

```text
EAST_COAST_MALARDALEN_STOCKHOLM
WEST_COAST_GOTHENBURG
NORTHERN_INLAND
SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND
```

Urban/load-structure groups:

```text
BIG_CITY_APARTMENT_SERVICE
VILLA_SUBURBAN
MIXED_SMALL_CITY_TOWN
RURAL_SPARSE_AGRICULTURE
```

Optional special classification may be kept as metadata, but the primary measured cluster grid should remain 16 clusters unless an MGA clearly cannot be classified.

If some measured MGAs remain unknown, create safe unknown/catch-all measured clusters and document them. Do not force bad labels.

## Residual interpretation

The residual represents the part of SE3 load not explained by the measured MGA set.

It likely includes:

```text
monthly-settled/profiled consumption
unmapped MGA consumption
unknown settlement classes
coverage gaps
measurement/source differences between eSett and ENTSO-E
```

Because residual is calculated using ENTSO-E total load, it is valid as a historical decomposition target but must be handled carefully in forecasting:

```text
historical target: allowed
future actual residual: not allowed as feature
forecast residual model: allowed in later package
```

## Required hourly aggregation semantics

For measured MGA data:

```text
15m energy -> hourly energy by summing 4 intervals, then MW equivalent if needed
60m measured rows -> hourly value after unit/value_kind validation
```

Rules:

```text
preserve settlement_class
preserve native resolution metadata
never mix measured and residual into the same cluster
never treat residual as observed MGA series
```

## Output tables/views

If repo database ownership allows, create/populate:

```text
se3_measured_mga_cluster_hourly_v1
se3_consumption_residual_hourly_v1
se3_consumption_decomposition_hourly_v1
```

### measured cluster table columns

```text
timestamp_utc
cluster_id
cluster_label
consumption_mw
mga_count
source_settlement_group = measured_15m_60m
native_resolution_mix
coverage_ratio
input_row_count
generated_by_package = P0054Y
```

### residual table columns

```text
timestamp_utc
area = SE3
residual_consumption_mw
entsoe_total_consumption_mw
measured_cluster_sum_mw
measured_share_of_total
residual_share_of_total
residual_definition
generated_by_package = P0054Y
```

### decomposition table columns

```text
timestamp_utc
component_type = measured_cluster or residual
component_id
component_label
consumption_mw
share_of_total
is_observed_component
is_calculated_residual
generated_by_package = P0054Y
```

If DB writes are not practical, create compact evidence CSVs, but do not commit large full time-series dumps.

## Validation requirements

P0054Y must report:

```text
measured_cluster_sum_mean_mw
entsoe_se3_mean_mw
measured_share_mean
residual_share_mean
residual_mean_mw
residual_min_mw
residual_p05_mw
residual_p95_mw
residual_max_mw
negative_residual_hours_count
negative_residual_hours_examples
missing_measured_hours_count
missing_entsoe_hours_count
```

Expected measured share may be around:

```text
~23%
```

Do not fail only because measured share is low; that is the known reason for residual modeling.

But WARN/STOP if residual is often negative or wildly unstable without explanation.

## Required evidence files

Create:

```text
requirements/package-runs/P0054Y/CHANGELOG.md
requirements/package-runs/P0054Y/review.md
requirements/package-runs/P0054Y/design.md
requirements/package-runs/P0054Y/functions.md
requirements/package-runs/P0054Y/labb-label.md
requirements/package-runs/P0054Y/p0054w-input-review.md
requirements/package-runs/P0054Y/measured-mga-cluster-contract.md
requirements/package-runs/P0054Y/measured-16-cluster-assignment.md
requirements/package-runs/P0054Y/hourly-aggregation-contract.md
requirements/package-runs/P0054Y/residual-definition.md
requirements/package-runs/P0054Y/output-table-schema.md
requirements/package-runs/P0054Y/decomposition-validation.md
requirements/package-runs/P0054Y/coverage-vs-entsoe.md
requirements/package-runs/P0054Y/residual-quality-review.md
requirements/package-runs/P0054Y/database-output-evidence.md if DB tables are written
requirements/package-runs/P0054Y/modeling-readiness-review.md
requirements/package-runs/P0054Y/what-we-learned.md
requirements/package-runs/P0054Y/next-package-recommendation.md
```

Optional compact evidence:

```text
measured-cluster-assignment.csv
cluster-volume-summary.csv
residual-quality-summary.csv
decomposition-summary.json
```

Do not commit large raw time-series dumps.

## Files to inspect

```text
requirements/package-runs/P0054W/**
requirements/packages/P0054W-operator-clarification-profiled-monthly-critical.md
requirements/packages/P0054X-labb-se3-mga-cluster-taxonomy.md
requirements/packages/P0054X-operator-clarification-32-clusters.md
requirements/packages/P0054X-operator-clarification-cluster-size-by-load-not-mga-count.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0054V2/decision.md
src/mac/**
tests/mac/**
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0054Y-labb-se3-measured-clusters-plus-residual.md
requirements/package-runs/P0054Y/**
src/mac/** narrowly scoped measured-cluster/residual series construction code if needed
tests/mac/** narrowly scoped tests for aggregation/residual construction if code is added
docs/functions/mac/** if durable docs need updating
local database schema/migration files if this repo owns them and only for P0054Y tables
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No external live data integration.
No credentials or tokens.
No large raw data commits.
No final forecasting model training in this package.
No treating measured 23% coverage as full SE3 load.
No pretending residual is directly observed monthly/profiled MGA data.
No future actual residual used as feature.
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- measured MGA data is available enough to create cluster series.
- 16 measured cluster design is applied or safe unknown/catch-all is documented.
- SE3 residual series is created from ENTSO-E total minus measured cluster sum.
- decomposition validates reasonably: measured + residual = total by construction.
- residual quality is reviewed.
- output contract for next forecasting package is clear.
```

WARN is acceptable if:

```text
- some measured MGAs remain unknown/catch-all.
- measured coverage is low, as expected, but residual is stable enough to model.
- DB writes are skipped but compact evidence exists.
- residual has occasional negative hours that are explained by timing/unit/coverage caveats.
```

STOP if:

```text
- P0054W measured data is not available.
- measured aggregation cannot be made unit-safe.
- residual is frequently negative or nonsensical.
- ENTSO-E total target cannot be joined.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
P0054W input status
measured MGA coverage percent
16 measured cluster list and volumes
residual series mean/share/quality
negative residual count
DB output tables or evidence files created
whether series are ready for forecasting
recommended next package
tests/commands run
files changed
confirmation no credentials, no external integration, no large raw data committed
```

## Completion notes

To be filled after implementation.
