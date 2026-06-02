# Package P0047: SE3-SE1 bottleneck data export and model design

## Status

planned

## Package order

P0047

## Primary area

G2 / Mac tooling / spotprice V2 / SE3-SE1 spread diagnostics / bottleneck model design / data export

## Decision summary

P0047 pauses the SE3 anchoring/API path and investigates `SE3-SE1` as a separate bottleneck/spread problem.

Do **not** anchor SE1 forecasts against SE3 in P0047.

Current decision:

```text
SE1 path:
  P0046 showed SE1 shape + anchoring works.

SE3 path:
  not ready for API.
  Do not force SE3 = SE1 + free SE3-SE1 model yet.
  Do not anchor SE1 shape to SE3 yet.

SE3-SE1 path:
  treat as possible bottleneck/regime model, not just a normal price-shape model.
```

P0047 must export and analyze the last year of hourly `SE3-SE1` spread data so humans can inspect the real series and decide what kind of bottleneck model is appropriate.

## Why this package exists

Prior packages showed:

```text
- SE1 is learnable with the AI-1/AI-2 shape approach.
- SE3-SE1 has some rank signal but unstable scale/shape behavior.
- area_diff targets became trainable only after robust scale correction.
- combined area_diff shape still harms some MAE/scale metrics.
```

This suggests `SE3-SE1` may not be best modeled as a regular continuous price-shape target.

It may need a model that answers questions like:

```text
- Is there a bottleneck regime now?
- Is SE3 decoupled from SE1?
- How large is the spread likely to be?
- Is the spread positive/negative/near zero?
- Are spikes clustered in particular weather/import/export regimes?
- Is this a classification + severity problem rather than pure regression?
```

## Scope

P0047 owns:

```text
1. Export last-year hourly SE3-SE1 data for inspection.
2. Create human-readable plots/tables/summaries of spread behavior.
3. Attribute spread behavior to available signals.
4. Identify candidate bottleneck/regime target definitions.
5. Recommend the next SE3-SE1 model design.
```

P0047 must not train a new production model. Small diagnostic classifiers/regressions are allowed only if clearly labeled exploratory and not selected as deployable.

## Data window

Primary export window:

```text
last complete year available in local dataset
```

If the latest complete 12-month period is not clear, Codex must document the chosen range.

Preferred examples:

```text
2025-01-01 .. 2025-12-31
```

or:

```text
latest 365 complete fixed-CET model days ending before the latest complete day
```

The export must use the fixed-CET time model established in P0042:

```text
timestamp_utc = primary timestamp
model_cet_timestamp = timestamp_utc + 1h
model_cet_date
model_cet_hour
```

## Required exported dataset

Create a repository-safe sample/export artifact under package-run evidence.

Required file:

```text
requirements/package-runs/P0047/se3-se1-last-year-export.csv
```

If the full CSV is too large for the repository, create:

```text
requirements/package-runs/P0047/se3-se1-last-year-export.sample.csv
```

and document the local full export path and regeneration command.

Required columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
se1_price
se3_price
se3_minus_se1
abs_se3_minus_se1
spread_sign
spread_regime
```

Required weather/signal columns if available:

```text
temperature_se1_or_system_actual
temperature_se3_or_south_actual
temperature_south_minus_north
solar_se1_or_system_actual
solar_se3_or_south_actual
solar_south_minus_north
wind_system_proxy
wind_south_proxy
wind_central_proxy
wind_north_proxy
wind_south_minus_north
wind_central_minus_north
```

Required calendar columns:

```text
model_cet_weekday
model_cet_day_of_year
base_day_type
special_day_type
special_day_name
is_special_day
is_bridge_day
is_holiday_period
is_major_social_holiday
```

If some fields are unavailable, P0047 must document exactly which fields are missing and why.

## Spread regime definitions

P0047 must propose and compute several candidate regime labels.

Minimum required labels:

```text
spread_near_zero:
  abs(SE3-SE1) <= small_threshold

spread_positive:
  SE3-SE1 > positive_threshold

spread_negative:
  SE3-SE1 < negative_threshold

spread_spike_positive:
  SE3-SE1 >= high_positive_threshold

spread_spike_negative:
  SE3-SE1 <= high_negative_threshold
```

Thresholds must be data-driven and documented.

Required candidate threshold strategies:

```text
T1_fixed_ore_or_currency_thresholds
T2_quantile_thresholds
T3_robust_sigma_thresholds based on median/MAD/IQR
```

P0047 must recommend one threshold strategy for future modeling.

## Required analysis

P0047 must analyze at least:

```text
- distribution of SE3-SE1 hourly spread
- distribution by model_cet_hour
- distribution by weekday
- distribution by month/season
- distribution by special-day category
- persistence/autocorrelation of spread regimes
- run lengths of positive/negative/near-zero regimes
- spike clustering
- transition matrix between regimes
- relation to wind proxies and wind gradients
- relation to solar proxies and solar gradients
- relation to temperature gradients
- relation to SE1 price level and SE3 price level
- relation to price volatility
```

Important: distinguish between:

```text
normal spread behavior
bottleneck/stress regimes
rare spikes
```

## Required visual evidence

Create plot files if repository conventions allow small images. Otherwise create tables and document local plot paths.

Suggested outputs:

```text
requirements/package-runs/P0047/plots/se3-se1-timeseries-last-year.png
requirements/package-runs/P0047/plots/se3-se1-histogram.png
requirements/package-runs/P0047/plots/se3-se1-by-hour.png
requirements/package-runs/P0047/plots/se3-se1-by-month.png
requirements/package-runs/P0047/plots/se3-se1-vs-wind-gradient.png
requirements/package-runs/P0047/plots/se3-se1-regime-runs.png
```

Do not commit very large images.

## Candidate model designs to evaluate conceptually

P0047 must recommend future modeling architecture among at least these options:

### Option A: constrained continuous spread regression

```text
Predict continuous SE3-SE1 but constrain amplitude/scale.
```

### Option B: two-stage bottleneck model

```text
Stage 1: classify regime: near-zero / positive bottleneck / negative bottleneck / spike.
Stage 2: predict severity conditional on non-zero regime.
```

### Option C: quantile/risk model

```text
Predict spread quantiles or probability of high spread, not just mean spread.
```

### Option D: direct SE3 model

```text
Build SE3 as its own target using the SE1-style AI-1/AI-2 architecture but with SE3/south/gradient weather signals.
```

### Option E: hybrid

```text
SE3 direct model for main forecast + bottleneck model as risk adjustment/diagnostic.
```

P0047 must not assume the answer before looking at data.

## Exploratory diagnostics allowed

P0047 may run lightweight exploratory models only for diagnosis:

```text
- logistic classifier for high spread regime
- decision tree / shallow gradient boosting for regime classification
- simple regression for non-zero severity
- feature importance / permutation importance
```

If run, these must be labeled:

```text
exploratory only, not deployable
```

No model artifact from P0047 may be treated as production-ready.

## Required evidence files

P0047 must create:

```text
requirements/package-runs/P0047/CHANGELOG.md
requirements/package-runs/P0047/review.md
requirements/package-runs/P0047/design.md
requirements/package-runs/P0047/functions.md
requirements/package-runs/P0047/dataset-contract.md
requirements/package-runs/P0047/export-summary.md
requirements/package-runs/P0047/se3-se1-last-year-export.csv or .sample.csv
requirements/package-runs/P0047/spread-distribution.md
requirements/package-runs/P0047/spread-regime-definitions.md
requirements/package-runs/P0047/regime-persistence-and-transitions.md
requirements/package-runs/P0047/weather-signal-attribution.md
requirements/package-runs/P0047/calendar-signal-attribution.md
requirements/package-runs/P0047/spike-and-outlier-review.md
requirements/package-runs/P0047/candidate-model-designs.md
requirements/package-runs/P0047/next-package-recommendation.md
requirements/package-runs/P0047/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0047/se3-se1-last-year-summary.json
requirements/package-runs/P0047/regime-transition-matrix.json
requirements/package-runs/P0047/top-spike-hours.csv
requirements/package-runs/P0047/regime-run-lengths.csv
```

## Required answers

P0047 must explicitly answer:

```text
1. What exact last-year window was exported?
2. How many hourly rows are included?
3. What are min/p01/p05/median/mean/p95/p99/max for SE3-SE1?
4. How often is SE3-SE1 near zero?
5. How often is SE3-SE1 strongly positive or strongly negative?
6. Are spread spikes isolated or persistent?
7. What is the typical run length of bottleneck regimes?
8. Which available weather signals correlate with spread regimes?
9. Are wind gradients more useful than absolute wind proxies?
10. Are solar or temperature gradients meaningful?
11. Are special days relevant for spread regimes?
12. Is SE3-SE1 better framed as regression, classification+severity, quantile/risk, or direct SE3 modeling?
13. Should the next package build a bottleneck model or a direct SE3 AI-1/AI-2 model?
14. Confirm no SE1-to-SE3 anchoring test, no SE3 API, no production model, no device actions.
```

## Tests

Required automated tests:

```text
- export uses timestamp_utc and fixed-CET derived fields
- exported SE3-SE1 equals se3_price - se1_price
- no SE1 shape is anchored to SE3 in P0047
- no production forecast API is created
- no AI-1/AI-2 retraining for SE1 is performed
- no deployable SE3-SE1 model artifact is created
- regime thresholds are documented and reproducible
- missing signal columns are explicitly documented
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- last-year SE3-SE1 export exists or sample+regeneration command exists
- spread distribution and regimes are documented
- weather/calendar attribution is documented
- candidate bottleneck model designs are compared
- next package recommendation is explicit
- no forbidden anchoring/API/device/model-production work is done
```

WARN is acceptable if:

```text
- some weather proxy fields are missing but documented
- plots are only local and tables are committed instead
- exploratory models are inconclusive but data export is good
```

STOP if:

```text
- SE3-SE1 cannot be reconstructed reliably
- timestamp/time model is ambiguous
- Codex accidentally anchors SE1 to SE3
- Codex builds a production forecast/API path
- evidence does not contain inspectable spread data
```

## Non-goals

- No SE1-shape-to-SE3 anchoring.
- No SE3 production forecast.
- No production API.
- No Home Assistant integration.
- No Shelly runtime changes.
- No Shelly deploy.
- No KVS writes.
- No optimizer/control changes.
- No AI-1/AI-2 retraining for SE1.
- No deployable SE3-SE1 model training.
- No M5 forecast-time temperature model.
- No M6 forecast API.
- No M7 futures/absolute long-term model.
- No futures/forward ingestion.
- No live device access.

## Expected Codex output

- PASS/WARN/STOP status
- export window and row count
- path to export/sample and regeneration command
- spread distribution summary
- regime threshold definitions
- persistence/transition summary
- weather/calendar attribution summary
- top spike examples
- recommended next model architecture for SE3-SE1
- whether direct SE3 model should be preferred over spread model
- tests run
- files changed
- no SE1-to-SE3 anchoring / no API / no device confirmation
- commit SHA after push

## Completion notes

To be filled after implementation.
