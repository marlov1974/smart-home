# P0054Q Consistency Review

## Status

WARN.

P0054Q is consistent and implementable, but the final model matrix depends on locally installed optional ML packages. The package allows WARN if one model family fails while key no-price results are available.

## Evidence

P0054P2 completed with PASS and built the canonical target table:

```text
entsoe_consumption_area_hourly_v1
```

Required target source is available:

```text
area = SE3
target_column = consumption_mw
source_type = actual_total_load
area_scope = bidding_zone_internal_consumption_or_load
usable_for_consumption_target = true
```

P0054P2 SE3 sanity:

```text
summer_half_year mean = 8030.544 MW
winter_half_year mean = 10967.240 MW
```

Old source is not equivalent:

```text
old source = physical_balance_se1_se4_hourly_v1.consumption_se3
ENTSO-E / old ratio = 2.415764
correlation = 0.232260
```

## Consistency Result

The package must not use `physical_balance_se1_se4_hourly_v1.consumption_se3` as target. Reusing P0054K/P0054M/P0054N helper functions is acceptable only if the source rows are normalized to the same in-memory field names while retaining P0054Q evidence that the persisted source is ENTSO-E actual load.

No live API calls are required. P0054Q reads local SQLite target, weather and price-history data only.

## Assumptions

- P0054P2 target rows remain in the local feature database.
- Existing weather rows remain labeled `weather_actual_as_forecast_proxy`.
- Existing P0054N exact-origin advanced-price protocol remains the safest local price-feature path.

## Decision

Proceed with code implementation under WARN.
