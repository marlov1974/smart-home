# Package P0056L: LABB SE2 neural DayAhead smoke test

## Status

planned

## Package order

P0056L

## Label

```text
LABB
```

## Purpose

Test whether neural network models can improve SE2 consumption forecasting under the realistic DayAhead protocol established in P0056K.

This is a narrow smoke test for SE2 only. The goal is not to build a complete neural production stack, but to see if neural models show enough upside to justify a larger package.

## Area in scope

```text
SE2
```

Do not run all 18 areas in this package.

## Baseline to beat

Use P0056K realistic DayAhead SE2 results as the primary baseline.

Reference values:

```text
SE2 best P0056K model: M6 WeightedEnsemble_no_price
DayAhead hourly MAE: 232.692807 MW
MAE percent of mean actual: 12.832409 %
```

Also compare against:

```text
P0056K M7 HorizonBiasCorrected_WeightedEnsemble_no_price: 233.948043 MW
P0056K M4 LightGBM: 233.753054 MW
P0056K M3 ExtraTrees/RandomForest-style: 233.092459 MW
```

If local evidence differs, use latest committed P0056K evidence and document the exact baseline.

## Forecast protocol

Use exactly the realistic DayAhead protocol from P0056K:

```text
forecast_origin = D-1 12:00 Europe/Stockholm
delivery_day = D 00:00 through D 23:00 Europe/Stockholm
```

For every forecast origin, train/fit only on rows available before that origin. No future actual consumption may enter features or labels before the target row.

## Input data

Use existing prepared data:

```text
area_consumption_hourly_v1
area_weather_features_hourly_v1
P0056D/P0056F SE2 weather variant if selected by P0056K setup
```

Weather protocol must match P0056K unless a difference is explicitly documented.

No spot price, flow, exchange, A61/capacity, or old physical_balance features in this package.

## Feature protocol

Use the same forecast-safe feature protocol as P0056K where possible:

```text
calendar/time
holiday/weekend
known load history at forecast origin
forecast-safe lag strategy
weather proxy features
```

Do not use row-wise actual lag features from the old static test.

For neural sequence models, build input windows only from data available at forecast origin.

## Neural model candidates

Test at minimum:

### N1 Tabular MLP

A small feed-forward neural network trained on the same tabular features as P0056K.

Suggested constraints:

```text
standardized numeric features
small architecture first
early stopping
dropout or weight decay
fixed random seed
```

### N2 Sequence MLP / flattened history window

A simple model using a fixed lookback window of historical SE2 load plus known calendar/weather features for the delivery horizon.

Suggested lookbacks:

```text
168h
336h if practical
```

### N3 TCN or 1D CNN sequence model if dependencies allow

A lightweight temporal convolution model. Skip with documented reason if dependencies are unavailable.

### N4 N-BEATS/N-HiTS style model if dependencies allow

Only run if already supported locally. Do not add heavy new dependencies just for this package.

## Non-neural control

Re-run or import the P0056K SE2 M6 and M7 results in the same result table so the neural results are easy to compare.

## Dependency policy

Use existing local Python packages if available.

Allowed frameworks:

```text
PyTorch if installed
scikit-learn MLPRegressor if PyTorch is unavailable
existing project-approved neural/time-series libraries if already present
```

Do not require CUDA/GPU. CPU run is acceptable.

If no neural framework is available, run scikit-learn MLPRegressor as minimum neural smoke test and document limitations.

Do not commit virtualenvs, model binaries, checkpoints, tensorboard logs, or large artifacts.

## Training policy

Use forecast-safe training for each origin or a documented rolling/expanding training protocol matching P0056K.

For speed, Codex may start with a reduced but representative origin subset, but final PASS requires enough origins to compare to P0056K fairly.

If a reduced smoke subset is used, status must be WARN and the exact subset must be documented.

## Metrics

Report for every neural model:

```text
origin_count
delivery_day_count
DayAhead hourly MAE
DayAhead RMSE
DayAhead bias
MAE percent of mean actual
MAE percent of median actual
absolute daily energy error MWh
signed daily energy error MWh
daily energy error percent of actual
p90 absolute error
p95 absolute error
weekday/weekend split
monthly split
train seconds per origin/model
predict seconds
```

Also report stability:

```text
random_seed
number of failed origins
number of NaN predictions
early-stopping behavior
train/validation loss trend if available
```

## Decision rules

A neural model is worth expanding if it improves SE2 P0056K M6 by:

```text
DayAhead hourly MAE >= 2 percent relative
or daily energy error >= 5 percent relative without worsening DayAhead MAE by more than 1 percent
```

If no neural model improves by at least 2 percent, recommend keeping P0056K M6/M7 as baseline and only revisit neural models when a larger multi-area/global neural setup is planned.

## Required evidence files

Create:

```text
requirements/package-runs/P0056L/CHANGELOG.md
requirements/package-runs/P0056L/review.md
requirements/package-runs/P0056L/design.md
requirements/package-runs/P0056L/functions.md
requirements/package-runs/P0056L/labb-label.md
requirements/package-runs/P0056L/p0056k-baseline-review.md
requirements/package-runs/P0056L/dayahead-protocol.md
requirements/package-runs/P0056L/input-source-contract.md
requirements/package-runs/P0056L/feature-protocol.md
requirements/package-runs/P0056L/neural-dependency-review.md
requirements/package-runs/P0056L/model-contract.md
requirements/package-runs/P0056L/training-policy.md
requirements/package-runs/P0056L/progress-log.md
requirements/package-runs/P0056L/job-status.md
requirements/package-runs/P0056L/area-model-results.md
requirements/package-runs/P0056L/comparison-vs-p0056k.md
requirements/package-runs/P0056L/stability-review.md
requirements/package-runs/P0056L/leakage-review.md
requirements/package-runs/P0056L/decision.md
requirements/package-runs/P0056L/what-we-learned.md
requirements/package-runs/P0056L/next-package-recommendation.md
```

Optional compact evidence:

```text
area-model-results.csv
comparison-vs-p0056k.csv
metrics-summary.json
job-status.csv
```

Do not commit model checkpoints, neural weights, full prediction dumps, caches or large artifacts.

## Files to inspect

```text
requirements/package-runs/P0056K/model-ranking.md
requirements/package-runs/P0056K/area-model-results.md
requirements/package-runs/P0056K/dayahead-protocol.md
requirements/package-runs/P0056K/lag-protocol.md
requirements/package-runs/P0056K/leakage-review.md
src/mac/** forecast/model/feature/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
```

## Files allowed to change

```text
requirements/packages/P0056L-labb-se2-neural-dayahead-smoke-test.md
requirements/package-runs/P0056L/**
src/mac/** narrowly scoped neural DayAhead smoke-test code if needed
tests/mac/** narrowly scoped neural/feature/leakage tests if code is added
local DB metrics tables if repo owns them and only for P0056L outputs
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No spot price features in this package.
No flow/exchange/A61/capacity features.
No old physical_balance target.
No future actual load in primary features.
No old static row-wise actual lag protocol.
No large neural/model artifacts committed.
```

## Pass / WARN / STOP

PASS requires:

```text
SE2 realistic DayAhead neural smoke test runs
at least one neural model completes on a fair origin set
comparison vs P0056K M6/M7 is reported
leakage review passes
clear decision on whether neural models are worth expanding
```

WARN is acceptable if:

```text
only MLP is available
TCN/N-BEATS/N-HiTS are skipped due to dependencies
reduced representative origin subset is used
neural models do not beat baseline
```

STOP if:

```text
no neural model can be run at all
realistic DayAhead protocol cannot be reproduced
future actual load leakage is found
input data is missing for SE2
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
neural frameworks available
models tested
origin count
SE2 neural metrics
comparison vs P0056K M6/M7
whether any neural model clears improvement threshold
runtime summary
tests/commands run
files changed
confirmation no forbidden features/no large artifacts/no device runtime changes
```

## Completion notes

To be filled after implementation.
