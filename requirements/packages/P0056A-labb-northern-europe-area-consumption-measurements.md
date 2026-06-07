# Package P0056A: LABB northern Europe area consumption measurements

## Status

planned

## Package order

P0056A

## Label

```text
LABB
```

## Purpose

Load actual consumption measurements from 2022-06-01 onward for northern European bidding zones that affect Swedish prices. This is the measurement layer for the market-emulator consumption forecasts.

This package is data preparation only. Do not train forecast models here.

## Primary area scope

Load actual consumption for:

```text
SE1
SE2
SE3
SE4
NO1
NO2
NO3
NO4
NO5
DK1
DK2
FI
EE
LV
LT
DE_LU
PL
NL
```

Document source-specific area-code mappings, including EIC codes if used. Do not silently drop scoped areas because names differ.

Possible later expansion, not blocking P0056A:

```text
BE
FR
GB
CZ
AT
```

## Source

Preferred source:

```text
ENTSO-E actual total load / actual consumption per bidding zone
```

Use existing local project access or existing local exports/tables. Do not add unrelated integrations. Do not commit large raw exports.

If source access is unavailable, STOP and document exact missing setup.

## Time period

Required period:

```text
2022-06-01T00:00:00Z onward
```

Fetch through latest complete available data.

## Storage

Discover native resolution:

```text
15m
30m
60m
mixed
unknown
```

Preferred tables:

```text
area_consumption_native_v1
area_consumption_hourly_v1
area_consumption_area_catalog_v1
```

If compatible existing tables exist, document and reuse them.

Hourly table must provide:

```text
timestamp_utc
area_code
bidding_zone_code
consumption_mw
source_system
aggregation_method
native_resolution_mix
coverage_flag
input_row_count
ingested_at_utc
generated_by_package = P0056A
```

Native table must preserve:

```text
area_code
interval_start_utc
interval_end_utc
value
unit
value_kind
native_resolution_minutes
source_system
generated_by_package = P0056A
```

Hourly aggregation rules:

```text
energy -> hourly sum and convert to average MW if needed
power/average MW -> time-weighted hourly average
60m -> as-is after unit check
mixed resolution -> preserve resolution metadata
```

## Batch policy

Run by area and time chunk. Write incrementally. Keep completed areas if a later area fails. Make the load rerunnable without duplicate rows.

## Validation

For each area report:

```text
row_count
min_timestamp_utc
max_timestamp_utc
native_resolution
coverage_ratio_since_2022_06_01
missing_intervals
duplicate_intervals
mean_mw
median_mw
p05_mw
p95_mw
min_mw
max_mw
negative_hours_count
zero_hours_count
```

SE3 must be checked against the corrected SE3 target used by earlier packages:

```text
entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
```

Material SE3 mismatch must be explained before downstream modeling.

## Required evidence files

Create:

```text
requirements/package-runs/P0056A/CHANGELOG.md
requirements/package-runs/P0056A/review.md
requirements/package-runs/P0056A/design.md
requirements/package-runs/P0056A/functions.md
requirements/package-runs/P0056A/labb-label.md
requirements/package-runs/P0056A/area-scope.md
requirements/package-runs/P0056A/source-access-review.md
requirements/package-runs/P0056A/area-code-mapping.md
requirements/package-runs/P0056A/native-resolution-review.md
requirements/package-runs/P0056A/database-schema-contract.md
requirements/package-runs/P0056A/ingestion-progress.md
requirements/package-runs/P0056A/database-load-evidence.md
requirements/package-runs/P0056A/hourly-aggregation-contract.md
requirements/package-runs/P0056A/coverage-and-missingness.md
requirements/package-runs/P0056A/volume-sanity-check.md
requirements/package-runs/P0056A/se3-target-consistency-check.md
requirements/package-runs/P0056A/data-quality-review.md
requirements/package-runs/P0056A/modeling-readiness-review.md
requirements/package-runs/P0056A/what-we-learned.md
requirements/package-runs/P0056A/next-package-recommendation.md
```

Optional compact evidence:

```text
area-scope.csv
area-code-mapping.csv
ingestion-summary.json
coverage-summary.csv
volume-sanity-summary.csv
```

Do not commit full measurement dumps or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0054R/target-source-contract.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054T4/inference-noise-summary.json
requirements/package-runs/P0055A/comparison-vs-direct.md
requirements/package-runs/P0055B/stale-after-p0055b2.md
requirements/package-runs/P0055B2/CHANGELOG.md if present
src/mac/** relevant ENTSO-E/data ingestion scripts
tests/mac/** relevant ingestion/aggregation tests
docs/functions/mac/**
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
```

## Files allowed to change

```text
requirements/packages/P0056A-labb-northern-europe-area-consumption-measurements.md
requirements/package-runs/P0056A/**
src/mac/** narrowly scoped measurement ingestion/normalization code if needed
tests/mac/** narrowly scoped tests for area mapping, hourly aggregation, rerunnable loading and sanity checks if code is added
docs/functions/mac/** if durable docs need updating
local database schema/migration files if this repo owns them and only for P0056A tables
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No large raw data commits.
No forecast model training.
No spot price features.
No flow/exchange/A61/capacity as consumption target.
No old physical_balance target.
No silent unit conversion.
No silently dropping scoped areas.
```

## Pass / WARN / STOP

PASS requires:

```text
all primary areas mapped
actual consumption loaded or verified from 2022-06-01 onward
hourly forecast target table populated
coverage and volume sanity documented
SE3 consistency check passes
data ready for multi-area consumption forecast package
```

WARN is acceptable if:

```text
some non-Swedish areas have partial coverage but are documented
native resolution differs by area/time and is handled safely
one area needs follow-up but the rest are loaded
expansion candidates are not loaded
```

STOP if:

```text
source access is unavailable
SE3 cannot be reconciled to corrected target
hourly aggregation cannot be made unit-safe
many primary areas cannot be mapped or loaded
large raw datasets would need to be committed
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
areas loaded/missing
source used
database tables created/used
row counts per area
min/max timestamp per area
coverage per area
native resolution summary
volume sanity summary
SE3 consistency result
recommended next package
tests/commands run
files changed
confirmation no large raw data/no device runtime/no forecast training
```

## Completion notes

Completed as `PASS` in commit package run `P0056A`.

Summary:

```text
areas loaded: 18/18
source: ENTSO-E A65/A16 actual total load
native rows: 1244180
hourly rows: 632871
SE3 consistency vs P0054P2 corrected target: exact overlap match
forecast models trained: no
device/runtime writes: no
large raw committed exports: no
```

Evidence:

```text
requirements/package-runs/P0056A/
```
