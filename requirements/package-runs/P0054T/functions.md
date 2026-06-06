# P0054T Function Design

Status: `planned-before-code`

## New Module

`src.mac.services.spotprice_model_diagnostics.p0054t`

## Intended New Functions

`run_p0054t_analysis(...)`

- Orchestrates dataset build, matrix execution, aggregation and evidence writing.

`build_p0054t_rows(...)`

- Builds corrected-target exact-origin rows with P0054L2-compatible price path features.

`temperature_noise_columns(rows)`

- Returns the weather proxy temperature columns eligible for +/-2C noise.

`apply_temperature_noise(rows, seed, columns)`

- Applies deterministic uniform noise in `[-2,+2]` to train_fit and holdout rows.

`prepare_matrix_rows(base_rows, weather_mode, price_mode, seed)`

- Copies base rows, applies weather mode, assigns splits/internal splits and train profiles.

`feature_contract_for_price_mode(price_mode)`

- Returns P0054R/P0054Q no-price or with-price feature names and classifications.

`fit_base_models_for_matrix(rows, features, specs)`

- Trains XGBoost plus ensemble source models on train_fit and internal validation.

`score_matrix_variant(rows, path_rows, model_key, prediction_column)`

- Produces full_36h, DayAhead and daily-energy metrics for one matrix variant.

`run_matrix_combination(...)`

- Runs one model/weather/price/seed combination and returns compact evidence.

`aggregate_matrix_results(results)`

- Aggregates W0 deterministic and W1 seed mean/std/min/max into the required 12-combination summary.

`price_delta_summary(summary_rows)`

- Computes with-price minus no-price deltas under same model/weather mode.

`weather_delta_summary(summary_rows)`

- Computes noisy minus proxy deltas under same model/price mode.

`robustness_ranking(summary_rows)`

- Ranks combinations by noisy mean MAE and variability.

`validate_p0054t_leakage(...)`

- Confirms corrected target, price alignment, weather noise bounds, no forbidden feature names and no holdout tuning.

`write_p0054t_evidence(...)`

- Writes required Markdown/JSON/CSV package evidence.

## Changed Functions

`docs/functions/mac/spotprice-model-diagnostics.md`

- Add current P0054T function catalog section after implementation.

## Removed Functions

None.
