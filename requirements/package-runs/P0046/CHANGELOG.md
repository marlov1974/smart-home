# P0046 changelog

- Built SE1-first anchored absolute-price backtest for P0045 `combined_scaled` 168h shape.
- Tested Monday 06:00 fixed-CET origins with A11/A16/A24/A35 anchors and L1/L2/L3 deterministic anchoring.
- Compared flat, last-known, time-profile, AI1-only, AI2-only and oracle diagnostics.
- Result status: PASS.
- Selected SE1 configuration: {'target_series': 'system_proxy_se1', 'predictor': 'P0045_combined_scaled', 'anchor_method': 'L2_level_scale', 'anchor_count': 35, 'selection_split': 'validate'}.
- Wrote aggregate JSON and best/worst JSON; full per-window raw JSON is intentionally not committed because it is large and reproducible.
- No AI retraining, production API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
