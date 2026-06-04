# P0054K Implementation Design

## Package Interpretation

P0054K copies the P0054J LABB modeling workflow from SE1 to SE3 and adds an upstream Phase A forecast-safe SE3 price forecast log. The result is package evidence, not a deployable/runtime model.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0054k.py
tests/mac/services/spotprice_model_diagnostics/test_p0054k.py
```

Update after implementation:

```text
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054K-labb-se3-consumption-spotprice-forecast-ai.md
```

## Phase A: SE3 Price Forecast Log

The local source has SE1 absolute price and SE3-SE1 area-difference rows, not a direct SE3 absolute series. P0054K will reconstruct:

```text
se3_absolute_price = system_proxy_se1.hour_price + area_diff_proxy_se3.hour_price
```

Then it will apply the P0054H origin-local history baseline:

```text
previous_week_same_hour_else_hist48_same_hour_else_hist48_median
```

The persisted table will be:

```text
anchored_absolute_price_forecast_log_p0054k_se3_v1
```

Rows will be daily complete 168h paths from the modeling start where:

```text
input_data_cutoff_utc = forecast_origin_timestamp_utc - 1h
anchor window = [origin - 48h, origin - 1h]
prediction source timestamp, when present, is strictly before origin
target timestamp is at or after origin
```

Phase A must pass leakage and coverage checks before Phase B runs.

## Phase B: SE3 Consumption Ablation

Reuse the P0054J modeling shape with SE3 substitutions:

```text
target: physical_balance_se1_se4_hourly_v1.consumption_se3
weather proxy: weather_area_hourly area_proxy=se3_load_weather
price forecast source: anchored_absolute_price_forecast_log_p0054k_se3_v1
variant A: no_price
variant B: with_p0054k_se3_price_forecast
```

Each model family must use identical target rows for the paired no-price vs with-price comparison.

## Deliberate Refactoring Decisions

No broad refactor of P0054J or P0054H. P0054K may duplicate/adapt package-local LABB code because the package is an evidence-producing experiment and the goal is to keep P0054J stable.

No model artifacts will be persisted.

## Test Strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054k
python3 -m src.mac.services.spotprice_model_diagnostics.p0054k
git diff --check
```

The unit tests will cover:

- SE3 price reconstruction from SE1 absolute plus SE3-SE1 diff.
- P0054K leakage validation rejects source timestamps at or after origin.
- Feature contract excludes forbidden leakage feature names.
- `with_p0054k_se3_price_forecast` uses the P0054K price variant naming.

Runtime verification will cover:

- P0054I/P0054J train_fit/holdout split applied.
- SE3 price forecast table exists and covers train_fit and holdout.
- SE3 target source verified.
- Paired no-price/with-price rows identical per model.
- Feature matrix contains no future actual price, production, flow/export/import or A61 features.
- Weekly 168h paths are complete.
- No large artifacts are staged.

## Risks and Uncertainties

- SE3 absolute price is reconstructed, not directly sourced. This is acceptable for LABB when explicitly documented.
- Weather remains actual-as-forecast proxy and cannot support production claims.
- MLP may be skipped because it is optional and the required tree/boosted family set is sufficient.
- Phase A output quality may be weaker than true M4/rolling-origin models; it is used only for forecast-safe ablation.
