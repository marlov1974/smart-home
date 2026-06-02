# Package P0048: SE3-SE1 bottleneck feature foundation and exploratory two-stage model

## Status

verified

## Package order

P0048

## Primary area

G2 / Mac tooling / spotprice V2 / SE3-SE1 spread / bottleneck-regime modeling / weather-gradient features

## Decision summary

P0048 is the next package after P0047.

P0047 showed that `SE3-SE1` should not yet be treated as a normal price-shape series and should not be used for SE1-to-SE3 anchoring/API work.

P0048 must build the missing bottleneck feature foundation and run exploratory, non-deployable two-stage modeling for `SE3-SE1`:

```text
Stage 1: classify bottleneck/spread regime.
Stage 2: predict spread severity conditional on non-zero/bottleneck regime.
```

P0048 must not build a production SE3 forecast and must not anchor SE1 to SE3.

## Preconditions

P0048 may start only after P0047 PASS evidence exists.

Required P0047 facts:

```text
- last complete year SE3-SE1 export exists
- 2025 export had 8760 hourly rows
- SE3-SE1 is mostly positive, rarely negative
- near-zero share is meaningful
- positive bottleneck/spike regimes are persistent
- requested south/north/central gradient weather fields were missing from the AI2 v2 table
- recommended next design is bottleneck classification + severity, then compare to direct SE3 modeling later
```

P0048 must STOP if it cannot reconstruct `SE3-SE1 = SE3 - SE1` reliably.

## Scope

P0048 owns:

```text
1. Add/derive missing weather-gradient features needed for SE3-SE1 bottleneck analysis.
2. Build a bottleneck-modeling dataset for SE3-SE1.
3. Define regime targets from P0047 robust-sigma thresholds or improved documented thresholds.
4. Train exploratory Stage-1 regime classifiers.
5. Train exploratory Stage-2 severity regressors conditional on non-zero/positive/spike regimes.
6. Compare against simple baselines and constrained continuous spread regression.
7. Decide whether bottleneck modeling is promising enough for a later deployable package.
```

P0048 must not produce a deployable model artifact.

## Non-goals and hard prohibitions

P0048 must not:

```text
- anchor SE1 shape to SE3
- build SE3 forecast API
- build production SE3 forecast
- retrain SE1 AI-1/AI-2 as part of the SE1 product path
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Exploratory model files/configs may be stored as evidence only. They must be explicitly labeled:

```text
exploratory only, not deployable
```

## Time model

Use the P0042 fixed-CET convention:

```text
timestamp_utc = primary time identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

Do not reintroduce Europe/Stockholm DST day-length artifacts as primary keys.

## Required feature foundation

P0048 must search existing source tables and create/derive the missing fields requested in P0047 where possible.

Required weather/proxy feature families:

```text
wind_south_proxy
wind_central_proxy
wind_north_proxy
wind_system_proxy
wind_south_minus_north
wind_central_minus_north
wind_south_minus_system
wind_north_minus_system

solar_south_proxy
solar_north_proxy
solar_system_proxy
solar_south_minus_north
solar_south_minus_system
solar_north_minus_system

temperature_south_proxy
temperature_north_proxy
temperature_system_proxy
temperature_south_minus_north
temperature_south_minus_system
temperature_north_minus_system
```

Recommended geographic mapping, unless existing project conventions define better mappings:

```text
south/SE3-oriented weather:
  Malmö, Kalmar, Kristinehamn

central transition/bottleneck weather:
  Ånge, Härnösand

north/SE1-oriented weather:
  Piteå
```

If a city/source is unavailable, Codex must document the omission and choose the closest available proxy.

## Weather normal and anomaly features

For every available weather proxy, P0048 should create actual, normal and anomaly fields where practical:

```text
proxy_actual
proxy_normal
proxy_delta = actual - normal
proxy_delta_rank_in_day if hourly
proxy_delta_rank_in_local_7d if daily/window-based
```

Use P0042 fixed-CET M2-normal logic when possible.

If normal/anomaly is not feasible in P0048, document why and at least provide actual and gradient actuals.

## Dataset

Create a modeling dataset for at least the last complete year from P0047 and preferably all available history if safe.

Required table/view or documented local artifact:

```text
se3_se1_bottleneck_training_dataset_v1
```

Required columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
model_cet_weekday
model_cet_day_of_year
model_cet_hour_sin
model_cet_hour_cos
model_cet_day_of_year_sin
model_cet_day_of_year_cos

se1_price
se3_price
se3_minus_se1
abs_se3_minus_se1
spread_sign
spread_regime
is_near_zero
is_positive_bottleneck
is_positive_spike
is_negative_bottleneck
is_negative_spike
spread_severity_positive
spread_severity_abs

calendar/special-day features
weather/proxy actual features
weather/proxy normal/anomaly features if available
weather gradient features
lagged regime/spread diagnostic columns if allowed and non-leaky for backtest setup
```

Lagged target-derived features may be included only if they use past timestamps relative to prediction time and are clearly marked. For initial exploratory models, train/evaluate both:

```text
without_lagged_spread_features
with_lagged_spread_features
```

This matters because bottleneck regimes are persistent.

## Regime labels

P0048 must start from P0047 selected strategy:

```text
T3_robust_sigma_thresholds
near_zero_abs = 0.050000
positive = 0.201919
negative = -0.201919
spike_positive = 0.807675
spike_negative = -0.807675
```

Codex may propose adjusted thresholds if the larger/all-history dataset materially changes quantiles/robust sigma. Any adjustment must be documented and compared against P0047 thresholds.

Minimum Stage-1 classification targets:

```text
binary_positive_bottleneck:
  se3_minus_se1 >= positive_threshold

binary_positive_spike:
  se3_minus_se1 >= spike_positive_threshold

multiclass_regime:
  near_zero / small_nonzero / positive / spike_positive / negative_or_spike_negative
```

Given P0047 found negative regimes are rare, P0048 may merge negative and negative-spike into one rare class for multiclass modeling, but must document counts.

## Stage 1 exploratory classifiers

Train and evaluate exploratory classifiers, at least:

```text
C0_time_calendar_baseline
C1_time_calendar_weather_actual
C2_time_calendar_weather_gradient
C3_time_calendar_weather_anomaly_gradient
C4_with_lagged_spread_features_diagnostic
```

Candidate model classes:

```text
LogisticRegression or calibrated linear classifier
RandomForestClassifier or HistGradientBoostingClassifier
shallow DecisionTreeClassifier for interpretability
```

Use conservative complexity. No neural nets, transformers, AutoML or heavy external dependencies.

## Stage 2 exploratory severity regressors

Conditional on positive bottleneck / spike-relevant rows, train severity models:

```text
severity_target_1 = se3_minus_se1 for rows above positive threshold
severity_target_2 = log(max(se3_minus_se1, epsilon)) for rows above positive threshold
severity_target_3 = excess_spread = se3_minus_se1 - positive_threshold
```

Evaluate at least:

```text
R0_median_or_regime_mean_baseline
R1_time_calendar_baseline
R2_weather_gradient_regressor
R3_weather_anomaly_gradient_regressor
R4_with_lagged_spread_features_diagnostic
```

Candidate model classes:

```text
HistGradientBoostingRegressor
RandomForestRegressor
HuberRegressor or robust linear baseline
QuantileRegressor if available
```

## Continuous spread regression baseline

P0048 must also train/evaluate a constrained continuous spread baseline:

```text
predict se3_minus_se1 directly
```

Compare it to the two-stage approach.

It must include guardrails:

```text
- non-finite predictions forbidden
- extreme predictions clipped or bounded for diagnostics
- evaluate MAE/RMSE and spike/rank usefulness
```

## Splits and leakage control

Use chronological splits.

Recommended:

```text
train: earliest available .. 2024-12-31
validate: 2025-01-01 .. 2025-12-31
holdout: 2026-01-01 .. latest complete timestamp
```

If P0048 only has 2025 last-year export available, then use rolling/month-based chronological cross-validation within 2025 and document limitations.

No random shuffle as the primary evaluation.

Leakage rules:

```text
- no future spread/prices as features
- lagged spread features must use only timestamps before prediction timestamp
- weather actuals are acceptable in exploratory analysis as proxy forecast weather, but must be labeled proxy-forecast-known
- calendar features are allowed
```

## Metrics

Stage 1 classification metrics:

```text
precision
recall
F1
ROC-AUC if applicable
PR-AUC for positive/spike classes
confusion matrix
calibration curve or reliability table
false positive/false negative review for spike regimes
```

Stage 2 severity metrics:

```text
MAE
RMSE
median_absolute_error
p90_absolute_error
p95_absolute_error
bias
rank correlation within positive-regime rows
```

Two-stage combined diagnostics:

```text
expected_spread = P(regime) * predicted_severity or documented formula
continuous reconstructed spread MAE/RMSE
spike detection + severity combined score
cheap/expensive impact if translated to SE3 adjustment diagnostics
```

Compare against:

```text
- time/calendar profile baseline
- regime persistence baseline
- continuous spread regression baseline
- naive previous-hour spread baseline where lagged features are allowed
```

## Feature attribution

P0048 must report which feature families matter:

```text
time/calendar
special days
absolute wind
wind gradients
solar gradients
temperature gradients
weather anomalies
lagged spread/regime persistence
SE1 price level
```

Use at least one of:

```text
permutation importance
model feature importance
ablation comparison
simple correlation/regime mean tables
```

The answer must explicitly state whether gradient weather improved over system-only weather.

## Required evidence files

P0048 must create:

```text
requirements/package-runs/P0048/CHANGELOG.md
requirements/package-runs/P0048/review.md
requirements/package-runs/P0048/design.md
requirements/package-runs/P0048/functions.md
requirements/package-runs/P0048/dataset-contract.md
requirements/package-runs/P0048/feature-foundation.md
requirements/package-runs/P0048/missing-feature-report.md
requirements/package-runs/P0048/regime-labels.md
requirements/package-runs/P0048/training-split.md
requirements/package-runs/P0048/stage1-classification-results.md
requirements/package-runs/P0048/stage2-severity-results.md
requirements/package-runs/P0048/continuous-spread-baseline-results.md
requirements/package-runs/P0048/two-stage-combined-diagnostics.md
requirements/package-runs/P0048/feature-attribution.md
requirements/package-runs/P0048/calibration-and-error-review.md
requirements/package-runs/P0048/spike-case-review.md
requirements/package-runs/P0048/next-package-recommendation.md
requirements/package-runs/P0048/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0048/metrics-summary.json
requirements/package-runs/P0048/confusion-matrices.json
requirements/package-runs/P0048/feature-importance.json
requirements/package-runs/P0048/spike-error-cases.csv
requirements/package-runs/P0048/modeling-dataset-sample.csv
```

Do not commit large generated datasets or model binaries.

## Required answers

P0048 must explicitly answer:

```text
1. Which weather-gradient features were successfully created?
2. Which requested features remain missing and why?
3. What time window and row counts were used for modeling?
4. What regime thresholds were used?
5. How imbalanced are the regime classes?
6. Can Stage 1 predict positive bottleneck regimes better than time/calendar baseline?
7. Can Stage 1 predict spike regimes with useful recall/precision?
8. Does adding wind/solar/temp gradients improve Stage 1?
9. Does adding lagged spread/regime features help materially?
10. Can Stage 2 predict severity better than regime-mean baseline?
11. Is two-stage classification+severity better than constrained continuous spread regression?
12. Is SE3-SE1 promising enough as a bottleneck adjustment path?
13. Should the next package build direct SE3 AI-1/AI-2, a deployable bottleneck model, or compare both?
14. Confirm no SE1-to-SE3 anchoring, no API, no production model, no device actions.
```

## Tests

Required automated tests:

```text
- SE3-SE1 equals se3_price - se1_price in the modeling dataset
- timestamp_utc and fixed-CET fields are present
- requested gradient feature formulas are reproducible
- missing features are documented
- regime labels match documented thresholds
- chronological splits are non-overlapping
- lagged features, if used, never reference current/future spread
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- bottleneck feature foundation is materially improved over P0047
- regime labels and class balance are documented
- Stage 1 and Stage 2 exploratory models are evaluated
- continuous spread baseline is evaluated
- next architecture recommendation is explicit
- forbidden anchoring/API/device work is not done
```

WARN is acceptable if:

```text
- some requested gradient features remain missing but are documented
- Stage 1 can predict positive bottleneck but not rare spikes
- Stage 2 severity remains noisy but better than naive baseline
- two-stage model is promising but not deployable
```

STOP if:

```text
- SE3-SE1 cannot be reconstructed reliably
- gradient feature foundation cannot be built or documented
- leakage is detected
- Codex anchors SE1 to SE3
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- feature foundation summary
- missing feature summary
- dataset row counts and split
- regime threshold/class balance summary
- Stage 1 classifier metrics
- Stage 2 severity metrics
- continuous spread baseline metrics
- feature attribution
- spike case review
- recommendation for P0049
- tests run
- files changed
- no SE1-to-SE3 anchoring / no API / no device confirmation
- commit SHA after push

## Completion notes

Implemented as a Mac-only exploratory diagnostic/modeling package.

Result:

```text
status: PASS
local dataset table: se3_se1_bottleneck_training_dataset_v1
modeling rows: 34968
split counts: train=22728, validate=8760, holdout=3480
```

P0048 derived all requested weather proxy families and gradients from local weather history source rows. No requested P0048 feature remains missing.

Key findings:

```text
Stage-1 positive bottleneck:
  gradients alone did not improve over system-weather actuals on validation F1.
  lagged spread/regime diagnostics improved validation F1 strongly.

Stage-1 positive spike:
  lagged diagnostics gave useful recall/precision compared with weak weather-only classifiers.

Stage-2 positive severity:
  lagged diagnostics beat regime-mean and weather-gradient baselines.

Continuous spread:
  lagged diagnostic continuous regression had the best MAE/RMSE, but remains exploratory and non-deployable.
```

Recommendation:

```text
P0049 should compare direct SE3 AI-1/AI-2 modeling against the best P0048 bottleneck path before any deployable SE3 forecast/API package.
Do not proceed directly to production bottleneck deployment.
Do not anchor SE1 shape to SE3.
```

Confirmed no SE1-to-SE3 anchoring, no SE3 API, no production model artifact, no M5/M6/M7, no Home Assistant, no Shelly, no KVS and no live device actions.
