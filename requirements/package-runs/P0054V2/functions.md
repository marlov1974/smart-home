# P0054V2 functions

Planned module: `src/mac/services/spotprice_model_diagnostics/p0054v2.py`.

## New Functions

`run_p0054v2_analysis(...)`

Orchestrates relaxed baseline gate, stitched price source construction, M1 price-family evaluation, evidence writing and status selection.

`run_baseline_gate(...)`

Runs P0054R in a temporary evidence directory and evaluates P0054V2 relaxed absolute/relative gate.

`relaxed_baseline_passes(...)`

Pure helper for P0054V2 baseline gate logic.

`build_full_contract_rows(...)`

Builds P0054R corrected ENTSO-E SE3 direct/path rows and applies split/profile/internal-validation fields.

`load_actual_se3_spot_prices(...)`

Loads reconstructed actual SE3 spot history from local SQLite through P0054L2/P0054K helpers.

`build_price_forecast_rows(...)`

Creates package-local forecast-safe holdout price predictions for all required P0054R holdout origin/target rows.

`price_history_features_at_origin(...)`

Builds price-model features using only history strictly before origin, without requiring holdout target actual spot.

`build_anchor_features(...)`

Builds the required actual 48h price-history anchor features and source audit.

`attach_basic_stitched_prices(...)`

Assigns actual target-hour spot to train_fit rows and forecast target-hour spot to holdout rows.

`attach_price_feature_families(...)`

Adds P1/P2/P3/P4 price family columns and records coverage/leakage evidence.

`price_family_feature_contract(...)`

Combines P0054R no-price features with each P0054V2 price feature family.

`fit_m1_for_family(...)`

Fits the four base learners, inverse-MAE weighted ensemble and horizon-bias correction for one feature family.

`compare_price_families(...)`

Computes deltas versus P0 and the best broad/daily/full36/regime results.

`decision_summary(...)`

Classifies price as default, conditional-only or excluded using package thresholds.

`write_p0054v2_evidence(...)`

Writes required Markdown, JSON and CSV package evidence.

## Durable Docs

Update `docs/functions/mac/spotprice-model-diagnostics.md` with the final P0054V2 function set and limitations after implementation.
