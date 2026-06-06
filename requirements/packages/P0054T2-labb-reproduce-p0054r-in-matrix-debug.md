# Package P0054T2: LABB reproduce P0054R in P0054T matrix debug

## Status

 completed

## Package order

P0054T2

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Debug and reproduce the P0054R advanced SE3 consumption result inside the later P0054T matrix harness.

P0054R found a strong corrected-target SE3 DayAhead/full_36h result:

```text
model = HorizonBiasCorrected_WeightedEnsemble_no_price
DayAhead hourly MAE ≈ 253.7006 MW ≈ 2.6388%
full_36h MAE ≈ 243.6767 MW ≈ 2.5006%
DayAhead daily energy error ≈ 4 381 MWh ≈ 1.9334%
```

P0054T, intended to test the same top model under weather/price variants, reported a much worse W0/P0 result:

```text
M1_HorizonBiasCorrectedWeightedEnsemble W0_weatherProxy P0_noPrice
DayAhead hourly MAE ≈ 624.3882 MW ≈ 6.4629%
full_36h MAE ≈ 639.3019 MW
daily energy error ≈ 12 820 MWh ≈ 5.2457%
```

M1 and M2 were identical in P0054T, which strongly suggests that P0054T did not faithfully execute the P0054R horizon-bias-corrected weighted ensemble logic, or that row/origin/feature/evaluation semantics differed.

P0054T2 must isolate and explain this discrepancy before any conclusions from P0054T weather/price ablation are trusted.

## Core questions

P0054T2 must answer:

```text
1. Can P0054R's best W0/P0 no-price result be reproduced exactly or near-exactly in the P0054T harness?
2. If not, which difference explains the gap: model implementation, horizon-bias correction, ensemble weighting, feature matrix, row/origin set, target alignment, DayAhead slicing, metric calculation, or train/validation split?
3. Why did P0054T M1 and M2 produce identical results?
4. Are P0054T price/weather conclusions valid after reproduction, or must P0054T be superseded by a corrected matrix rerun?
5. What corrected matrix package should run next if P0054T is invalid?
```

## Required target source

Use only the corrected ENTSO-E SE3 target:

```text
table: entsoe_consumption_area_hourly_v1
area: SE3
target_column: consumption_mw
source_type: actual_total_load
```

STOP if old target is used:

```text
physical_balance_se1_se4_hourly_v1.consumption_se3
```

STOP if cross-border flow/exchange/capacity data is used as target.

## Required split policy

Use the P0054 split and the same internal-validation semantics as P0054R unless explicitly comparing alternatives:

```text
train_fit: target_timestamp_utc >= 2022-06-01T00:00:00Z
           and target_timestamp_utc < 2025-06-01T00:00:00Z
holdout:   target_timestamp_utc >= 2025-06-01T00:00:00Z
```

Holdout must not be used for fitting, model selection, ensemble weights, horizon-bias correction, correction fitting, feature selection or hyperparameter selection.

## Scope

This is a debug/reproduction package, not a new model-search package.

Do not run the full 12-test matrix until the P0054R reproduction is explained.

Allowed:

```text
reproduce P0054R W0/P0 no-price run
run P0054T W0/P0 no-price run under controlled variants
compare datasets/predictions/metrics row by row
small diagnostic code changes
```

Forbidden:

```text
new production deployment
Nord Pool/workplace integration
live API calls
Shelly/Home Assistant/device/runtime changes
new broad model search
large raw/model artifacts
```

## Required reproduction ladder

Run the following steps serially and checkpoint evidence after each:

### Step A: Evidence comparison from package runs

Read and summarize:

```text
requirements/package-runs/P0054R/model-comparison.md
requirements/package-runs/P0054R/baseline-p0054q-comparison.md
requirements/package-runs/P0054R/model-training-evidence.md
requirements/package-runs/P0054R/dataset-contract.md
requirements/package-runs/P0054R/feature-groups.md
requirements/package-runs/P0054R/leakage-review.md
requirements/package-runs/P0054T/matrix-results-summary.md
requirements/package-runs/P0054T/model-training-evidence.md
requirements/package-runs/P0054T/dataset-contract.md
requirements/package-runs/P0054T/model-selection-from-p0054r.md
requirements/package-runs/P0054T/feature-groups.md
requirements/package-runs/P0054T/leakage-review.md
```

### Step B: Dataset contract diff

Compare P0054R and P0054T for:

```text
target table/column/area
train rows
holdout rows
forecast origin count
DayAhead delivery-day count
full_36h path count
target timestamp set
origin timestamp set
horizon convention
weather feature columns
calendar feature columns
load lag/rollup feature columns
feature count
missing-row filtering
```

Produce exact row/origin overlap metrics:

```text
p0054r_target_rows
p0054t_target_rows
intersection_rows
r_only_rows
t_only_rows
p0054r_origins
p0054t_origins
intersection_origins
r_only_origins
t_only_origins
```

### Step C: Model implementation diff

Compare P0054R and P0054T implementations for:

```text
base model families used
base model hyperparameters
random seeds
weighted ensemble weights
whether weights are learned on internal validation only
whether P0054T actually applies M1 horizon-bias correction
whether P0054T M1 accidentally aliases M2
horizon-bias correction formula
horizon-bias correction training data
post-processing/calibration layers
feature preprocessing/imputation/scaling
```

P0054T2 must specifically prove or disprove:

```text
M1_HorizonBiasCorrectedWeightedEnsemble == M2_WeightedEnsemble by code/path/identity
```

### Step D: Metric implementation diff

Compare P0054R and P0054T metric code for:

```text
DayAhead delivery-day slice construction
Europe/Stockholm DST handling
forecast origin 12:00 D-1 semantics
full_36h path construction
MAE calculation row set
daily energy aggregation
denominator for percent metrics
bias/sign conventions
```

### Step E: Reproduction attempt

Run a minimal reproduction:

```text
R_like = exact P0054R W0/P0 no-price configuration in current code
T_like = P0054T W0/P0 no-price configuration
```

Compare:

```text
DayAhead hourly MAE
full_36h MAE
daily energy error
row count
origin count
prediction distribution
target distribution
error distribution
```

If R_like matches P0054R but T_like does not, isolate the matrix harness bug.

If neither matches P0054R, identify code/data drift since P0054R or an evidence reproducibility issue.

If both match P0054T, explain why P0054R evidence was not reproduced and mark old evidence as requiring review.

### Step F: Prediction-level comparison if available

If compact prediction CSVs are available or can be generated without committing large artifacts, compare P0054R-like and P0054T-like predictions by:

```text
timestamp_utc
forecast_origin_timestamp_utc
horizon_hour
actual_mw
prediction_mw
error_mw
```

Report:

```text
prediction_correlation
mean_prediction_difference
p95_abs_prediction_difference
rows_with_large_prediction_diff
largest 20 discrepancy examples summarized
```

Do not commit large prediction files; commit compact summaries only.

## Expected likely failure modes to test

P0054T2 must explicitly check these hypotheses:

```text
H1: P0054T M1 did not apply horizon-bias correction.
H2: P0054T M1 accidentally reused M2 predictions.
H3: P0054T did not reproduce P0054R ensemble weights.
H4: P0054T used P0054Q baseline-style model path instead of P0054R advanced path.
H5: P0054T used a different origin/target row set.
H6: P0054T used holdout-only weather/noise handling incorrectly even for W0.
H7: P0054T price-feature plumbing changed the no-price matrix feature set.
H8: P0054T metric calculation differs from P0054R.
H9: P0054R evidence used a different feature generation contract than documented.
H10: P0054R result was not reproducible under current code and must be quarantined.
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054T2/CHANGELOG.md
requirements/package-runs/P0054T2/review.md
requirements/package-runs/P0054T2/design.md
requirements/package-runs/P0054T2/functions.md
requirements/package-runs/P0054T2/labb-label.md
requirements/package-runs/P0054T2/source-evidence-summary.md
requirements/package-runs/P0054T2/dataset-contract-diff.md
requirements/package-runs/P0054T2/model-implementation-diff.md
requirements/package-runs/P0054T2/metric-implementation-diff.md
requirements/package-runs/P0054T2/m1-m2-alias-review.md
requirements/package-runs/P0054T2/reproduction-attempt-results.md
requirements/package-runs/P0054T2/prediction-diff-summary.md if applicable
requirements/package-runs/P0054T2/root-cause-analysis.md
requirements/package-runs/P0054T2/leakage-review.md
requirements/package-runs/P0054T2/impact-on-p0054t.md
requirements/package-runs/P0054T2/impact-on-p0054r.md
requirements/package-runs/P0054T2/what-we-learned.md
requirements/package-runs/P0054T2/next-package-recommendation.md
```

Optional compact evidence:

```text
rowset-diff-summary.json
model-config-diff.json
metric-diff-summary.json
reproduction-summary.json
prediction-diff-top20.csv
```

Do not commit large raw datasets, model binaries, full prediction dumps, virtualenvs, wheels or caches.

## Files to inspect

```text
requirements/package-runs/P0054R/**
requirements/package-runs/P0054T/**
requirements/packages/P0054R-labb-se3-advanced-ai-entsoe-dayahead.md
requirements/packages/P0054T-labb-se3-consumption-model-weather-price-matrix.md
src/mac/** relevant P0054R/P0054T modeling/evaluation scripts
tests/mac/** relevant tests
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
docs/functions/mac/spotprice-model-diagnostics.md
```

## Files allowed to change

```text
requirements/packages/P0054T2-labb-reproduce-p0054r-in-matrix-debug.md
requirements/package-runs/P0054T2/**
src/mac/** narrowly scoped reproduction/debug fixes if needed
tests/mac/** narrowly scoped tests for reproduction semantics if code changes are made
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No Nord Pool/workplace integration.
No live API calls.
No old physical_balance target.
No flow/exchange/capacity target.
No future actual load/price leakage.
No holdout fitting or selection.
No broad refactor unrelated to P0054T2.
No large raw data/model/prediction artifacts.
```

## Verification commands

Codex must define final commands in design.md and run equivalent checks for:

```text
P0054R and P0054T evidence read
corrected ENTSO-E target confirmed
old physical_balance target not used
row/origin set diff computed
model implementation diff computed
M1/M2 alias check completed
metric implementation diff completed
minimal reproduction completed or STOP reason documented
root cause identified or bounded honestly
leakage review passes
git diff --check
no large artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- root cause for P0054R vs P0054T discrepancy is identified, or narrowed to a specific unreproducible evidence/code-drift boundary.
- M1/M2 identical-result issue is explained.
- P0054T validity is assessed.
- clear next package recommendation is provided.
- leakage review passes.
```

WARN is acceptable if:

```text
- P0054R cannot be exactly reproduced but the reason is bounded and evidence is honest.
- prediction-level comparison is limited to compact summaries.
- one optional hypothesis cannot be tested due to missing old artifacts.
```

STOP if:

```text
- corrected ENTSO-E target cannot be accessed.
- reproduction cannot be attempted at all.
- root cause cannot be bounded sufficiently for a next action.
- future actual load/price leakage is found.
- device/runtime/NordPool/workplace integration is attempted.
```

## Expected Codex output

```text
PASS/WARN/STOP status
commit SHA
P0054R vs P0054T headline discrepancy
whether P0054R was reproduced
whether P0054T M1 equals M2 and why
root cause
validity of P0054T conclusions
impact on P0054R conclusions
recommended next package
commands/tests run
files changed
confirmation no old target/flow target/API/device/A61/NordPool/workplace integration
confirmation no large artifacts committed
```

## Completion notes

Completed by Codex on 2026-06-06.

Result: `PASS`.

P0054R was reproduced near-exactly/current-deterministically:

```text
historic P0054R DayAhead MAE:    253.70062353819162 MW
reproduced R-like DayAhead MAE:  253.70062353819173 MW
absolute delta:                  ~1.1e-13 MW
```

P0054T W0/P0 was not a faithful P0054R reproduction. It used the P0054N exact-origin price-coverage skeleton even for no-price, so P0054T's no-price baseline was restricted to:

```text
P0054R row/origin skeleton: 52 173 rows, 1 451 origins
P0054T row/origin skeleton: 16 102 rows,   448 origins
intersection:               16 102 rows,   448 origins
R-only:                     36 071 rows, 1 003 origins
T-only:                          0 rows,     0 origins
```

The restricted P0054T W0/P0 rowset had only March-May 2025 train_fit coverage and no internal-validation rows. That forced equal ensemble weights and zero horizon-bias correction.

P0054T M1 equaled M2 because all horizon-bias values were zero:

```text
compared rows: 16 102
max abs M1-M2 prediction difference: 0.0 MW
nonzero horizon-bias count: 0
```

P0054T conclusions should therefore be superseded for weather/price ablation. P0054R remains valid/reproducible. Recommended next package: P0054U corrected matrix, using the P0054R no-price origin skeleton for P0 and a separate aligned price-coverage comparison for P1.

No API, devices, runtime, A61, Nord Pool, workplace integration, old physical-balance target, flow/exchange/capacity target, future actual load/price leakage or large model artifacts were used.
