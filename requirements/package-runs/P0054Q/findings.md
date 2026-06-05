# Findings

## Status

PASS.

P0054Q produced corrected-target SE3 DayAhead/full_36h LABB metrics using P0054P2 ENTSO-E Actual Total Load.

## Target

```text
table = entsoe_consumption_area_hourly_v1
area = SE3
target_column = consumption_mw
source_type = actual_total_load
area_scope = bidding_zone_internal_consumption_or_load
```

The old `physical_balance_se1_se4_hourly_v1.consumption_se3` target was not used.

## Best Models

Best full_36h:

```text
LightGBM_no_price
MAE_full_36h = 644.987 MW
MAE_percent_of_mean_actual = 6.586%
```

Best DayAhead hourly MAE:

```text
LightGBM_no_price
hourly_MAE_delivery_day = 632.787 MW
MAE_percent_of_mean_actual = 6.550%
```

Best DayAhead daily energy:

```text
HGB_no_price
absolute_daily_energy_error_MWh = 12862.666
daily_energy_error_percent_of_actual = 5.283%
```

## Advanced Price

Advanced price did not help overall on the corrected target. It worsened HGB, LightGBM and XGBoost on full_36h and DayAhead hourly MAE. ExtraTrees had only a small full_36h improvement and worse DayAhead MAE.

## Interpretation

The corrected-target result is around 6.55% hourly DayAhead MAE of mean actual load, above the 3-4% workplace reference.

This is still LABB evidence because weather remains `weather_actual_as_forecast_proxy`; it is not production DayAhead performance.

## Next

Recommended next package:

```text
P0054R LABB SE3 DayAhead weather realism on ENTSO-E target
```
