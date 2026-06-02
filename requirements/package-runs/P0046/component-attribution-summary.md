# P0046 component attribution summary

Status: PASS
1. P0045 SE1 shape source used: P0045 system_proxy_se1 selected formula combined_scaled.
2. Forecast-origin policy: Monday 06:00 fixed-CET model time; 168 consecutive fixed-CET hours; validation=2025 origins, holdout=2026 origins.
3. Anchor scenarios tested: (11, 16, 24, 35).
4. Selected anchoring formula: {'target_series': 'system_proxy_se1', 'predictor': 'P0045_combined_scaled', 'anchor_method': 'L2_level_scale', 'anchor_count': 35, 'selection_split': 'validate'}.
5. Validation selected MAE=0.153460, B0_anchor_flat MAE=0.212950.
6. Holdout selected MAE=0.267128, B0_anchor_flat MAE=0.382517.
7. Rank/top-bottom and optimization metrics are reported in dedicated evidence files.
8. Worst windows are reported in `best-worst-windows.md`.
9. P0047 should be SE1-only and non-production if it proceeds.
10. area_diff/recomposed SE3 remains diagnostic only.
11. Confirmed: no production API, no AI retraining, no M5/M6/M7 and no device actions.
