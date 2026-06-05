# P0054N LABB

Status: `PASS`

```json
{
  "advanced_price_keep": true,
  "best_dayahead_daily_energy_model": {
    "absolute_daily_energy_error_MWh": 3088.67835726033,
    "model": "HGB_no_price"
  },
  "best_dayahead_hourly_model": {
    "hourly_MAE_delivery_day": 149.03724768647368,
    "model": "HGB_no_price"
  },
  "best_full36_model": {
    "MAE_full_36h": 153.69412267688818,
    "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
  },
  "method_candidate_track": "future_G2-KANDIDAT_or_workplace_grade_track_requires_operator_request_and_market_acceptance_criteria",
  "p0054m_comparison": {
    "comparison_label": "indicative: P0054N uses exact 12:00-local origins and full_36h, P0054M weekly evidence used persisted 23:00Z origins and full_168h.",
    "full36_vs_full168_relative_change_percent": -25.484324224333783,
    "p0054m_best_direct_holdout_MAE": 140.54830097681355,
    "p0054m_best_weekly_MAE_full_168h": 206.2574365420684,
    "p0054n_best_with_advanced_price_full36": {
      "MAE_full_36h": 153.69412267688818,
      "model": "HGB_with_p0054n_exact_dayahead_advanced_price"
    }
  }
}
```
