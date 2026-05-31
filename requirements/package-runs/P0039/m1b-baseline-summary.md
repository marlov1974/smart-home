# P0039 M1B baseline summary

train_rows_total = 13945
train_rows_included_for_M1B = 12817
train_rows_excluded_for_M1B = 1128

M1B uses the same week/weekday/hour robust median surface style as M1, fitted only on holiday-clean train rows.

# P0039 full-year holdout results

| holdout_year | variant | target | MAE | RMSE | signed_error | MAE_delta_vs_M1 | MAE_delta_vs_previous_variant |
|---:|---|---|---:|---:|---:|---:|---:|
| 2025 | M1 | system_proxy_se1 | 0.371326 | 0.474105 | 0.286880 | 0.000000 | 0.000000 |
| 2025 | M1 | area_diff_proxy_se3 | 0.324620 | 0.488786 | -0.218774 | 0.000000 | 0.000000 |
| 2025 | M1 | recomposed_se3 | 0.384666 | 0.521048 | 0.068106 | 0.000000 | 0.000000 |
| 2025 | M1B | system_proxy_se1 | 0.395991 | 0.518789 | 0.314199 | 0.024664 | 0.024664 |
| 2025 | M1B | area_diff_proxy_se3 | 0.327647 | 0.493348 | -0.196476 | 0.003027 | 0.003027 |
| 2025 | M1B | recomposed_se3 | 0.422423 | 0.587098 | 0.117723 | 0.037758 | 0.037758 |
