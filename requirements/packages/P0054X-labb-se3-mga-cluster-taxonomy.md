# Package P0054X: LABB SE3 MGA cluster taxonomy

## Status

planned

## Package order

P0054X

## Label

```text
LABB
```

This package is local research work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Build an interpretable cluster taxonomy for SE3 MGAs after P0054W has loaded MGA consumption data.

The goal is to understand what each MGA represents and create stable modeling clusters for the next hierarchical SE3 consumption-forecast package.

P0054X must not train the final consumption forecast model. It prepares the grouping layer.

## Input dependency

P0054X depends on P0054W producing usable MGA data in the local database.

Expected P0054W outputs:

```text
esett_mga_consumption_native_v1
esett_mga_masterdata_v1
optional: esett_mga_consumption_hourly_v1
settlement_class preserved
resolution_minutes preserved
MGA-to-price-area mapping attempted
SE3 MGA list identified
```

If P0054W is incomplete but has checkpointed partial SE3 data, P0054X may run a limited prototype only if it clearly labels results as partial. The intended full package should run after P0054W completes the SE3 load.

## Core hypothesis

SE3 direct modeling is strong, but a middle/bottom-up model may improve if MGAs are grouped by behavioral and climate similarity.

Candidate dimensions:

```text
settlement/resolution behavior:
  monthly/profiled
  60m measured
  15m measured
  mixed/native transition

settlement class:
  monthly_settled/profiled
  hourly_settled
  15m_settled
  unknown/other

urban/load structure:
  big-city apartment/service dominated
  villa/suburban heating dominated
  mixed small-city/town
  rural/agriculture/sparse load
  industrial or large-site dominated if detectable

climate geography within SE3:
  northern inland
  east coast / Mälardalen / Stockholm coast
  west coast / Gothenburg area
  southern inland / Småland/north Götaland

load-shape behavior:
  temperature sensitivity
  weekday/weekend ratio
  morning/evening peak shape
  base-load share
  seasonal amplitude
  holiday sensitivity
  rampiness/volatility
```

The operator expects around 16 clusters as a first target:

```text
approximately 4 urban/load-structure groups x 4 climate/geography groups
```

Settlement/resolution class may either be a separate dimension or may split clusters where behavior differs strongly.

## Required outputs

P0054X must produce:

```text
1. MGA inventory for SE3
2. feature set describing each MGA
3. human-readable MGA classification
4. cluster proposal around 16 clusters
5. evidence that clusters are not only mathematical but interpretable
6. recommendation for the next forecasting package
```

## Data sources to inspect

Primary:

```text
P0054W database tables
P0054W evidence files
MGA masterdata
MGA consumption native/hourly derived data
```

Additional local sources if present:

```text
MGA names
DSO/grid owner names
municipality or region mappings
coordinates or polygon centroids
weather station/proxy mapping
SCB/municipality population or housing metadata if already local
repo docs/data inventories
```

No external live API integration unless already approved in project. If external enrichment is needed, document it as a future enrichment rather than blocking the first clustering.

## Required feature engineering

### A. Data availability features

For each SE3 MGA:

```text
first_timestamp
last_timestamp
row_count
coverage_ratio_since_2022_06_01
missing_interval_count
duplicate_interval_count
native_resolution_mix: share_15m/share_60m/share_monthly
resolution_transition_date_candidate
settlement_class_mix
```

### B. Load shape features

Use hourly derived measured/profileresolved data only where defensible.

Candidate features:

```text
mean_load_mw
median_load_mw
p95_load_mw
base_load_ratio = p10 / mean
seasonal_amplitude = winter_mean / summer_mean or winter_minus_summer
heating_sensitivity_proxy = load_vs_temperature_slope if temperature can be mapped
weekday_weekend_ratio
holiday_ratio
morning_peak_ratio
evening_peak_ratio
night_min_ratio
ramp_p95
volatility
monthly_profile_share if separate settlement class exists
```

### C. Geography/climate features

If coordinates/municipality/DSO mapping exists, derive:

```text
latitude/longitude or centroid
nearest weather station/proxy
climate_region_candidate
coastal/inland flag if defensible
north/south/east/west region within SE3
```

If not available, classify using available names/DSO/mapping and label confidence.

### D. Urbanity/load-structure features

Use available local metadata if present. Otherwise infer conservatively from:

```text
MGA name
DSO/grid owner
municipality mapping
load shape
base-load ratio
seasonal sensitivity
weekday/weekend behavior
peak shapes
```

Allowed labels:

```text
big_city_apartment_service
villa_suburban
mixed_small_city_town
rural_sparse
industrial_or_large_site
unknown
```

Every inferred label must include a confidence:

```text
high / medium / low
```

## Cluster design

P0054X must test at least these designs:

### C0: No cluster / direct SE3 reference

Not a model, only a reference from prior packages.

### C1: Settlement/resolution groups

```text
monthly/profiled
60m measured
15m measured
mixed
unknown
```

### C2: Climate groups

Target around 4 groups:

```text
northern_inland
east_coast_malardalen_stockholm
west_coast_gothenburg
southern_inland_smaland_north_gotaland
unknown
```

### C3: Urban/load-structure groups

Target around 4 groups:

```text
big_city_apartment_service
villa_suburban
mixed_small_city_town
rural_sparse_or_agriculture
industrial_or_large_site
unknown
```

### C4: Combined 4x4 cluster taxonomy

Combine climate x urban/load structure where coverage supports it.

Target:

```text
approximately 16 clusters
```

Rules:

```text
merge clusters with too few MGAs or too little load volume
keep unknown cluster rather than forcing bad labels
preserve settlement_class/resolution flags as modeling features or subcluster flags
```

### C5: Data-driven validation overlay

Run a simple clustering analysis on load-shape features, for example k-means/hierarchical/GMM if available, only as validation/support.

Do not let a black-box clustering override interpretable taxonomy without explanation.

## Minimum cluster quality checks

For each proposed cluster:

```text
cluster_id
cluster_label
member_mga_count
total_mean_load_mw
share_of_se3_load
dominant_settlement_class
dominant_resolution
coverage_ratio
mean seasonal amplitude
mean weekday/weekend ratio
mean heating sensitivity if available
assigned climate group
assigned urban/load group
confidence
known caveats
```

P0054X must flag clusters that are too small for standalone modeling:

```text
small by MGA count
small by load volume
low coverage
mixed settlement/resolution risk
unknown geography risk
```

## Database outputs

If repo database ownership allows, create or populate local tables:

```text
se3_mga_cluster_taxonomy_v1
se3_mga_cluster_features_v1
```

Minimum taxonomy columns:

```text
mga_id
mga_name
bidding_zone
cluster_id
cluster_label
climate_group
urban_load_group
settlement_group
resolution_group
confidence
valid_from nullable
valid_to nullable
generated_by_package = P0054X
```

Minimum feature columns:

```text
mga_id
feature_name
feature_value
feature_unit nullable
feature_period_start_utc
feature_period_end_utc
generated_by_package = P0054X
```

If DB write is not practical, produce compact CSV evidence files, but do not commit large time-series dumps.

## Required evidence files

Create:

```text
requirements/package-runs/P0054X/CHANGELOG.md
requirements/package-runs/P0054X/review.md
requirements/package-runs/P0054X/design.md
requirements/package-runs/P0054X/functions.md
requirements/package-runs/P0054X/labb-label.md
requirements/package-runs/P0054X/p0054w-input-review.md
requirements/package-runs/P0054X/mga-inventory.md
requirements/package-runs/P0054X/data-availability-features.md
requirements/package-runs/P0054X/settlement-resolution-classification.md
requirements/package-runs/P0054X/geography-climate-classification.md
requirements/package-runs/P0054X/urban-load-structure-classification.md
requirements/package-runs/P0054X/load-shape-feature-summary.md
requirements/package-runs/P0054X/cluster-designs-tested.md
requirements/package-runs/P0054X/recommended-16-cluster-taxonomy.md
requirements/package-runs/P0054X/cluster-quality-review.md
requirements/package-runs/P0054X/modeling-readiness-review.md
requirements/package-runs/P0054X/database-output-evidence.md if DB tables are written
requirements/package-runs/P0054X/what-we-learned.md
requirements/package-runs/P0054X/next-package-recommendation.md
```

Optional compact evidence:

```text
se3-mga-cluster-taxonomy.csv
se3-mga-cluster-features-summary.csv
cluster-quality-summary.csv
```

Do not commit large raw MGA time-series data.

## Files to inspect

```text
requirements/package-runs/P0054W/**
requirements/packages/P0054W-labb-esett-mga-consumption-discovery.md
requirements/packages/P0054W-operator-clarification-heavy-se3-mga-fetch.md
requirements/packages/P0054W-operator-clarification-complete-fetch-not-half-step.md
requirements/package-runs/P0054V2/decision.md
requirements/package-runs/P0054T4/inference-noise-summary.json
src/mac/**
tests/mac/**
docs/functions/mac/**
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0054X-labb-se3-mga-cluster-taxonomy.md
requirements/package-runs/P0054X/**
src/mac/** narrowly scoped clustering/feature scripts if needed
tests/mac/** narrowly scoped tests for cluster feature helpers if code is added
docs/functions/mac/** if durable docs need updating
local database schema/migration files if this repo owns them and only for P0054X tables
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No external live enrichment integration without explicit approval.
No credentials or tokens.
No large raw data commits.
No final forecasting model training in this package.
No forced assignment of unknown MGAs into named climate/urban clusters without confidence/caveat.
No mixing monthly/profiled and measured series without preserving settlement_class.
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- P0054W input is usable enough for SE3 clustering.
- SE3 MGA inventory is produced.
- settlement/resolution classification is produced.
- geography/climate classification is attempted with confidence/caveats.
- urban/load-structure classification is attempted with confidence/caveats.
- approximately 16-cluster taxonomy is proposed, with small/unknown clusters handled safely.
- next forecasting package recommendation is clear.
```

WARN is acceptable if:

```text
- some MGAs lack geography/urban metadata and remain unknown.
- P0054W data is partial but enough for prototype taxonomy.
- DB table write is skipped but compact evidence exists.
- load-shape features cannot compute heating sensitivity due to missing weather mapping.
```

STOP if:

```text
- P0054W has no usable SE3 MGA consumption data.
- MGA identity/mapping is too incomplete to create a defensible taxonomy.
- settlement/resolution cannot be classified enough to avoid mixing incompatible series.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
P0054W input status
SE3 MGA count
cluster count and labels
settlement/resolution group counts
climate group counts
urban/load group counts
unknown/low-confidence count
largest/smallest clusters by load
whether ~16 clusters are usable for modeling
recommended next package
tests/commands run
files changed
confirmation no credentials, no external enrichment integration, no large raw data committed
```

## Completion notes

To be filled after implementation.
