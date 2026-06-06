# Package P0054Y2: LABB SE3 profiled clusters plus metered residual series

## Status

planned

## Package order

P0054Y2

## Label

```text
LABB
```

This package is local research work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Create the practical SE3 decomposition that matches the data actually found in P0054W.

Current repository evidence says the accessible per-MGA source is not measured/non-profiled 15m/60m load. It is:

```text
source: EXP18/LoadProfile
settlement_class: profiled_load_profile
matches: EXP15/Consumption.profiled
coverage_vs_ENTSOE_SE3: about 23.2%
```

Therefore the correct practical decomposition is:

```text
A. profiled/load-profile MGA component:
   split into 16 interpretable clusters using climate x urban/load design

B. missing metered/non-profiled/other component:
   one SE3 residual series
   residual = ENTSO-E SE3 actual total load - sum(profiled/load-profile MGA clusters)
```

P0054Y2 supersedes P0054Y for the current data reality.

## Why P0054Y stopped

P0054Y expected:

```text
16 measured 15m/60m MGA clusters
+ residual monthly/profiled/missing-load
```

But the repository evidence showed:

```text
repo has: profiled/load-profile per-MGA component
repo lacks: metered/non_profiled per-MGA component
```

Running P0054Y as written would invert the decomposition semantics. P0054Y2 fixes that.

## Required input sources

### Total SE3 target

Use corrected ENTSO-E actual total load:

```text
table: entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
```

### Profiled/load-profile MGA data

Use P0054W loaded source:

```text
EXP18/LoadProfile-derived local DB data
settlement_class = profiled_load_profile or equivalent
```

Use the local table/view actually produced by P0054W, documenting its name exactly.

Do not relabel profiled/load-profile data as measured 15m/60m load.

## Series to create

Create, validate and document these hourly series:

```text
1. 16 profiled/load-profile MGA cluster series
2. 1 SE3 residual metered/non_profiled/unobserved series
3. optional total reconstructed series = sum(16 profiled clusters) + residual
```

The residual series is not directly observed measured load. It is a calculated balancing residual:

```text
se3_residual_metered_non_profiled_mw
=
entsoe_se3_consumption_mw - sum_profiled_load_profile_clusters_mw
```

Suggested residual label:

```text
SE3_RESIDUAL_METERED_NON_PROFILED_UNOBSERVED
```

## Cluster design

Use 16 clusters for profiled/load-profile MGAs:

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

If some MGAs remain unknown, create safe unknown/catch-all profiled clusters and document them. Do not force bad labels.

Cluster size must be judged by load/data quality, not raw MGA count.

## Residual interpretation

The residual represents the part of SE3 load not explained by the profiled/load-profile MGA set.

It likely includes:

```text
metered/non-profiled consumption
large measured customers
industrial and commercial measured load
unmapped MGA consumption
unknown settlement classes
coverage gaps
measurement/source differences between eSett/NBS and ENTSO-E
```

Because residual is calculated using ENTSO-E total load, it is valid as a historical decomposition target but must be handled carefully in forecasting:

```text
historical target: allowed
future actual residual: not allowed as feature
forecast residual model: allowed in later package
```

## Required hourly aggregation semantics

For profiled/load-profile MGA data:

```text
preserve source settlement_class = profiled_load_profile
validate source unit and value_kind
aggregate to hourly only with documented method
```

Rules:

```text
never call this component measured 15m/60m load
never mix residual into a profiled cluster
never treat residual as directly observed per-MGA data
preserve source coverage and resolution metadata
```

## Output tables/views

If repo database ownership allows, create/populate:

```text
se3_profiled_mga_cluster_hourly_v1
se3_consumption_metered_residual_hourly_v1
se3_consumption_profiled_residual_decomposition_hourly_v1
```

### profiled cluster table columns

```text
timestamp_utc
cluster_id
cluster_label
consumption_mw
mga_count
source_settlement_group = profiled_load_profile
native_resolution_mix
coverage_ratio
input_row_count
generated_by_package = P0054Y2
```

### residual table columns

```text
timestamp_utc
area = SE3
residual_metered_non_profiled_mw
entsoe_total_consumption_mw
profiled_cluster_sum_mw
profiled_share_of_total
residual_share_of_total
residual_definition
generated_by_package = P0054Y2
```

### decomposition table columns

```text
timestamp_utc
component_type = profiled_cluster or metered_residual
component_id
component_label
consumption_mw
share_of_total
is_observed_component
is_calculated_residual
generated_by_package = P0054Y2
```

If DB writes are not practical, create compact evidence CSVs, but do not commit large full time-series dumps.

## Validation requirements

P0054Y2 must report:

```text
profiled_cluster_sum_mean_mw
entsoe_se3_mean_mw
profiled_share_mean
residual_share_mean
residual_mean_mw
residual_min_mw
residual_p05_mw
residual_p95_mw
residual_max_mw
negative_residual_hours_count
negative_residual_hours_examples
missing_profiled_hours_count
missing_entsoe_hours_count
```

Expected profiled share may be around:

```text
~23%
```

Do not fail only because profiled share is low; that is the known reason for residual modeling.

WARN/STOP if residual is often negative or wildly unstable without explanation.

## Required evidence files

Create:

```text
requirements/package-runs/P0054Y2/CHANGELOG.md
requirements/package-runs/P0054Y2/review.md
requirements/package-runs/P0054Y2/design.md
requirements/package-runs/P0054Y2/functions.md
requirements/package-runs/P0054Y2/labb-label.md
requirements/package-runs/P0054Y2/p0054y-stop-review.md
requirements/package-runs/P0054Y2/p0054w-input-review.md
requirements/package-runs/P0054Y2/profiled-mga-cluster-contract.md
requirements/package-runs/P0054Y2/profiled-16-cluster-assignment.md
requirements/package-runs/P0054Y2/hourly-aggregation-contract.md
requirements/package-runs/P0054Y2/residual-definition.md
requirements/package-runs/P0054Y2/output-table-schema.md
requirements/package-runs/P0054Y2/decomposition-validation.md
requirements/package-runs/P0054Y2/coverage-vs-entsoe.md
requirements/package-runs/P0054Y2/residual-quality-review.md
requirements/package-runs/P0054Y2/database-output-evidence.md if DB tables are written
requirements/package-runs/P0054Y2/modeling-readiness-review.md
requirements/package-runs/P0054Y2/what-we-learned.md
requirements/package-runs/P0054Y2/next-package-recommendation.md
```

Optional compact evidence:

```text
profiled-cluster-assignment.csv
cluster-volume-summary.csv
metered-residual-quality-summary.csv
decomposition-summary.json
```

Do not commit large raw time-series dumps.

## Files to inspect

```text
requirements/package-runs/P0054Y/CHANGELOG.md
requirements/package-runs/P0054Y/review.md
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
requirements/packages/P0054Y2-labb-se3-profiled-clusters-plus-metered-residual.md
requirements/package-runs/P0054Y2/**
src/mac/** narrowly scoped profiled-cluster/residual series construction code if needed
tests/mac/** narrowly scoped tests for aggregation/residual construction if code is added
docs/functions/mac/** if durable docs need updating
local database schema/migration files if this repo owns them and only for P0054Y2 tables
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
No treating profiled 23% coverage as full SE3 load.
No pretending residual is directly observed measured/non-profiled data.
No future actual residual used as feature.
No relabeling EXP18/LoadProfile as measured load.
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- profiled/load-profile MGA data is available enough to create cluster series.
- 16 profiled cluster design is applied or safe unknown/catch-all is documented.
- SE3 residual metered/non_profiled series is created from ENTSO-E total minus profiled cluster sum.
- decomposition validates reasonably: profiled + residual = total by construction.
- residual quality is reviewed.
- output contract for next forecasting package is clear.
```

WARN is acceptable if:

```text
- some profiled MGAs remain unknown/catch-all.
- profiled coverage is low, as expected, but residual is stable enough to model.
- DB writes are skipped but compact evidence exists.
- residual has occasional negative hours that are explained by timing/unit/coverage caveats.
```

STOP if:

```text
- P0054W profiled/load-profile data is not available.
- profiled aggregation cannot be made unit-safe.
- residual is frequently negative or nonsensical.
- ENTSO-E total target cannot be joined.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
P0054Y stop review
P0054W input status
profiled coverage percent
16 profiled cluster list and volumes
metered/non_profiled residual mean/share/quality
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
