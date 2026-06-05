# Findings

## Status

PASS.

P0054P2 loaded ENTSO-E Actual Total Load for SE1, SE2, SE3 and SE4 using:

```text
documentType = A65
processType = A16
area parameter = outBiddingZone_Domain
source_type = actual_total_load
area_scope = bidding_zone_internal_consumption_or_load
usable_for_consumption_target = true
```

Forbidden target sources were not used: no cross-border flow, A09/A11 exchange/flow, A61 capacity, production or price data.

## Canonical Target

Downstream packages should use:

```text
entsoe_consumption_area_hourly_v1
```

with:

```text
timestamp_utc, area, consumption_mw
```

The source is a historical observed target. Future target hours still require a separate forecast model.

## Coverage

Loaded rows by area:

```text
SE1 35001 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
SE2 35026 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
SE3 35125 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
SE4 35023 rows, 2022-06-01T00:00:00Z..2026-06-05T10:00:00Z
```

All areas have train_fit and holdout coverage. Missing-hour counts are documented in `coverage-by-area.md`.

## SE3 Volume

SE3 matches the expected order of magnitude for actual total load:

```text
summer_half_year mean = 8030.544 MW
winter_half_year mean = 10967.240 MW
winter_half_year p75 = 12202.000 MW
winter_half_year p95 = 13959.200 MW
```

The operator's winter expectation of roughly 12-15 GW aligns best with upper-seasonal hours, especially p75/p95, not the all-hour seasonal mean.

## Old Source Comparison

The old `physical_balance_se1_se4_hourly_v1` source is not equivalent to ENTSO-E Actual Total Load:

```text
SE1 ratio entsoe/old = 2.275001, correlation = 0.114140
SE2 ratio entsoe/old = 2.291547, correlation = 0.173880
SE3 ratio entsoe/old = 2.415764, correlation = 0.232260
SE4 ratio entsoe/old = 2.355651, correlation = 0.254001
```

For SE3, ENTSO-E mean over the overlap is 9501.266 MW while the old source mean is 3933.028 MW. This explains the P0054O percent-error discrepancy direction: P0054K-P0054O were measuring a lower proxy target, not validated total SE3 load.

## Downstream Interpretation

P0054K-P0054O should be treated as proxy-target methodology experiments, not validated total-SE3-load forecast experiments.

Recommended next package:

```text
P0054Q LABB SE3 DayAhead full_36h rerun with ENTSO-E actual load target
```
