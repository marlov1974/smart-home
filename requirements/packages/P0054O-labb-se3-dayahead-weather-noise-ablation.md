# Package P0054O: LABB SE3 DayAhead weather noise ablation

## Status

planned

## Package order

P0054O

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Test how much the P0054N SE3 DayAhead/full_36h consumption forecast depends on the optimistic `weather_actual_as_forecast_proxy` assumption by injecting synthetic forecast error into temperature features.

The operator-requested first simulation is:

```text
temperature_degraded = temperature_actual + (random() * 4 - 2)
```

That simulates a weather forecast whose temperature error is uniformly distributed between -2°C and +2°C.

## Business/use-case context

The P0054N best DayAhead result was about:

```text
HGB_no_price DayAhead hourly MAE ≈ 149 MW
```

A workplace production model is reported to have about 3-4% error, but it uses real weather forecasts rather than weather actuals. P0054O must estimate how much P0054N degrades when weather actuals are made less perfect.

This is still LABB only. It does not integrate with workplace systems or Nord Pool.

## Core questions

P0054O must answer:

```text
1. How much does DayAhead hourly MAE worsen when temperature actuals are perturbed by ±2°C uniform noise?
2. How much does full_36h MAE worsen under the same perturbation?
3. Does the best model change when weather is degraded?
4. Does advanced spot-price input become more or less useful when temperature is noisy?
5. What is the MAE percent of mean/median actual load before and after noise?
6. What happens to DayAhead daily energy error percent?
7. Is the result still competitive against the reported 3-4% workplace reference range?
```

## Required split policy

Use the same P0054 train/holdout policy as P0054N:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z

holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

No holdout row may be used for fitting, early stopping, hyperparameter selection, feature selection or model-family selection.

## Target and evaluation framing

Primary target:

```text
consumption_se3_mw
```

Primary evaluation cases:

```text
full_36h
DayAhead delivery day from 12:00 Europe/Stockholm D-1 origin
```

Use P0054N timing semantics:

```text
forecast origin = 12:00 Europe/Stockholm on D-1
delivery day = D 00:00..23:00 Europe/Stockholm
```

## Weather degradation protocol

Identify all temperature-like weather feature columns used by P0054N, for example columns whose names include:

```text
temp
temperature
t2m
```

Do not perturb non-temperature features unless explicitly documented.

For each selected temperature column:

```text
temp_noisy = temp_actual_proxy + uniform(-2.0, +2.0)
```

Equivalent implementation:

```python
temp_noisy = temp_actual_proxy + (rng.random(size) * 4.0 - 2.0)
```

Use deterministic seeded RNG.

Required seeds:

```text
at least 10 seeds, for example 1000..1009
```

Report mean/std/min/max over seeds.

Preferred additional noise scenarios if runtime is practical:

```text
±1°C uniform
±2°C uniform
±3°C uniform
cold_bias_minus_1°C
warm_bias_plus_1°C
```

But the required scenario is ±2°C uniform.

## Important modeling choice

Codex must decide and document whether the weather noise is applied to:

```text
A. holdout/evaluation features only, while models are trained on actual-weather proxy, or
B. both train_fit and holdout features, simulating a model trained and used with noisy weather forecasts.
```

Preferred primary analysis:

```text
B. apply noise consistently to train_fit and holdout for with-weather forecast realism.
```

Also useful as secondary diagnostic:

```text
A. holdout-only noise to isolate sensitivity of already-trained P0054N-style models.
```

Do not silently mix these. Label results clearly.

## Models to evaluate

Minimum:

```text
HGB_no_price
LightGBM_with_advanced_price
XGBoost_no_price
```

Preferred full comparison matching P0054N:

```text
HGB_no_price
HGB_with_advanced_price
ExtraTrees_no_price
ExtraTrees_with_advanced_price
LightGBM_no_price
LightGBM_with_advanced_price
XGBoost_no_price
XGBoost_with_advanced_price
```

If runtime is tight, prioritize:

```text
1. HGB_no_price because it won P0054N DayAhead/full_36h.
2. LightGBM_with_advanced_price because it was the best with-price model.
3. XGBoost_no_price / with-price for comparison to earlier long-horizon behavior.
```

## Price feature policy

Use the same safe advanced price protocol as P0054N if with-price models are run:

```text
exact 12:00-local DayAhead-compatible package-local advanced price forecasts
no P0054L2 holdout-only price rows used as train_fit features
no actual future spot price
```

P0054O is about weather perturbation, not price-model redesign.

## Metrics

Report baseline P0054N no-noise metrics and noisy-weather metrics.

Required full_36h metrics:

```text
MAE_full_36h
RMSE_full_36h
bias_full_36h
p90/p95 absolute error
MAE_percent_of_mean_actual
MAE_percent_of_median_actual
```

Required DayAhead metrics:

```text
hourly_MAE_delivery_day
hourly_RMSE_delivery_day
bias_delivery_day
hourly_MAE_percent_of_mean_actual
hourly_MAE_percent_of_median_actual
absolute_daily_energy_error_MWh
signed_daily_energy_error_MWh
daily_energy_error_percent_of_actual
peak_hour_error_MW
peak_hour_timing_error_hours
morning_ramp_MAE
evening_peak_MAE
```

Required regime metrics:

```text
cold_hours
very_cold_hours
weekday
weekend
holiday
morning_ramp
evening_peak
high forecast price
low forecast price
forecast price spike
large forecast price ramp
```

## Required comparisons

P0054O must report:

```text
1. P0054N baseline best DayAhead MAE and percent-of-load.
2. P0054N baseline best full_36h MAE and percent-of-load.
3. Noisy ±2°C DayAhead MAE distribution across seeds.
4. Noisy ±2°C full_36h MAE distribution across seeds.
5. Delta MW and delta percent vs P0054N baseline.
6. Which model is most robust to temperature noise.
7. Whether advanced price features become more useful under noisy weather.
8. Whether degraded model remains near or below 3-4% error.
```

## Leakage and realism restrictions

Allowed:

```text
synthetic noise added to weather actual proxy for LABB sensitivity analysis
local SQLite reads/writes
local deterministic Python computation
package-run evidence
```

Forbidden:

```text
actual future spot price leakage
actual future load leakage
production/export/import/A61/future-flow features
live weather API calls
live market API calls
Nord Pool/workplace integration
Shelly/Home Assistant/device/runtime actions
production deployment
G2-KANDIDAT promotion
large raw dataset/model binary/venv/cache commits
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054O/CHANGELOG.md
requirements/package-runs/P0054O/review.md
requirements/package-runs/P0054O/design.md
requirements/package-runs/P0054O/functions.md
requirements/package-runs/P0054O/labb-label.md
requirements/package-runs/P0054O/weather-noise-protocol.md
requirements/package-runs/P0054O/temperature-feature-discovery.md
requirements/package-runs/P0054O/split-policy-applied.md
requirements/package-runs/P0054O/dataset-contract.md
requirements/package-runs/P0054O/price-feature-protocol-review.md
requirements/package-runs/P0054O/model-training-evidence.md
requirements/package-runs/P0054O/full-36h-weather-noise-results.md
requirements/package-runs/P0054O/dayahead-weather-noise-results.md
requirements/package-runs/P0054O/percent-error-results.md
requirements/package-runs/P0054O/daily-energy-error-results.md
requirements/package-runs/P0054O/advanced-price-under-weather-noise.md
requirements/package-runs/P0054O/conditional-regime-results.md
requirements/package-runs/P0054O/leakage-review.md
requirements/package-runs/P0054O/interpretation.md
requirements/package-runs/P0054O/what-we-learned.md
requirements/package-runs/P0054O/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
seed-metrics.csv
percent-error-summary.json
daily-energy-error-summary.csv
```

Do not commit large raw datasets, model binaries, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054N/CHANGELOG.md
requirements/package-runs/P0054N/full-36h-results.md
requirements/package-runs/P0054N/dayahead-delivery-day-results.md
requirements/package-runs/P0054N/advanced-price-ablation-36h.md
requirements/package-runs/P0054N/model-comparison.md
requirements/package-runs/P0054N/leakage-review.md
requirements/package-runs/P0054M/model-comparison.md
requirements/package-runs/P0054M/leakage-review.md
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files for P0054N modeling/evaluation
```

Do not read large raw data files during bootstrap unless required by verification/modeling commands.

## Files allowed to change

```text
requirements/packages/P0054O-labb-se3-dayahead-weather-noise-ablation.md
requirements/package-runs/P0054O/**
docs/functions/mac/weather-history-dataset.md if durable docs need updating
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** relevant existing LABB weather-noise/evaluation scripts if needed
tests/mac/** relevant tests for deterministic noise and percent metrics if code changes are made
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
P0054 split applied
temperature feature columns discovered and documented
noise is deterministic per seed
noise range is within [-2, +2] °C for required scenario
weather actual proxy baseline is preserved for comparison
no actual future price/load/flow/A61 features enter the matrix
DayAhead 12:00 D-1 timing remains correct
full_36h paths complete or skipped with reason
percent metrics computed against actual SE3 load mean/median/daily energy
git diff --check
no large data/model/env artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- ±2°C uniform temperature-noise ablation is completed.
- at least the key P0054N winner model is evaluated.
- DayAhead and full_36h degradation are reported in MW and percent.
- daily energy error percent is reported.
- leakage review passes.
```

WARN is acceptable if:

```text
- fewer than all P0054N model families are rerun but key models are covered.
- only ±2°C is run and optional ±1/±3/bias scenarios are skipped.
- train+holdout noise is too expensive and holdout-only sensitivity is clearly labeled.
```

STOP if:

```text
- temperature features cannot be identified.
- noise cannot be applied deterministically and safely.
- DayAhead/full_36h evaluation cannot be reproduced.
- actual future spot/load leakage is introduced.
- live API/device/Nord Pool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
weather noise protocol used
model families run
baseline percent error
±2°C noisy percent error
delta MW and delta percent
full_36h degradation
DayAhead degradation
daily energy error percent
most robust model
whether advanced price helps under noisy weather
comparison to 3-4% workplace reference range
leakage review result
what we learned
next package recommendation
tests/commands run
files changed
confirmation no live API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
commit SHA after push
```

## Completion notes

To be filled after implementation.
