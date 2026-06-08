# P0056G Implementation Design

## Package Interpretation

P0056G builds a LABB weekly walk-forward consumption emulator for SE1, SE2, SE3 and FI. Each simulated forecast origin is Monday 06:00 Europe/Stockholm. Training data is limited to target timestamps at or before the preceding Sunday 24:00 local. The delivery week is Monday 00:00 through Sunday 23:00 local.

The package reports both:

- `full_week_168h`: Monday 00:00 through Sunday 23:00, including Monday 00:00-05:00 as nowcast/backcast hours.
- `forward_162h`: Monday 06:00 through Sunday 23:00, pure forward hours from forecast origin.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0056g.py` with:

- weekly calendar generation in Europe/Stockholm
- area input loading from existing P0056A/P0056B/P0056D tables
- weekly feature row construction for horizons 1..168
- per-job progress logging and checkpoint resume artifacts
- deterministic weekly HGB no-price fit
- weekly and aggregate metrics
- structural-change diagnostics
- DB tables for compact P0056G forecast and metrics outputs
- evidence writer for all required P0056G files

Add tests under `tests/mac/test_p0056g_weekly_walk_forward.py` for weekly windows, leakage ordering and metric behavior.

## Intended Model Variants

- `A_static_baseline`: committed static baseline evidence per area.
- `B_weekly_HGB_no_price`: weekly retrain using HGB, P0056 feature family, no price/flow/A61/capacity features.
- SE1/SE2 use P0056D weather where available.
- SE3 uses P0056B weather.
- FI uses P0056D weather because P0056D explicitly retuned FI weather.

This is deliberately narrower than full P0056C/P0056E/P0056F weighted ensembles because the full weekly ensemble matrix is too expensive for the first walk-forward package. The evidence remains LABB/WARN.

## Refactoring Decisions

No broad refactor. The package reuses P0056C feature builders and P0054K feature matrix/model helpers where possible, while owning weekly origin logic locally because existing helpers create daily 36h origins.

## Test Strategy

Run:

```bash
python3 -m unittest tests.mac.test_p0056g_weekly_walk_forward
PYTHONPYCACHEPREFIX=/private/tmp/p0056g-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056g
git diff --check
git status --short
```

Verification covers:

- forecast origins and delivery windows
- training cutoff before forecast origin
- no future target/load leakage in train rows
- actual-weather proxy labeling
- checkpoint/job status completion
- weekly metrics and comparison to static baselines
- no forbidden feature names

## Risks And Uncertainty

- The weekly retrain model is a tractable P0056 no-price HGB model, not the complete static-best weighted ensemble. This limits direct method equivalence and keeps status at `WARN`.
- Actual weather proxy is not production forecast weather.
- Static baseline comparison uses committed static aggregate evidence, while weekly retrain is evaluated week-by-week on the same target period.
