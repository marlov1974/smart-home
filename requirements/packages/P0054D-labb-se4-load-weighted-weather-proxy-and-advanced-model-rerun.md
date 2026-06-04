# Package P0054D: LABB SE4 load-weighted weather proxy and advanced model rerun

## Status

done

## Package order

P0054D

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Fix the weak SE4 weather proxy discovered during P0054C review and rerun the SE4 no-price consumption forecast experiment with a load-weighted SE4 weather proxy.

P0054C used the broad `south_connected_weather` proxy. That was acceptable as a WARN LABB proxy, but it is not specific enough for SE4 load behavior. P0054D must build a better proxy from weather locations that represent most of the SE4 household consumption concentration, then reload/rebuild the modeling dataset and compare which model gives the best result.

## Decision summary

Use a three-location SE4 load-weather proxy:

```text
se4_load_weather
```

Initial household-weight basis from operator-provided SE4 load representation:

```text
Malmö:        156000 households
Helsingborg:   71000 households
Lund:          58000 households
Kristianstad:  39000 households
Hässleholm:    24000 households
Landskrona:    22000 households
Trelleborg:    21000 households
Total:        391000 households
```

Aggregate into three proxy weather locations:

```text
Malmö represents Malmö + Lund + Trelleborg:
  households = 235000
  weight = 0.6010

Helsingborg represents Helsingborg + Landskrona:
  households = 93000
  weight = 0.2379

Kristianstad represents Kristianstad + Hässleholm:
  households = 63000
  weight = 0.1611
```

Weights may be stored with more exact precision, but must sum to 1.0 within normal floating tolerance.

## Core question

P0054D must answer:

```text
Was P0054C's HGB win mainly a model-family result, or was it partly caused by a too-broad weather proxy?
```

## Target

Primary target remains:

```text
consumption_se4_mw
```

Use the same canonical physical-balance source used by P0054C unless Codex finds a repository-documented successor:

```text
physical_balance_se1_se4_hourly_v1
```

Unit:

```text
MW hourly mean
```

## Period and split

Use P0053C global policy:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

No target rows before 2022-06-01.

Context-only lag warmup before 2022-06-01 is allowed only if target rows start at or after 2022-06-01 and warmup rows are not scored/trained as targets.

## Weather proxy requirements

Add or compute a new weather proxy group:

```text
se4_load_weather
```

The proxy must use the existing weather-history architecture where possible:

```text
weather_locations / weather_observations / weather_area_hourly
```

or the current equivalent documented by the repository.

Required location names and approximate coordinates:

```text
malmo        55.6050  13.0038  0.6010
helsingborg  56.0465  12.6945  0.2379
kristianstad 56.0294  14.1567  0.1611
```

Codex may adjust coordinates slightly to match the existing weather service conventions or known Open-Meteo point behavior, but must document exact coordinates used.

The proxy must expose the same kind of hourly weather variables used by P0054C/P0054B where available, for example:

```text
temperature_2m
apparent_temperature
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
heating_degree_proxy
cooling_degree_proxy
rapid_temperature_change / temperature deltas if already part of the feature builder
```

Realized/archive weather remains a LABB proxy and must be labeled:

```text
weather_actual_as_forecast_proxy
```

## Feature groups

Rerun at minimum:

```text
G4_calendar_load_lags_rollups_weather_proxy
```

using `se4_load_weather` instead of `south_connected_weather`.

Codex should also keep or report the comparable P0054C baseline if easy and safe:

```text
P0054C G4 with south_connected_weather
P0054D G4 with se4_load_weather
```

If recomputing old P0054C is costly, read the existing P0054C evidence and compare against it, but label the comparison as evidence-summary comparison rather than same-run comparison.

## Forbidden inputs

The model feature matrix must not contain:

```text
spot price
M4 anchored price forecast
actual future spot price
production
future production
export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
continental prices
```

Historical SE4 consumption lags and rollups are allowed only when they are strictly before the forecast origin.

## Models to compare

Required benchmark:

```text
HGB = HistGradientBoostingRegressor
```

Required advanced model from P0054B/P0054C family:

```text
MLP = deterministic sklearn MLPRegressor
```

Additional advanced model required if local dependencies allow it without large new dependency installation:

Preferred order:

```text
1. ExtraTreesRegressor or RandomForestRegressor as a strong nonlinear ensemble baseline
2. A stronger/wider sklearn MLP variant with documented regularization and early stopping
3. GRU/LSTM/TCN only if torch/tensorflow/keras is already locally available
4. LightGBM/XGBoost only if already locally available and dependency-safe
```

The package must not silently install large ML dependencies unless the repository already has an approved local dependency pattern for this lab area. If sequence/deep dependencies are missing, document the blocker and run the strongest dependency-safe model instead.

Minimum model set:

```text
B0-B4 simple baselines
HGB_G4_se4_load_weather
MLP_G4_se4_load_weather
one additional stronger advanced model, dependency-safe
```

Recommended additional model for standard-library/sklearn-only environments:

```text
ExtraTreesRegressor_G4_se4_load_weather
```

because it gives a strong nonlinear comparison without requiring torch/tensorflow/keras.

## Advanced model fairness rules

All model comparisons that claim a winner must use identical rows.

For each model, evidence must include:

```text
model_name
model_type
feature_group
weather_proxy_name
training_rows
validation_rows
holdout_rows
random_seed
hyperparameters
training_duration_seconds
early_stopping_reason if applicable
resource limits if any
```

Do not select hyperparameters on holdout. Validation may be used for model-family/hyperparameter choice inside the package, but the final holdout report must clearly state what was selected before holdout scoring.

## Evaluation

Direct horizons:

```text
1h, 3h, 6h, 12h, 24h, 48h, 72h, 96h, 120h, 144h, 168h
```

Weekly 168h path evaluation on holdout:

```text
weekly origins from 2025-06-01 onward where complete 168h paths exist
```

Required metrics:

```text
MAE
RMSE
bias
median absolute error
p90
p95
sMAPE
MAE percent of mean/median actual
R2 where useful
```

Path metrics:

```text
MAE_0_24h
MAE_24_48h
MAE_48_72h
MAE_72_168h
MAE_full_168h
bias_full_168h
p90/p95 full path
daily energy error proxy
peak load hour error
```

Conditional metrics:

```text
cold hours
very cold hours
rapid temperature drop
weekday
weekend
holiday
morning ramp
evening peak
summer low load
winter high load
```

## Required comparisons

P0054D must report:

```text
1. P0054C weather proxy: south_connected_weather summary
2. P0054D weather proxy: se4_load_weather summary
3. HGB old-vs-new weather comparison where possible
4. MLP old-vs-new weather comparison where possible
5. Best model among HGB, MLP and the additional advanced model
6. Whether the better weather proxy changes the P0054C conclusion
7. Whether a more advanced model beats HGB under the corrected weather proxy
```

Learning threshold:

```text
A corrected proxy or advanced model is interesting if it improves holdout MAE or weekly MAE_full_168h by >= 2%, or improves >= 3% in at least two important conditional regimes.
```

This is a LABB learning threshold, not a production gate.

## Required evidence files

Create:

```text
requirements/package-runs/P0054D/CHANGELOG.md
requirements/package-runs/P0054D/review.md
requirements/package-runs/P0054D/design.md
requirements/package-runs/P0054D/functions.md
requirements/package-runs/P0054D/labb-label.md
requirements/package-runs/P0054D/se4-weather-proxy-design.md
requirements/package-runs/P0054D/se4-weather-proxy-validation.md
requirements/package-runs/P0054D/dataset-contract.md
requirements/package-runs/P0054D/input-classification.md
requirements/package-runs/P0054D/feature-groups.md
requirements/package-runs/P0054D/baseline-results.md
requirements/package-runs/P0054D/hgb-results.md
requirements/package-runs/P0054D/mlp-results.md
requirements/package-runs/P0054D/additional-advanced-model-design.md
requirements/package-runs/P0054D/additional-advanced-model-results.md
requirements/package-runs/P0054D/model-comparison.md
requirements/package-runs/P0054D/direct-horizon-results.md
requirements/package-runs/P0054D/weekly-168h-path-results.md
requirements/package-runs/P0054D/conditional-regime-results.md
requirements/package-runs/P0054D/feature-importance-or-attribution.md
requirements/package-runs/P0054D/interpretation.md
requirements/package-runs/P0054D/what-we-learned.md
requirements/package-runs/P0054D/next-package-recommendation.md
```

Optional compact evidence:

```text
metrics-summary.json
weekly-path-metrics.csv
conditional-metrics.csv
modeling-dataset-sample.csv
advanced-training-history.csv
```

Do not commit large raw datasets or large model binaries.

## Files to inspect

```text
memory/energy-market-ai-lab.md
memory/energy-market-simulator-ambition.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
requirements/packages/P0054C-labb-se4-consumption-advanced-ai-without-price.md
requirements/package-runs/P0054C/CHANGELOG.md
requirements/package-runs/P0054C/review.md
requirements/package-runs/P0054C/dataset-contract.md
requirements/package-runs/P0054C/input-classification.md
requirements/package-runs/P0054C/hgb-vs-advanced-ai-comparison.md
requirements/package-runs/P0054C/what-we-learned.md
relevant local source files for weather-history proxy-group computation
relevant local source files for the P0054C modeling experiment
```

Do not read large raw spot-price/weather data files during package bootstrap unless needed by the package's actual verification commands.

## Files allowed to change

```text
requirements/packages/P0054D-labb-se4-load-weighted-weather-proxy-and-advanced-model-rerun.md
requirements/package-runs/P0054D/**
docs/functions/mac/weather-history-dataset.md
docs/functions/mac/spotprice-model-diagnostics.md
src/mac/services/weather_history/** if needed for proxy configuration/generation
src/mac/** relevant existing LABB modeling scripts if P0054C code is stored there
tests/mac/** relevant tests for changed weather/modeling code
```

If Codex discovers that P0054C was implemented only as local/offline package-run scripts not committed under `src/`, it may create narrowly scoped reusable LABB scripts under an appropriate `src/mac/labs/` or existing equivalent path, but must document the location and avoid broad framework work.

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No price features.
No production/export/import/A61/future-flow features.
No large raw dataset commits.
No model binary commits.
No broad refactor unrelated to P0054D.
```

## Live/API/device policy

Live testing allowed: no.

Device/API/runtime actions allowed: no.

External HTTP weather backfill is allowed only if it is already part of the existing local weather-history service workflow and only for historical weather ingestion needed to compute the new proxy. If Codex uses Open-Meteo through the existing weather service, it must document commands and row coverage. No Shelly, Home Assistant or runtime control endpoint may be touched.

## Test / verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
- weather proxy configuration exists and weights sum to 1.0
- weather proxy rows exist for the modeled period
- target/split validation follows P0053C
- feature matrix contains no forbidden columns
- HGB/MLP/additional advanced model compare on identical rows
- weekly 168h paths are complete or skipped with reason
- no large data/model artifacts are staged
- git diff --check
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- se4_load_weather proxy created or computed with documented weights
- SE4 modeling dataset rebuilt/reloaded with the corrected proxy
- HGB, MLP and one additional advanced model evaluated or an honest dependency-safe substitute documented
- fair identical-row comparison
- direct horizon, weekly path and conditional metrics reported
- clear answer on whether corrected weather changes the P0054C conclusion
```

WARN is acceptable if:

```text
- exact named weather stations are unavailable but coordinates/proxy points are used and documented
- sequence/deep model dependencies are missing, but a stronger dependency-safe model such as ExtraTrees is run
- old P0054C comparison is evidence-summary rather than same-run recomputation
- weather remains actual-as-forecast LABB proxy
```

STOP if:

```text
- weather proxy cannot be computed or validated
- forbidden price/production/flow/A61/future features enter the model matrix
- advanced model is silently skipped
- holdout is used for model selection
- device/API/runtime work is created
```

## Expected Codex output

```text
PASS/WARN/STOP status
se4_load_weather station/coordinate/weight table
weather proxy coverage and validation
input classification summary
model list and training evidence
best model by direct holdout MAE
best model by weekly 168h path MAE
conditional/regime findings
comparison to P0054C
whether better weather changed the conclusion
whether stronger advanced model beat HGB
what we learned
next package recommendation
tests/commands run
files changed
confirmation of no price/API/device/A61/leakage work
commit SHA after push
```

## Completion notes

Implemented and verified by Codex.

Result summary:

```text
status: PASS
label: LABB
weather proxy: se4_load_weather
weather proxy rows: 35064
weather proxy coverage: 2022-05-29T22:00:00Z .. 2026-05-29T21:00:00Z
direct rows: 382106
weekly 168h holdout origins: 51
HGB holdout MAE: 21.821 MW
MLP holdout MAE: 21.651 MW
ExtraTrees holdout MAE: 18.611 MW
best direct holdout model: ExtraTrees_G4_se4_load_weather
best weekly 168h model: ExtraTrees_G4_se4_load_weather
```

P0054D answer:

```text
The broad P0054C weather proxy was a material factor for MLP. With se4_load_weather,
MLP no longer has the broad-weather penalty and slightly beats HGB on direct holdout,
while ExtraTrees beats HGB clearly. The corrected weather changes the P0054C MLP-vs-HGB
picture, but model family still matters because ExtraTrees is the strongest corrected-proxy model.
```

Verification completed:

```text
python3 -m unittest tests.mac.services.weather_history.test_proxy_groups tests.mac.services.spotprice_model_diagnostics.test_p0054d
PYTHONPYCACHEPREFIX=/private/tmp/p0054d-pycache python3 -m py_compile src/mac/services/weather_history/storage.py src/mac/services/spotprice_model_diagnostics/p0054d.py tests/mac/services/weather_history/test_proxy_groups.py tests/mac/services/spotprice_model_diagnostics/test_p0054d.py
PYTHONDONTWRITEBYTECODE=1 python3 -B -m src.mac.services.weather_history backfill --start-date 2022-05-30 --end-date 2026-05-29
PYTHONDONTWRITEBYTECODE=1 python3 -B -m src.mac.services.weather_history validate-proxy-groups --start-date 2022-05-30 --end-date 2026-05-29
PYTHONPYCACHEPREFIX=/private/tmp/p0054d-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0054d
git diff --check --cached
```

No Shelly, Home Assistant, device, runtime, KVS, price-feature, production, export/import, future A09/A11 or A61 utilization work was performed.
