# P0055A implementation design

## Package interpretation

Build a LABB comparison between:

- direct SE3 corrected ENTSO-E total load forecast,
- profiled/load-profile cluster forecasts,
- calculated metered/non_profiled residual forecast,
- aggregated decomposition total forecast,
- optional train-fit-only reconciled direct/decomposition ensemble.

The question is whether component decomposition improves total SE3 consumption forecast accuracy versus the latest best direct SE3 method.

## Implementation structure

Create one package-scoped module:

```text
src/mac/services/spotprice_model_diagnostics/p0055a.py
```

Create focused tests:

```text
tests/mac/services/spotprice_model_diagnostics/test_p0055a.py
```

The module will reuse P0054R/P0054Q/P0054K helpers where possible:

- P0054R model fitting, inverse-MAE weights and horizon-bias correction.
- P0054Q/P0054N DayAhead/full_36h selectors and metrics.
- P0054K calendar, lag, rolling and matrix helpers.

## Intended changes

- Load direct SE3 target rows from `entsoe_consumption_area_hourly_v1`.
- Load P0054Y2 cluster and residual targets.
- Load P0054Z weather features by climate zone.
- Build per-component origin/target modeling rows for 36h paths.
- Train the P0054R-style no-price ensemble per non-zero component.
- Use explicit zero forecast for zero-history clusters.
- Use simple same-hour previous-week fallback if full model training fails for a sparse component.
- Aggregate component predictions into decomposition total rows.
- Compare direct and decomposition totals on DayAhead and full_36h holdout.
- Learn optional reconciliation weights only from internal validation rows and apply them to holdout.
- Write compact package evidence and CSV/JSON summaries.

## Deliberate limits

- No spot-price features.
- No old `physical_balance` target.
- No flow/exchange/A61/capacity features.
- No external weather/API integration.
- No model binaries or full prediction dumps committed.
- No Shelly/Home Assistant/device/runtime changes.

## Test strategy

Unit tests will cover:

- cluster-to-weather-zone mapping,
- zero-history cluster handling,
- decomposition aggregation equals sum of component forecasts,
- reconciliation weights learned without holdout rows,
- leakage review rejects forbidden feature names.

Verification commands:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0055a
PYTHONPYCACHEPREFIX=/private/tmp/p0055a-pycache python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0055a.py tests/mac/services/spotprice_model_diagnostics/test_p0055a.py
PYTHONPYCACHEPREFIX=/private/tmp/p0055a-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0055a
git diff --check
```

## Risks and uncertainties

- Full per-component model training may be moderately expensive; the module checkpoints by component and uses safe fallbacks.
- Cluster targets represent only the public profiled/load-profile share, while residual is calculated as the unobserved rest.
- Weather is actual-as-forecast proxy and therefore LABB-only.
- Direct P0054R baseline may not reproduce exactly if local input tables have gained newer rows; comparison will use the same current dataset for direct and decomposition.
