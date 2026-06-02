# Package P0050: SE3-SE1 baseline-corrected demand-response and heat-pump effect analysis

## Status

verified

## Package order

P0050

## Primary area

G2 / Mac tooling / spotprice V2 / SE3-SE1 spread / demand response / local SE3 price rank / heat-pump effect analysis

## Decision summary

P0050 follows P0047, P0048 and P0049 and corrects one important framing issue:

```text
Large consumers, Nibe heat pumps, Tibber users, Homey automations and similar price optimizers do not react to SE3-SE1 spread directly.
They react to SE3 price being locally expensive or cheap relative to the current day or nearby days.
```

Therefore P0050 must analyze whether local SE3 price rank and top-N/bottom-N price windows explain later SE3-SE1 behavior better than broad absolute price thresholds alone.

P0050 must also baseline-correct raw SE3-SE1 before interpreting day-type effects. Weekend/holiday effects must not be misread as dynamic bottleneck behavior if they are only lower normal spread baseline.

P0050 is an analysis package. It must not build a production SE3 forecast, API, device integration or deployable model.

## Preconditions

P0050 may start only after P0049 PASS evidence exists.

Required P0049 facts:

```text
- se3_se1_bottleneck_reservoir_analysis_v1 was derived from P0048 data.
- Explicit reservoir pressure did not beat rolling or lagged spread features.
- Lagged spread remained strong for regime classification across horizons.
- Time/calendar was strong for MAE at several longer horizons.
- SE1 price level weakly decreased future 6h spread risk in validation correlation.
- SE3 price level had positive future 6h spread correlation.
- Friday/weekend/holiday evidence was suggestive but not conclusive.
```

P0050 must STOP if it cannot reconstruct:

```text
se3_minus_se1 = se3_price - se1_price
```

or if it cannot build a train-only baseline expected spread profile for residual analysis.

## Core hypotheses

### H1: Baseline-corrected day-type hypothesis

Raw weekend/holiday spread differences may reflect normal lower/higher baseline rather than a different bottleneck mechanism.

P0050 must therefore analyze:

```text
spread_residual = actual_se3_minus_se1 - expected_spread_baseline
```

where `expected_spread_baseline` is fit only on train data and uses at least:

```text
model_cet_hour
model_cet_weekday or daytype
season/month/day-of-year bucket
holiday/bridge-day where available
```

All day-type conclusions must be reported for both:

```text
raw se3_minus_se1
baseline-corrected spread_residual
```

### H2: Local SE3 price-rank response hypothesis

Consumers react to local SE3 price rank, not to spread.

Example algorithms:

```text
- avoid the 4 most expensive hours today
- avoid the 8 most expensive hours today
- charge/heat/recover during the 4 or 8 cheapest hours
- optimize against highest hours this day
- optimize against highest hours in a 48h published/known horizon
```

P0050 must test whether top-N/bottom-N SE3 price windows are followed by spread damping, spread shifting, or rebound.

### H3: Heat-pump / degree-minute veto hypothesis

Common heat-pump optimizers may handle isolated price peaks but fail during prolonged high-price/cold periods because heat demand and degree-minute deficit override spot optimization.

P0050 must test whether:

```text
low temperature + long high SE3 local-rank period
```

is followed by higher future SE3-SE1 residuals, especially after short-term avoidance capacity is exhausted.

## Scope

P0050 owns:

```text
1. Build baseline-corrected SE3-SE1 residuals.
2. Build local SE3 price-rank features over day and 48h windows.
3. Build top-N and bottom-N response features that approximate common consumer optimizers.
4. Build cold/high-price and heat-pump-pressure diagnostic features.
5. Evaluate response/rebound behavior by horizon and day type.
6. Determine whether demand-response/heat-pump effects should be features in a future SE3 bottleneck or direct SE3 model.
```

## Non-goals and hard prohibitions

P0050 must not:

```text
- anchor SE1 shape to SE3
- build SE3 forecast API
- build production SE3 forecast
- retrain or deploy SE1 AI-1/AI-2 product models
- create deployable SE3-SE1 model artifacts
- touch Shelly/Home Assistant/KVS/devices
- build M5/M6/M7
- ingest futures/forward curves
```

Exploratory models/configs are allowed as evidence only and must be labeled:

```text
exploratory only, not deployable
```

## Time model

Use the P0042 fixed-CET convention inherited by P0048/P0049:

```text
timestamp_utc = primary time identity
model_cet_timestamp = timestamp_utc + 1h all year
model_cet_date
model_cet_hour
```

Do not use Europe/Stockholm civil time as a primary key.

## Dataset

Start from the latest P0049/P0048 dataset that contains:

```text
se1_price
se3_price
se3_minus_se1
weather gradient features
calendar/special-day features
fixed-CET fields
```

Preferred input:

```text
se3_se1_bottleneck_reservoir_analysis_v1
```

or, if that is not persisted, regenerate from:

```text
se3_se1_bottleneck_training_dataset_v1
```

Create a derived analysis dataset:

```text
se3_se1_demand_response_analysis_v1
```

Required columns:

```text
timestamp_utc
model_cet_timestamp
model_cet_date
model_cet_hour
model_cet_weekday
model_cet_day_of_year
se1_price
se3_price
se3_minus_se1
expected_spread_baseline
spread_residual
spread_residual_abs
spread_regime
is_near_zero
is_positive_bottleneck
is_positive_spike
weather proxy/gradient features
calendar/special-day features
local SE3 rank/top-N features
heat-pump/cold-pressure features
```

## Train-only spread baseline

P0050 must build at least three train-only expected-spread baselines and compare them:

```text
B0_hour_weekday:
  mean/median se3_minus_se1 by model_cet_weekday × model_cet_hour

B1_hour_daytype_season:
  robust mean/median by model_cet_hour × daytype × season/month

B2_smoothed_hour_daytype_dayofyear:
  smoothed fixed-CET hour/daytype/day-of-year profile if practical
```

Use train data only. Apply the chosen baseline to validation/holdout.

P0050 must select one residual definition for analysis and document why.

## Local SE3 price-rank features

P0050 must create local price-rank features based on SE3 price.

### Day window features

For each fixed-CET model date:

```text
se3_rank_in_day
se3_percentile_in_day
se3_price_minus_day_mean
se3_price_minus_day_median
se3_price_zscore_day
se3_is_top2_day
se3_is_top4_day
se3_is_top6_day
se3_is_top8_day
se3_is_bottom2_day
se3_is_bottom4_day
se3_is_bottom6_day
se3_is_bottom8_day
se3_above_day_p70
se3_above_day_p80
se3_above_day_p90
se3_below_day_p30
se3_below_day_p20
se3_below_day_p10
```

Interpretation:

```text
p90 ≈ top 2–3 hours/day
p80 ≈ top 4–5 hours/day
p70 ≈ top 7–8 hours/day
```

### 48h window features

For rolling or forecast-origin-compatible 48h windows, create:

```text
se3_rank_in_48h
se3_percentile_in_48h
se3_price_minus_48h_mean
se3_price_zscore_48h
se3_is_top4_48h
se3_is_top8_48h
se3_is_top12_48h
se3_is_top16_48h
se3_is_bottom4_48h
se3_is_bottom8_48h
se3_is_bottom12_48h
se3_is_bottom16_48h
se3_above_48h_p70
se3_above_48h_p80
se3_above_48h_p90
se3_below_48h_p30
se3_below_48h_p20
se3_below_48h_p10
```

P0050 must document whether the 48h window is centered, trailing, leading-known, or forecast-origin-compatible.

For causal/forecast diagnostics, prefer using only prices that would be known at the forecast origin. If historical full-day/future-day ranks are used as behavioral explanatory variables, label them as explanatory/oracle-not-deployable.

## Consumer optimizer response features

Build features approximating common simple optimizers:

```text
top4_day_hours_last_6h
 top4_day_hours_last_12h
 top4_day_hours_last_24h
 top8_day_hours_last_6h
 top8_day_hours_last_12h
 top8_day_hours_last_24h
bottom4_day_hours_last_6h
bottom4_day_hours_last_12h
bottom4_day_hours_last_24h
bottom8_day_hours_last_6h
bottom8_day_hours_last_12h
bottom8_day_hours_last_24h
hours_since_top4_day_hour
hours_since_top8_day_hour
hours_since_bottom4_day_hour
hours_since_bottom8_day_hour
hours_until_next_bottom4_day_hour_if_known
hours_until_next_bottom8_day_hour_if_known
no_bottom4_recovery_window_next_12h_if_known
no_bottom8_recovery_window_next_24h_if_known
```

Remove the leading spaces in field names in implementation; they are not semantic.

Where forward-looking known-price features are not forecast-safe for the evaluated horizon, keep them in an explicitly labeled explanatory-only group.

## Heat-pump / cold-pressure features

P0050 must build heat-pump-pressure proxies using SE3/south/system temperature fields from P0048.

Required features:

```text
temperature_south_or_se3_actual
temperature_south_or_se3_delta_from_normal
is_cold_below_train_p25
is_cold_below_train_p10
cold_hours_last_6h
cold_hours_last_12h
cold_hours_last_24h
cold_hours_last_48h
cold_hours_last_72h
se3_top4_and_cold_hours_last_24h
se3_top8_and_cold_hours_last_24h
se3_top4_and_cold_hours_last_48h
se3_top8_and_cold_hours_last_48h
se3_above_day_p80_and_cold_hours_last_24h
se3_above_day_p70_and_cold_hours_last_48h
heat_debt_pressure_ema_12h
heat_debt_pressure_ema_24h
heat_debt_pressure_ema_48h
heat_debt_pressure_ema_72h
cheap_recovery_hours_last_24h
hours_since_cheap_recovery_window
cold_and_no_cheap_recovery_window
```

Definition guidance:

```text
heat_debt_pressure = accumulated cold × local high-price avoidance pressure - cheap recovery relief
```

Codex must document exact formulas and train-only thresholds.

## Day-type groups

Analyze at least these groups:

```text
monday_to_thursday
friday
saturday
sunday
weekend
holiday
bridge_day
holiday_period
workday_business_hour
morning_peak
evening_peak
```

Day-type findings must be reported on both:

```text
raw spread
spread_residual
```

## Response and rebound analysis

P0050 must evaluate whether top-N/bottom-N SE3 hours are followed by:

```text
1. same-hour spread damping
2. delayed spread damping
3. shifted spread/rebound in later cheap hours
4. increased future spread during cold/high-price extended periods
```

Required horizons:

```text
same_hour
1h
3h
6h
12h
24h
48h
72h
```

For each horizon and event class, compute future raw spread and residual spread summaries.

Required event classes:

```text
se3_top4_day
se3_top8_day
se3_top4_48h
se3_top8_48h
se3_bottom4_day
se3_bottom8_day
se3_top4_day_and_cold
se3_top8_day_and_cold
se3_top8_day_after_24h_cold_pressure
se3_bottom4_recovery_after_top8
```

## Exploratory model groups

Evaluate simple exploratory models to quantify feature usefulness.

Required target variants:

```text
future_spread_residual_1h
future_spread_residual_6h
future_spread_residual_24h
future_spread_residual_48h
future_positive_bottleneck_residual_regime_1h
future_positive_bottleneck_residual_regime_6h
future_positive_bottleneck_residual_regime_24h
```

Feature groups:

```text
G0_time_calendar_baseline
G1_raw_spread_lagged
G2_local_se3_rank_topN
G3_local_se3_rank_topN_plus_daytype
G4_heat_pump_cold_pressure
G5_topN_plus_heat_pump_plus_daytype
G6_P0049_reservoir_plus_topN_plus_heat_pump
G7_explanatory_oracle_known_future_price_rank_diagnostic
```

`G7` may use explanatory forward-known rank fields only if clearly labeled non-deployable/oracle diagnostic.

Models may include:

```text
HistGradientBoostingRegressor
HistGradientBoostingClassifier
LogisticRegression / linear baseline
shallow DecisionTree for interpretation
```

No neural nets, transformers, AutoML or heavy dependencies.

## Baselines

Required baselines:

```text
B0_expected_spread_baseline_only
B1_previous_hour_spread_residual
B2_time_calendar_residual_profile
B3_P0049_best_lagged_spread_group
B4_P0049_time_calendar_long_horizon_group
```

## Metrics

Regression/residual metrics:

```text
MAE
RMSE
median_absolute_error
p90_absolute_error
p95_absolute_error
bias
spearman/rank correlation
```

Classification metrics:

```text
precision
recall
F1
PR-AUC
ROC-AUC if meaningful
confusion matrix
calibration/reliability table
```

Response/rebound diagnostics:

```text
same-hour residual difference vs baseline
future residual difference by horizon
rebound residual after bottom/recovery hours
cold/high-price interaction lift
Friday/weekend/holiday lift after baseline correction
```

## Required evidence files

P0050 must create:

```text
requirements/package-runs/P0050/CHANGELOG.md
requirements/package-runs/P0050/review.md
requirements/package-runs/P0050/design.md
requirements/package-runs/P0050/functions.md
requirements/package-runs/P0050/dataset-contract.md
requirements/package-runs/P0050/spread-baseline-and-residuals.md
requirements/package-runs/P0050/local-se3-price-rank-features.md
requirements/package-runs/P0050/consumer-optimizer-response-features.md
requirements/package-runs/P0050/heat-pump-pressure-features.md
requirements/package-runs/P0050/daytype-baseline-corrected-results.md
requirements/package-runs/P0050/topN-response-and-rebound.md
requirements/package-runs/P0050/heat-pump-cold-high-price-results.md
requirements/package-runs/P0050/exploratory-model-results.md
requirements/package-runs/P0050/feature-ablation-results.md
requirements/package-runs/P0050/calibration-and-error-review.md
requirements/package-runs/P0050/next-package-recommendation.md
requirements/package-runs/P0050/component-attribution-summary.md
```

Optional machine-readable evidence:

```text
requirements/package-runs/P0050/metrics-summary.json
requirements/package-runs/P0050/topN-response-and-rebound.csv
requirements/package-runs/P0050/daytype-residual-summary.csv
requirements/package-runs/P0050/heat-pump-pressure-summary.csv
requirements/package-runs/P0050/modeling-dataset-sample.csv
```

Do not commit large generated datasets or model binaries.

## Required answers

P0050 must explicitly answer:

```text
1. Which input dataset/table/view was used?
2. Which expected-spread baseline was selected and why?
3. Do weekend/holiday effects remain after baseline correction?
4. Is Friday actually less persistent or less bottleneck-prone after baseline correction?
5. Do SE3 top4/top8 day hours show same-hour spread damping?
6. Do SE3 top4/top8 day hours show later rebound?
7. Are p70/p80/top8 effects more useful than p90/top2 effects?
8. Do bottom4/bottom8 cheap recovery hours show shifted load effects?
9. Does cold + top-N high-price pressure increase later spread residuals?
10. Does heat_debt_pressure improve over simple temperature or simple price-rank features?
11. Are the effects stronger on weekdays, Fridays, weekends or holidays?
12. Which feature family should be carried into P0051: local price rank, heat-pump pressure, daytype residuals, reservoir, or none?
13. Should P0051 compare direct SE3 AI-1/AI-2 with a bottleneck/demand-response model, or is more analysis needed?
14. Confirm no SE1-to-SE3 anchoring, no API, no production model, no device actions.
```

## Tests

Required automated tests:

```text
- SE3-SE1 equals se3_price - se1_price in the derived dataset
- timestamp_utc and fixed-CET fields are present
- expected-spread baseline is fit on train only
- spread_residual uses train-only baseline predictions
- day and 48h rank features have deterministic tie handling
- top-N/bottom-N counts are correct for 24h and 48h groups
- p70/p80/p90 flags correspond to documented percentile logic
- rolling response features are backward-looking unless explicitly marked explanatory/oracle
- forward-known rank features are labeled non-deployable/oracle if used
- heat-pump pressure formulas are documented and reproducible
- chronological splits are non-overlapping
- no SE1 shape is anchored to SE3
- no production forecast API is created
- no deployable model artifact is created
- no M5/M6/M7/API/device path is touched
```

## Pass/fail interpretation

PASS requires:

```text
- baseline-corrected spread residuals are built and documented
- local SE3 price-rank/top-N features are built and documented
- p70/p80/top4/top8 behavior is tested
- heat-pump/cold/high-price pressure hypothesis is tested
- day-type effects are reported before and after baseline correction
- next architecture recommendation is explicit
- forbidden anchoring/API/device work is not done
```

WARN is acceptable if:

```text
- effects are suggestive but not decisive
- forward-known price-rank features are only explanatory/oracle
- heat-pump pressure helps only subsets or short horizons
- daytype samples are too small for strong Friday/holiday conclusions
```

STOP if:

```text
- leakage is detected in deployable feature groups
- expected-spread residual baseline cannot be trusted
- SE3-SE1 cannot be reconstructed reliably
- Codex anchors SE1 to SE3
- Codex creates production/API/device work
```

## Expected Codex output

- PASS/WARN/STOP status
- dataset and split used
- selected expected-spread baseline
- top-N/p70/p80/p90 response summary
- heat-pump/cold/high-price response summary
- daytype baseline-corrected conclusion
- feature ablation conclusion
- recommendation for P0051
- tests run
- files changed
- no SE1-to-SE3 anchoring / no API / no device confirmation
- commit SHA after push

## Completion notes

P0050 PASS.

Implemented `src.mac.services.spotprice_model_diagnostics.p0050` and built the local analysis table:

```text
se3_se1_demand_response_analysis_v1
```

Primary input:

```text
se3_se1_bottleneck_training_dataset_v1
```

P0049 reservoir join:

```text
se3_se1_bottleneck_reservoir_analysis_v1
```

Row counts:

```text
source_rows = 34968
persisted_rows = 34968
train = 22728
validate = 8760
holdout = 3480
```

Selected baseline:

```text
B2_smoothed_hour_daytype_dayofyear
```

Main result:

```text
- Baseline correction changed the interpretation of day-type effects; weekend residual lift was lower than all validation/holdout rows.
- SE3 top4/top8 day hours had high same-hour residual lift, negative 6h residual lift and positive 24h residual lift, consistent with short damping plus later rebound as an exploratory diagnostic.
- Bottom4 recovery after top8 showed positive 6h residual lift, so cheap-hour recovery is not proven as clean relief.
- Heat-debt pressure was weak in this deterministic diagnostic; 24h heat-debt correlation with future 6h residual was slightly negative.
- Lagged raw spread residual remained the strongest exploratory MAE group across tested horizons; local SE3 rank/top-N won F1 at 48h only.
```

Recommendation:

```text
P0051 should compare direct SE3 AI-1/AI-2 with a bottleneck/demand-response residual model. Carry local SE3 rank/top-N and heat-debt features only as diagnostic candidates until forecast-origin validation confirms usefulness.
```

Confirmed:

```text
No SE1-to-SE3 anchoring, no SE3 API, no production model artifact, no M5/M6/M7, no Shelly, no Home Assistant, no KVS and no device actions.
```
