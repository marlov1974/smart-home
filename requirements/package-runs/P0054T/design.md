# P0054T Implementation Design

Status: `planned-before-code`

## Interpretation

P0054T runs a controlled LABB matrix for corrected-target SE3 consumption forecasting:

```text
3 consumption variants x 2 weather modes x 2 price modes = 12 summarized combinations
```

W1 weather noise uses deterministic seeds `1000..1004`. Each W1 combination reports mean/std/min/max across seeds.

## Implementation Structure

- Add `src/mac/services/spotprice_model_diagnostics/p0054t.py`.
- Reuse P0054Q target loading, P0054N exact-origin price reconstruction, P0054M/P0054K row construction, and P0054R ensemble/correction helpers where practical.
- Add P0054T-specific weather-noise, price/no-price feature selection, matrix orchestration, seed aggregation and evidence writing.
- Add `tests/mac/services/spotprice_model_diagnostics/test_p0054t.py`.
- Update durable function catalog in `docs/functions/mac/spotprice-model-diagnostics.md`.

## Dataset

Rows are exact-origin DayAhead/full_36h rows with:

- target from `entsoe_consumption_area_hourly_v1.consumption_mw`, area `SE3`;
- forecast origin 12:00 Europe/Stockholm D-1;
- horizon convention `horizon_h 1..36`;
- train/holdout split by target timestamp;
- price branch using P0054L2-compatible exact-origin reconstruction and path features;
- weather proxy label preserved.

## Matrix Execution

For each weather/price dataset:

- train base models on train_fit only;
- learn weighted ensemble weights on internal validation only;
- apply weighted ensemble and horizon-bias correction;
- evaluate:
  - `M1_HorizonBiasCorrectedWeightedEnsemble`;
  - `M2_WeightedEnsemble`;
  - `M3_XGBoost`.

Weather modes:

- `W0_weatherProxy`: no noise;
- `W1_tempNoise2C`: train_fit and holdout temperature-like weather columns receive deterministic uniform noise in `[-2,+2]` per seed.

Price modes:

- `P0_noPrice`: no price forecast features;
- `P1_p0054l2Price`: P0054L2-compatible exact-origin price path features.

## Runtime Choices

Use the minimum required five W1 seeds (`1000..1004`) to keep runtime bounded. Run combinations serially and write compact checkpoint evidence.

## Risks

- Price features may hurt corrected-target consumption, as P0054Q found.
- W1 retraining is expensive but more faithful than holdout-only sensitivity.
- Weather noise only perturbs temperature-like proxy features, not full forecast realism.
- P0054L2-compatible exact-origin price rows are package-local forecast-safe reconstruction, not a persisted rolling train-period downstream source.

## Verification Commands

```text
/usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054t
/usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054t
git diff --check
git status --short --branch
```
