# Package P0054W: LABB eSett MGA consumption discovery and ingestion

## Status

planned

## Package order

P0054W

## Label

```text
LABB
```

This package is local research/discovery work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Investigate whether consumption/load can be obtained per Swedish MGA / metering grid area / nätavräkningsområde from eSett/NBS or related local/exported data sources.

If a credible and legally/locally accessible MGA consumption source is found, P0054W must also load the data from 2022-06-01 onward into the local database, preserving native resolution and settlement class.

The goal is to determine whether SE3 consumption forecasting can later be improved by geographic granularity:

```text
price area direct model
vs grouped MGA / regional bottom-up model
vs individual MGA bottom-up model
vs reconciled hierarchical ensemble
```

P0054W is a discovery, ingestion and data-contract package only. It must not build the final hierarchical forecast model.

## Operator context

Important expectations to verify:

```text
1. eSett/MGA consumption may be split between monthly-settled and hourly/15-minute-settled series.
2. Early historical series may be 60-minute resolution.
3. Later series may switch to 15-minute resolution.
4. The resolution switch must not be hidden by naive aggregation.
5. Monthly-settled and hourly/15-minute-settled consumption must not be mixed without clear classification.
6. If usable data is found, it must be downloaded/loaded into the database from 2022-06-01 onward.
```

## Definitions to resolve

P0054W must document exact terms found in the data/source:

```text
MGA
Metering Grid Area
nätavräkningsområde
market balance area / grid area if present
settlement method
profiled/monthly settled consumption
hourly settled consumption
15-minute settled consumption
consumption/load direction/sign convention
bidding zone / price area mapping
DSO / grid owner mapping if available
valid-from / valid-to history
```

If eSett terminology differs from Swedish grid-area terminology, document the mapping and uncertainty.

## Data-source discovery scope

Search local repository/database/config first.

Allowed source categories:

```text
existing local DB tables
existing local parquet/csv/json exports
repo scripts/config pointing to eSett/NBS data
public documentation already present in repo
operator-provided files
manual/downloaded files if already local
```

External live API calls are not allowed unless an existing project-approved fetch mechanism already exists for the source. If a new authenticated eSett/NBS integration would be required, STOP or WARN and document the needed manual/source steps instead of adding credentials or a live integration.

If the data is already available through an approved local file/export/process, Codex may ingest it into the local database.

## Required discovery tasks

### 1. Find candidate data sources

Search for tables/files/columns containing:

```text
esett
nbs
mga
metering_grid_area
grid_area
network_area
netområde
nätområde
nätavräkningsområde
consumption
load
profiled
settlement
hourly
15min
quarter_hour
```

Produce an inventory:

```text
source_name
source_type: table/file/script/doc
path_or_table
columns
row_count if accessible
min_timestamp
max_timestamp
countries/areas if present
resolution candidates
settlement-type candidates
```

### 2. Identify MGA masterdata

Try to find or construct:

```text
mga_id
mga_name
country
bidding_zone / price_area
DSO/grid owner if available
valid_from
valid_to
```

For Sweden, count MGA per price area if possible:

```text
SE1
SE2
SE3
SE4
unknown/unmapped
```

If price-area mapping is not directly available, document what is needed to map MGA to SE1-SE4.

### 3. Identify consumption time series

For each candidate MGA consumption source, classify:

```text
mga_id
timestamp_start_utc
timestamp_end_utc or interval end
value
unit
resolution: 15m / 60m / daily / monthly / unknown
settlement_class: monthly_settled / hourly_settled / 15m_settled / profiled / unknown
direction/sign
quality/status flags
version/publication timestamp if present
```

### 4. Detect 60m to 15m transition

For each source and, if feasible, per MGA:

```text
first_timestamp
last_timestamp
observed_time_deltas
share_15m
share_60m
transition_date_candidate
mixed-resolution periods
missing intervals
duplicate intervals
DST anomalies
```

Do not simply resample 15m to hourly before documenting native resolution.

### 5. Separate settlement classes

Explicitly test whether the data contains separate series for:

```text
monthly-settled / profiled consumption
hourly-settled consumption
15-minute-settled consumption
other/unknown settlement
```

If separate series exist, report whether total MGA consumption requires summing classes.

If only one aggregated series exists, document whether it appears to include both settlement classes.

### 6. Load found MGA consumption data into the database

If a credible MGA consumption source is found and can be accessed through approved local/source mechanisms, load data from:

```text
2022-06-01T00:00:00Z onward
```

Required local database tables, unless an equivalent existing schema is found and documented:

```text
esett_mga_consumption_native_v1
esett_mga_masterdata_v1
```

Native consumption table minimum schema:

```text
source_system                  -- e.g. esett/nbs/export/local
source_name                    -- source table/file/feed name
country
mga_id
mga_name nullable
bidding_zone nullable
settlement_class               -- monthly_settled/hourly_settled/15m_settled/profiled/unknown
resolution_minutes             -- 15/60/monthly/etc as numeric or canonical enum
interval_start_utc
interval_end_utc
value
unit                           -- MWh/MW/kWh/etc
value_kind                     -- energy/power/unknown
direction                      -- consumption/load/import/export/unknown, as source defines
quality_status nullable
version_or_publication_time_utc nullable
ingested_at_utc
generated_by_package = P0054W
```

Masterdata table minimum schema:

```text
source_system
mga_id
mga_name nullable
country
bidding_zone nullable
DSO_or_grid_owner nullable
valid_from nullable
valid_to nullable
ingested_at_utc
generated_by_package = P0054W
```

Ingestion requirements:

```text
preserve native 15m/60m/monthly resolution
preserve settlement class
preserve original unit and value kind
do not silently convert energy to power or power to energy
do not merge monthly/profiled and measured series into one row set without settlement_class
be idempotent/upsert-safe if rerun
document primary key/uniqueness strategy
```

Suggested native table uniqueness key:

```text
source_system, source_name, country, mga_id, settlement_class, interval_start_utc, interval_end_utc, resolution_minutes, version_or_publication_time_utc
```

If version/publication time is unavailable, document how duplicate revisions are handled.

### 7. Optional hourly derived view/table for sanity checks

If native data is loaded, Codex may create a derived hourly table/view only for sanity checks and later modeling exploration.

Suggested name:

```text
esett_mga_consumption_hourly_v1
```

Rules:

```text
15m energy -> hourly energy by sum; hourly average MW only if unit/time basis is clear
60m rows -> hourly as-is after unit check
monthly/profiled -> do not allocate to hourly unless source already provides hourly profile allocation
keep settlement_class in output
include aggregation_method
```

Do not let the hourly view replace the native table as source of truth.

### 8. Compare to ENTSO-E SE area totals

If SE3 MGA data can be mapped and loaded, perform a rough volume sanity check against the corrected ENTSO-E area target:

```text
entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
```

For a sample period and, if feasible, full overlap:

```text
sum_mga_consumption_mw_or_mwh
entsoe_se3_consumption_mw_or_mwh
absolute_difference
percent_difference
coverage_ratio
missing_mga_count
known_unmapped_mga_count
```

Do not require exact equality. The goal is to determine whether MGA data is plausible and usable.

### 9. Recommend next modeling granularity

Based on data availability and quality, recommend one of:

```text
A. continue with price-area direct model only
B. test grouped MGA / region clusters first
C. test individual MGA bottom-up model
D. test hierarchical reconciliation: direct SE3 + grouped/MGA bottom-up
E. STOP because MGA consumption source is not available or not trustworthy
```

## Time period of interest

Primary required load period if data is found:

```text
2022-06-01T00:00:00Z onward
```

This aligns with P0054 train/holdout policy.

If MGA data starts later, load the maximum available overlap and document exact start/end and whether it can support post-2025 or future-only tests.

## Resolution handling policy

Native resolution must be preserved in database and evidence.

Allowed derived views for sanity checks:

```text
15m -> hourly energy/average MW with documented aggregation
60m -> hourly direct value with unit check
monthly/profiled -> separate monthly/profiled total, not mixed into hourly unless documented allocation exists
```

Forbidden shortcuts:

```text
silently mixing 15m and 60m rows
silently averaging energy values as power values
silently treating monthly-settled/profiled load as hourly measured load
silently filling missing MGA intervals
assuming all MGA are in SE3 without mapping evidence
loading only hourly aggregates while discarding native 15m/60m/monthly records
```

## Expected evidence files

Create:

```text
requirements/package-runs/P0054W/CHANGELOG.md
requirements/package-runs/P0054W/review.md
requirements/package-runs/P0054W/design.md
requirements/package-runs/P0054W/functions.md
requirements/package-runs/P0054W/labb-label.md
requirements/package-runs/P0054W/source-inventory.md
requirements/package-runs/P0054W/esett-terminology.md
requirements/package-runs/P0054W/mga-masterdata-inventory.md
requirements/package-runs/P0054W/mga-price-area-mapping.md
requirements/package-runs/P0054W/consumption-series-inventory.md
requirements/package-runs/P0054W/settlement-classification.md
requirements/package-runs/P0054W/resolution-transition-analysis.md
requirements/package-runs/P0054W/native-resolution-contract.md
requirements/package-runs/P0054W/database-ingestion-contract.md
requirements/package-runs/P0054W/database-load-evidence.md if data is loaded
requirements/package-runs/P0054W/hourly-aggregation-contract.md if hourly aggregation is tested
requirements/package-runs/P0054W/se3-volume-sanity-check.md if feasible
requirements/package-runs/P0054W/data-quality-review.md
requirements/package-runs/P0054W/leakage-and-use-scope-review.md
requirements/package-runs/P0054W/what-we-learned.md
requirements/package-runs/P0054W/next-package-recommendation.md
```

Optional compact evidence:

```text
source-inventory.json
mga-masterdata-summary.csv
mga-price-area-counts.csv
resolution-transition-summary.csv
settlement-classification-summary.csv
database-load-summary.json
se3-volume-sanity-check.csv
```

Do not commit large raw eSett/NBS datasets, full time-series dumps, credentials, tokens, caches or private extracts.

## Files to inspect

```text
README.md
memory/bootstrap-manifest.json
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
requirements/package-runs/P0054R/target-source-contract.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0054V2/decision.md
src/mac/**
tests/mac/**
docs/functions/mac/**
local DB/table discovery scripts if present
local data inventory docs if present
```

Also inspect any local database/table list commands already used by earlier P0054 packages.

## Files allowed to change

```text
requirements/packages/P0054W-labb-esett-mga-consumption-discovery.md
requirements/package-runs/P0054W/**
src/mac/** narrowly scoped discovery/introspection/ingestion scripts if needed
tests/mac/** narrowly scoped tests for resolution/aggregation/ingestion helpers if code is added
docs/functions/mac/** if durable data-source docs need updating
local database schema/migration files if this repo owns them and only for P0054W tables
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No new external live API integration without explicit approval.
No credentials or tokens.
No large raw data commits.
No final forecasting model training in this package.
No old physical_balance target as ground truth for SE3 consumption.
No silent conversion between 15m/60m/monthly series.
No database table that discards native resolution or settlement class.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
source inventory completed
MGA masterdata search completed
consumption series search completed
settlement class classification attempted
native resolution analysis completed
60m/15m transition search completed
SE3 mapping attempted
database schema created or existing equivalent documented if data found
data from 2022-06-01 onward loaded if approved source found
load row counts and min/max timestamps documented
native resolution and settlement class preserved in DB
SE3 volume sanity check completed or reason documented
no large raw datasets staged
no credentials staged
git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- credible MGA consumption source is found and loaded to local DB from 2022-06-01 onward, or a strong negative result is documented.
- settlement/monthly vs hourly/15m classification is addressed.
- native resolution and 60m/15m transition are addressed.
- MGA-to-price-area mapping is found or the missing mapping is documented.
- if data is loaded, database schema preserves native resolution and settlement class.
- next package recommendation is clear.
```

WARN is acceptable if:

```text
- MGA consumption exists but price-area mapping is incomplete.
- data exists only for part of the desired 2022-06 onward period.
- monthly-settled and measured series cannot yet be separated but evidence is clear.
- SE3 volume sanity check cannot be completed due to missing mapping.
- source can be identified but download requires a manually provided export rather than local automation.
```

STOP if:

```text
- no local/source path exists to inspect eSett/MGA data at all.
- candidate source requires credentials/live integration not approved for this package.
- data cannot be classified enough to avoid mixing settlement classes or resolutions.
- large raw/private data would need to be committed to proceed.
- ingestion would discard native 15m/60m/monthly resolution or settlement class.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
whether eSett/MGA consumption data was found
candidate source/table/file names
whether data was loaded into DB
DB table names and row counts
loaded min/max timestamps
MGA count by price area if available
whether SE3 MGA coverage exists
settlement classes found: monthly/profiled/hourly/15m/unknown
native resolution summary and 60m->15m transition date candidates
SE3 volume sanity check result if feasible
whether data is usable for grouped/MGA forecasting
recommended next package
tests/commands run
files changed
confirmation no credentials, no unauthorized external live API integration, no large raw data committed
```

## Completion notes

To be filled after implementation.
