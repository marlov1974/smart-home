# P0040 component attribution summary

Status: WARN
forecast_origin_count = 50

## Required Answers

1. Best anchored absolute 7-day forecast: V0_naive_flat_week with anchor_16h_mean MAE=0.333955.
2. Best 16h anchoring method: anchor_16h_mean for the winning variant.
3. Remaining absolute error after anchoring: MAE=0.333955, RMSE=0.421096.
4. Best weekly shape: V0_naive_flat_week centered-shape MAE=0.287086.
5. Best expensive-hour identification is in `anchored-absolute-results.md` (`weekly_top_10pct_precision`).
6. Best cheap-hour identification is in `anchored-absolute-results.md` (`weekly_bottom_10pct_precision`).
7. P0039 M1B-trained M3A/M3B improves anchored absolute MAE vs existing M3A/M3B: V2=0.365197, V3=0.364194.
8. M3D effect vs V3: -0.010920 MAE.
9. M3C effect vs V3: -0.000022 MAE.
10. M4_area_diff effect vs V3: 0.001625 MAE.
11. The stack is not ready to replace a simple anchored flat-week short-term baseline. Missing work: level-aware shape training, stronger intra-week shape validation and real weather forecast handling. P0040 does not build M5/M6/API and still uses actual weather as an oracle proxy.

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
