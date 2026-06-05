# P0054Q LABB

Status: `PASS`

```json
{
  "best_dayahead_daily_energy_model": {
    "absolute_daily_energy_error_MWh": 12862.665916660333,
    "daily_energy_error_percent_of_actual": 5.28283705993215,
    "day_count": 347,
    "model": "HGB_no_price",
    "signed_daily_energy_error_MWh": -5862.984144686694
  },
  "best_dayahead_hourly_model": {
    "MAE_percent_of_mean_actual": 6.549820972573629,
    "hourly_MAE_delivery_day": 632.7869013389628,
    "model": "LightGBM_no_price"
  },
  "best_full36_model": {
    "MAE_full_36h": 644.9873394113744,
    "MAE_percent_of_mean_actual": 6.585759056659982,
    "model": "LightGBM_no_price"
  },
  "best_with_advanced_price_full36_model": {
    "MAE_full_36h": 671.7222528712044,
    "MAE_percent_of_mean_actual": 6.858740691629407,
    "model": "LightGBM_with_p0054n_exact_dayahead_advanced_price"
  },
  "corrected_target_percent_vs_workplace_reference": {
    "best_dayahead_hourly_percent_of_mean_actual": 6.549820972573629,
    "interpretation": "LABB-only comparison; weather_actual_as_forecast_proxy prevents production claim.",
    "workplace_reference_percent": "3-4"
  },
  "future_method_candidate_basis": false,
  "old_target_reference": {
    "old_target_label": "proxy-target methodology experiment, not validated total-SE3-load performance",
    "p0054n_old_target_best_dayahead_MAE_MW": 149.03724768647368,
    "p0054n_old_target_best_full36_MAE_MW": 150.42261836159255,
    "p0054o_old_target_baseline_percent_of_old_proxy_mean_actual": 6.394256809659218,
    "p0054p2_entsoe_old_correlation": 0.23226,
    "p0054p2_entsoe_over_old_ratio": 2.415764
  },
  "target_sanity": {
    "order_of_magnitude_ok": true,
    "p0054p2_summer_half_year_mean_mw": 8030.544,
    "p0054p2_winter_half_year_mean_mw": 10967.24,
    "se3_daily_energy_mean_gwh_day": 231.86718683957753,
    "se3_dayahead_delivery_day_mean_actual_mw": 9661.132784982383,
    "se3_holdout_mean_actual_mw": 9564.640591488878,
    "se3_holdout_median_actual_mw": 9124.0
  }
}
```
