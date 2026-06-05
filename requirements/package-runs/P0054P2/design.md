# P0054P2 Design

## Interpretation

Build and validate canonical ENTSO-E actual-load hourly targets for Swedish bidding zones SE1-SE4 from `2022-06-01T00:00:00Z` onward.

This package is ingestion and validation only. It must not rerun P0054N/P0054O consumption models.

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0054p2.py`.

The module will:

- load the ENTSO-E token through P0052A's token-safe helper.
- fetch actual total load in monthly chunks for SE1-SE4 using sanitized request evidence.
- parse ENTSO-E XML periods and points into timestamped MW observations.
- aggregate subhourly values to hourly mean MW if needed.
- persist rows to `entsoe_consumption_area_hourly_v1`.
- validate schema, source contract, duplicate rows, negative values, missing hours, split coverage, volume sanity and old-source comparison.
- classify any local cross-border physical-flow export as not usable for consumption target if found.
- write compact evidence under `requirements/package-runs/P0054P2/`.

## Table Contract

Preferred canonical table:

```text
entsoe_consumption_area_hourly_v1
```

Columns:

```text
timestamp_utc
area
consumption_mw
source_system
source_measure
source_area_code
resolution
unit
timezone_handling
package_id
ingested_at_utc
quality_flag
```

Primary uniqueness is `(timestamp_utc, area, source_system, source_measure, package_id)`.

## Test Strategy

Add `tests/mac/services/spotprice_model_diagnostics/test_p0054p2.py` for:

- actual-load request params use `A65/A16` and bidding-zone domain, not flow/capacity params.
- XML period parsing and hourly aggregation.
- duplicate/negative quality checks.
- old-source comparison ratio/correlation helper.

Verification commands:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054p2
python3 -m src.mac.services.spotprice_model_diagnostics.p0054p2
git diff --check
```

## Risks And Uncertainties

ENTSO-E may limit date range, return partial coverage, or use a subtly different parameter name for load by bidding zone. The module will keep request evidence sanitized and STOP/WARN honestly if the source cannot be validated.

The operator's SE3 expected values may align better with p75/p95/peak than mean. The evidence must state which statistic matches.
