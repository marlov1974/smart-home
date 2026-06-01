# P0045 changelog

- Combined regenerated P0043 AI-2 and P0044 AI-1 predictions into fixed-CET rolling 168h shape diagnostics.
- Applied P0044 fallback policy for weak area_diff scale targets.
- Evaluated scaled and dimensionless combination formulas against B0-B5 baselines.
- Result status: PASS.
- Wrote summary metrics and best/worst JSON; full per-window raw JSON is intentionally not committed because it is large and reproducible.
- No new AI model search, production API, M5/M6/M7, Shelly, Home Assistant, KVS or device action was performed.
