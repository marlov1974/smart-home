# P0056E Implementation Design

## Package Interpretation

Run a deterministic LABB model-variant test for SE1 and SE2. Compare P0056B-current weather and P0056D Open-Meteo weather, different model families and feature groups, then decide whether any variant beats the best current baseline per area.

## Implementation Structure

Create a new package runner:

```text
src/mac/services/spotprice_model_diagnostics/p0056e.py
```

The runner will:

1. read P0056A targets through P0056C helpers
2. read P0056B weather through P0056C helpers
3. read P0056D weather features for SE1/SE2 from `area_weather_features_hourly_p0056d_v1`
4. build modeling rows with P0056C row semantics
5. apply named feature groups and model variants
6. evaluate holdout DayAhead/full36/daily/regime metrics
7. persist compact P0056E forecast and metric tables
8. write all required P0056E evidence files

## Intended Changes

- Add `p0056e.py`.
- Add `test_p0056e.py`.
- Create/update `requirements/package-runs/P0056E/**`.
- Fill P0056E package completion notes after verification.

## Deliberate Refactoring Decisions

- Do not refactor P0056C/P0056D broadly.
- Reuse P0056C helpers where possible to preserve split and metric behavior.
- Add P0056E-local wrappers for variant metadata, P0056D weather loading and evidence writing.
- Do not run optional reference areas unless primary SE1/SE2 results are complete and runtime remains clearly acceptable.

## Variant Scope

Planned required variants for each area:

- V0 current weather, horizon-bias weighted ensemble
- V1 P0056D weather, horizon-bias weighted ensemble
- V2 P0056D weather, weighted ensemble without horizon correction
- V3 P0056D weather, LightGBM family
- V4 P0056D weather, XGBoost family
- V5 P0056D weather, HGB family
- V6 P0056D weather, lag-heavy feature group
- V7 P0056D weather, weather-heavy feature group
- V8 P0056D weather, simple internal-validation learned regime correction

If a model family is unavailable, mark the variant skipped with reason.

## Test Strategy

Run:

```bash
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056e
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056c tests.mac.services.spotprice_model_diagnostics.test_p0056d tests.mac.services.spotprice_model_diagnostics.test_p0056e
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056e
git diff --check
```

Verification also checks local SQLite row counts for P0056E forecast and metrics tables.

## Risks And Uncertainties

- Some optional ML families may be unavailable in the local environment.
- V8 regime correction must stay strictly inside train_fit/internal validation.
- P0056D weather is historical observed weather proxy, not a production weather forecast.
- Runtime may be significant because each area has multiple variants.
