# P0040 Design

## Package Interpretation

P0040 evaluates short-term 7-day hourly spot forecasts under a realistic level anchor. The model stack supplies shape; the 16 known Monday spot hours set the current level.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0040.py`:

- load P0037 diagnostic rows
- enrich rows with P0038 solar/wind proxy weather fields
- generate Monday forecast origins
- fit static strict pre-backtest components once using P0037 train rows ending `2023-12-31`
- for each origin:
  - require Monday 00-15 known spot hours
  - require a complete 168-hour Monday-start horizon
  - build unanchored variant shapes
  - anchor each variant with mean, median and robust methods from the 16 known hours
  - compute anchored absolute metrics and shape metrics on the 168-hour horizon
- aggregate evidence and write markdown/JSON summaries under `requirements/package-runs/P0040/`

Add `tests/mac/services/spotprice_model_diagnostics/test_p0040.py` for deterministic unit coverage of origins, anchoring, shape metrics and recomposition.

## Variants

Implemented variants:

- `V0_naive_flat_week`
- `V1_M1_shape_only`
- `V2_M1_plus_existing_M3A_M3B`
- `V3_M1_plus_M3A_m1b_M3B_m1b`
- `V4_M1_plus_M3A_m1b_M3B_m1b_plus_M3D`
- `V5_diagnostic_with_M3C`

`V6_diagnostic_with_M4_area_diff` is included when the local scikit-backed P0038-style M4 area diagnostic can be fit. It remains diagnostic only.

## Anchoring Policy

Methods:

- `anchor_16h_mean`
- `anchor_16h_median`
- `anchor_16h_robust`

Each method uses additive calibration:

```text
anchored_price = model_shape_price + (known_anchor_stat - model_known_anchor_stat)
```

Additive anchoring is deterministic and safe for zero or negative prices. The robust method uses median residual between known actuals and model known predictions.

## Evidence Strategy

P0040 writes all required package evidence files plus optional JSON summaries. It does not commit large prediction dumps.

## Test Strategy

Run:

```bash
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0040
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0037 tests.mac.services.spotprice_model_diagnostics.test_p0038 tests.mac.services.spotprice_model_diagnostics.test_p0039 tests.mac.services.spotprice_model_diagnostics.test_p0040
PYTHONDONTWRITEBYTECODE=1 python3 -B -m src.mac.services.spotprice_model_diagnostics.p0040
git diff --check
```

## Design Deviation

The original design considered expanding-window per-origin refits. P0040 uses a static strict pre-backtest fit instead because all primary origins are after `2025-06-01`, while the component fit period ends `2023-12-31` with 2024 used only where an existing diagnostic model requires validation. This avoids horizon leakage and keeps runtime tractable.

## Risks

- Expanding-window refits are slower than static diagnostics.
- Weather is actual historical weather, not provider forecast; all evidence must label it as oracle/proxy.
- P0040 evaluates design readiness only. It does not build a production forecast API.
