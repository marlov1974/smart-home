# P0056P Implementation Design

## Package Interpretation

P0056P verifies whether the SE2 `2026-03-28` extreme consumption target exists in fresh/original ENTSO-E Actual Total Load source data and whether local native/hourly storage and aggregation are consistent with that source.

Primary question:

```text
Is the 7279 MW / extreme-load spike a local ingestion/cache/aggregation bug, a source-observed ENTSO-E anomaly, a plausible real regime, or unresolved?
```

This package is LABB/source-audit only.

## P0056N Baseline

P0056N found:

- `classification = probable_target_source_anomaly`
- hourly mean actual around `5487.6 MW`
- native mean around `5505.8 MW`
- top hourly spike around `7279 MW`
- local native rows for `2026-03-28`: 94 observed 15-minute rows vs 96 expected
- two partial hourly rows
- neighboring days around 1800..2200 MW

P0056O fixed a separate DST row-generation bug and did not change this anomaly classification.

## ENTSO-E Request Contract

Use the existing P0056A/P0054P2 Actual Total Load contract:

```text
documentType = A65
processType = A16
outBiddingZone_Domain = SE2 EIC
SE2 EIC = 10Y1001A1001A45N
periodStart / periodEnd = UTC ENTSO-E timestamps
```

No A09/A11/A61/flow/exchange/capacity/production/price parameters are used.

## Source Window

Primary local date window:

```text
2026-03-27..2026-03-30 Europe/Stockholm
```

The implementation converts the inclusive local date window to an exclusive UTC interval:

```text
start = 2026-03-27 local midnight
end = 2026-03-31 local midnight
```

The implementation may support command-line date arguments, defaulting to the package values.

## Fresh Source Fetch Plan

The module reads the ENTSO-E token through the existing approved P0052A helper path, verifies secret safety, builds sanitized request metadata, performs one Actual Total Load request for SE2 over the UTC source window, parses XML into native rows, and discards the raw payload.

If ENTSO-E returns acknowledgement/no data/network error, the module records sanitized failure evidence and classifies as unresolved unless a sufficiently original source is otherwise available.

## Local Native Read Plan

Read from:

```text
area_consumption_native_v1
```

Filter:

```text
generated_by_package = P0056A
area_code = SE2
interval_start_utc in source window
local_date in requested local dates
```

The audit records expected/observed row counts, duplicate timestamps, missing 15-minute timestamps for normal local days, min/max/mean MW, and spike presence.

## Local Hourly Read Plan

Read from:

```text
area_consumption_hourly_v1
```

Filter:

```text
generated_by_package = P0056A
area_code = SE2
timestamp_utc in source window
local_date in requested local dates
```

Optionally also read `entsoe_consumption_area_hourly_v1` for reference if present, but the primary comparison is fresh native source -> local P0056A hourly.

## Aggregation Comparison Method

The fresh/native rows are aggregated to hourly mean MW by UTC hour using all native rows within each UTC hour. Local rows already include `input_row_count` and coverage flags; these are preserved in comparison evidence.

Comparison fields include:

- timestamp UTC and local timestamp
- fresh aggregated MW
- local hourly MW
- absolute difference
- fresh input row count
- local input row count
- local coverage flag

Tolerance:

```text
0.001 MW
```

Differences above tolerance are flagged.

## Decision Classification Logic

The module emits exactly one primary classification:

```text
verified_local_bug
source_observed_anomaly
independently_plausible_real_regime
unresolved_exclude_from_selection
```

P0056P has no independent non-ENTSO-E source, so it cannot classify `independently_plausible_real_regime` unless a future package provides that source.

Expected decisions:

- fresh lacks spike while local has spike -> `verified_local_bug`
- fresh has spike and local matches -> `source_observed_anomaly`
- fetch/source unavailable -> `unresolved_exclude_from_selection`

Model-selection action:

- source-observed anomaly: `exclude_until_independently_verified`
- local bug: `fix_local_ingestion_before_modeling`
- unresolved: `exclude_until_source_verified`

## Token And Secret Safety

- Token is read only from the existing approved token helper.
- Token value is never printed.
- Evidence includes only token source class/safety booleans and sanitized request metadata.
- Evidence files are scanned for token-like fields by unit tests and manual review.

## Evidence Plan

Write compact evidence only:

```text
CHANGELOG.md
source-contract.md
fresh-entsoe-fetch.md
local-native-comparison.md
hourly-aggregation-comparison.md
decision.md
what-we-learned.md
next-package-recommendation.md
metrics-summary.json
se2-2026-03-28-native-comparison.csv
se2-2026-03-28-hourly-comparison.csv
```

No raw XML dumps are written.

## Test Strategy

Unit tests cover:

- request contract is Actual Total Load only
- SE2 EIC is correct
- XML parser handles native rows and resolutions
- hourly aggregation uses mean MW and reports input row count
- classification table
- evidence writer does not include forbidden token fields

Verification command:

```bash
python3 -m unittest discover tests/mac
python3 -m src.mac.services.spotprice_model_diagnostics.p0056p --area SE2 --start-local-date 2026-03-27 --end-local-date 2026-03-30 --write-evidence requirements/package-runs/P0056P
git diff --check
```

## Risks And Uncertainties

- ENTSO-E can revise historical values or return different native resolution than local P0056A. This is the core audit target and must be reported, not normalized away.
- Fresh API fetch may be blocked by network. That yields WARN/STOP according to package rules, not fabricated evidence.
- The package cannot independently verify whether ENTSO-E's source-observed spike is a real physical regime. That requires a later independent-source package.
