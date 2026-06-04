# P0053C-B baseline comparison

```json
{
  "holdout": {
    "B0_last48_mean_flat": {
      "baseline_MAE_full_168h": 0.2626585764049244,
      "baseline_top8_day_precision": 0.4395012315270938,
      "selected_minus_baseline_MAE_full_168h": -0.012439330831810425,
      "selected_minus_baseline_top8_day_precision": 0.16789819376026222
    },
    "B1_same_hour_hist48_flat": {
      "baseline_MAE_full_168h": 0.2619192939672274,
      "baseline_top8_day_precision": 0.5115968801313627,
      "selected_minus_baseline_MAE_full_168h": -0.011700048394113427,
      "selected_minus_baseline_top8_day_precision": 0.09580254515599329
    },
    "B2_same_hour_previous_week": {
      "baseline_MAE_full_168h": 0.29474964230124495,
      "baseline_top8_day_precision": 0.49435550082101815,
      "selected_minus_baseline_MAE_full_168h": -0.04453039672813097,
      "selected_minus_baseline_top8_day_precision": 0.11304392446633788
    },
    "B3_train_profile": {
      "baseline_MAE_full_168h": 0.38477121301246936,
      "baseline_top8_day_precision": 0.571172003284072,
      "selected_minus_baseline_MAE_full_168h": -0.13455196743935538,
      "selected_minus_baseline_top8_day_precision": 0.03622742200328399
    }
  },
  "selected_anchor": "A1_median_iqr",
  "validate": {
    "B0_last48_mean_flat": {
      "baseline_MAE_full_168h": 0.21855073199129174,
      "baseline_top8_day_precision": 0.41232638888888873,
      "selected_minus_baseline_MAE_full_168h": -0.03345310200427315,
      "selected_minus_baseline_top8_day_precision": 0.13665674603174593
    },
    "B1_same_hour_hist48_flat": {
      "baseline_MAE_full_168h": 0.221889435557209,
      "baseline_top8_day_precision": 0.4484126984126984,
      "selected_minus_baseline_MAE_full_168h": -0.036791805570190406,
      "selected_minus_baseline_top8_day_precision": 0.10057043650793629
    },
    "B2_same_hour_previous_week": {
      "baseline_MAE_full_168h": 0.25098095692790995,
      "baseline_top8_day_precision": 0.431919642857143,
      "selected_minus_baseline_MAE_full_168h": -0.06588332694089136,
      "selected_minus_baseline_top8_day_precision": 0.11706349206349165
    },
    "B3_train_profile": {
      "baseline_MAE_full_168h": 0.3949995371700507,
      "baseline_top8_day_precision": 0.5282738095238098,
      "selected_minus_baseline_MAE_full_168h": -0.20990190718303212,
      "selected_minus_baseline_top8_day_precision": 0.020709325396824907
    }
  }
}
```
