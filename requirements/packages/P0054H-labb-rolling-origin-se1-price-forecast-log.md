# Package P0054H: LABB rolling-origin SE1 anchored price forecast-origin log

## Status

planned

## Package order

P0054H

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Create a forecast-origin-safe SE1 anchored absolute price forecast log with train, validation and holdout coverage, using a rolling-origin, expanding-origin or blocked out-of-fold training protocol.

P0054F and P0054G established that the existing P0053C-B log is forecast-origin-safe for validation and holdout but has no train-period rows. P0054G also showed that naively reusing the P0053C-B/P0045 globally trained M4 method for train origins would leak future train-period target data relative to early origins.

P0054H must implement or construct a safe origin-local protocol so the later SE1 consumption no-price vs with-price-forecast ablation can train normally under the P0053C global split.

## Prior package conclusions

P0054F STOP cause:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
has validation and holdout coverage only, with zero canonical train rows.
```

P0054G STOP cause:

```text
Extending the current global-trained P0053C-B/P0045 M4 shape method into train origins would use future train-period target rows relative to early origins.
Safe train-origin coverage requires rolling-origin, expanding-origin or blocked out-of-fold upstream training.
```

P0054H is the package that is allowed to build that safe train-origin forecast source.

## Core questions

P0054H must answer:

```text
1. Can a forecast-origin-safe SE1 price forecast log be created for train origins without future leakage?
2. Which safe protocol is used: rolling-origin, expanding-origin, blocked out-of-fold, or simpler origin-local anchored baseline?
3. Does the resulting log cover train/validation/holdout target timestamps sufficiently for P0054F retry?
4. Does validation/holdout remain comparable to P0053C-B where possible?
5. What table/source should downstream SE1 consumption packages use?
```

## Target artifact

Preferred durable local table name:

```text
m4_48h_anchored_absolute_price_forecast_log_p0054h_se1_v1
```

If Codex chooses a simpler method than M4 because safe upstream model training is not practical, the table name must make that clear, for example:

```text
anchored_absolute_price_forecast_log_p0054h_se1_v1
```

Codex must document the exact name and schema.

The table must be a forecast-origin log, not a downstream consumption feature matrix.

## Required schema semantics

Each row must include or be joinable to:

```text
area
prediction_kind
forecast_origin_timestamp_utc
input_data_cutoff_utc
target_timestamp_utc
horizon_hour
predicted_price
prediction_unit
anchor_window_start_utc
anchor_window_end_utc
training_protocol
training_cutoff_utc or equivalent
source_model_family / method name
package_id = P0054H
created_at / run_id if existing conventions support it
```

Names may follow existing repo conventions, but these semantics must be represented and documented.

## Forecast-origin semantics

For every forecast origin:

```text
input_data_cutoff_utc = forecast_origin_timestamp_utc - 1h
forecast_origin_timestamp_utc <= target_timestamp_utc
target_window = [forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]
anchor_history_window = [forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)
```

The forecast path should normally be 168h long unless a row is explicitly skipped and documented.

## Safe training protocol options

Codex may choose the safest implementable option after inspecting existing P0053C-B/P0045 code.

Preferred order:

```text
1. Expanding-origin training for each forecast origin or origin block:
   train upstream price model only on data strictly before forecast_origin_timestamp_utc.

2. Blocked out-of-fold training:
   produce train-period forecast rows from folds where the model for each fold is trained only on data before that fold's forecast origins.

3. Rolling-origin training:
   use a fixed historical lookback window ending before each forecast origin.

4. Origin-local anchored baseline:
   if M4 shape training cannot be made safe in this package, create a simpler anchored absolute forecast that uses only the 48h pre-origin anchor/history and documented calendar/shape rules that do not fit on future data.
```

The chosen method must be clearly labeled. Do not call the output `M4` unless it actually uses the repository-approved M4 method safely.

## Leakage restrictions

For every generated row, these must hold:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
all anchor/history price timestamps < forecast_origin_timestamp_utc
all model fitting/training rows used for that origin have timestamps < forecast_origin_timestamp_utc
no target-window actual price is used as an input
no validation/holdout actual target data is used for train-origin model fitting
no holdout is used for selection or hyperparameter tuning
```

Forbidden inputs:

```text
actual future spot price inside target_window
future production
future export/import
future A09/A11 flow/exchange
A61 capacity/utilization/margin
continental actual prices unless proven forecast-origin safe and already allowed by source policy
live API data
```

## Period and split coverage

Use P0053C global split:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

The forecast log should provide rows that downstream P0054F retry can join to SE1 consumption target rows across all three splits.

Minimum downstream requirement:

```text
train rows > 0 and enough origins for model fitting
validation rows > 0 and enough origins for model selection/comparison
holdout rows > 0 and enough origins for final report
```

Preferred:

```text
train origin cadence is consistent with validation/holdout cadence, or clearly documented if different.
168h complete paths where possible.
```

## Validation/holdout comparison to P0053C-B

Where possible, preserve P0053C-B validation/holdout semantics or compare against it.

Required comparison if both sources exist:

```text
P0053C-B validation/holdout coverage and MAE-like price forecast metrics
P0054H validation/holdout coverage and MAE-like price forecast metrics
```

This comparison is for forecast-log quality only. It is not the SE1 consumption ablation.

## Allowed actions

Allowed:

```text
local SQLite/database reads
local SQLite/database writes for forecast log creation
local Python computation
narrow source changes under src/mac/** if needed
narrow tests under tests/mac/** if code changes are made
package-run evidence files
```

Not allowed:

```text
live market API calls
Shelly/Home Assistant/device/runtime actions
production deployment
G2-KANDIDAT promotion
large raw dataset commits
model binary commits
virtualenv/wheel/cache commits
rerunning P0054F downstream consumption models in this package
```

## Relationship to P0054F retry

P0054H must not run the downstream SE1 consumption no-price vs with-price ablation. It creates the safe price forecast source only.

After P0054H PASS or useful WARN, create a follow-up package:

```text
P0054I LABB SE1 consumption price forecast ablation retry
```

or reuse P0054F semantics if the project prefers.

## Required evidence files

Create:

```text
requirements/package-runs/P0054H/CHANGELOG.md
requirements/package-runs/P0054H/review.md
requirements/package-runs/P0054H/design.md
requirements/package-runs/P0054H/functions.md
requirements/package-runs/P0054H/labb-label.md
requirements/package-runs/P0054H/source-discovery.md
requirements/package-runs/P0054H/training-protocol-decision.md
requirements/package-runs/P0054H/forecast-method-contract.md
requirements/package-runs/P0054H/forecast-log-schema.md
requirements/package-runs/P0054H/coverage-by-split.md
requirements/package-runs/P0054H/leakage-review.md
requirements/package-runs/P0054H/validation-holdout-comparison-to-p0053cb.md
requirements/package-runs/P0054H/verification-results.md
requirements/package-runs/P0054H/downstream-contract-for-p0054f-retry.md
requirements/package-runs/P0054H/what-we-learned.md
requirements/package-runs/P0054H/next-package-recommendation.md
```

Optional compact evidence:

```text
forecast-log-summary.json
coverage-by-origin.csv
leakage-check-summary.json
price-forecast-metrics-summary.json
```

Do not commit the full generated forecast table if large. Commit summaries, schema, counts and leakage evidence.

## Files to inspect

```text
requirements/package-runs/P0054F/CHANGELOG.md
requirements/package-runs/P0054F/review.md
requirements/package-runs/P0054F/price-forecast-source-contract.md
requirements/package-runs/P0054G/CHANGELOG.md
requirements/package-runs/P0054G/review.md
requirements/package-runs/P0054G/prior-use-investigation.md
requirements/package-runs/P0054G/next-package-recommendation.md
requirements/packages/P0053C-B-M4-48h-anchored-absolute-price-forecast-log.md or nearest matching P0053C-B package
requirements/package-runs/P0053C-B/** if present
requirements/package-runs/P0053C*/** relevant price forecast evidence
requirements/package-runs/P0053B-A2/** if present
memory/spotprice-forecast-period-policy.md
memory/energy-market-ai-lab.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files that created P0053C-B forecast logs
local SQLite schema/table metadata for price forecast logs
```

Do not read large raw spot-price data files during bootstrap unless required by the actual local SQL/generation step.

## Files allowed to change

```text
requirements/packages/P0054H-labb-rolling-origin-se1-price-forecast-log.md
requirements/package-runs/P0054H/**
docs/functions/mac/spotprice-model-diagnostics.md if durable docs need updating
src/mac/** narrowly scoped forecast-log generation code if needed
tests/mac/** narrowly scoped tests for coverage/leakage/schema if code changes are made
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/API/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No actual future spot price leakage.
No production/export/import/A61/future-flow features.
No live API calls.
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054H.
No downstream consumption model ablation in this package.
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
source discovery for local price/history tables
forecast log schema exists and has required origin/cutoff/target columns
coverage by target timestamp for train/validation/holdout
coverage by forecast origin for train/validation/holdout
input cutoff not after origin
forecast origin not after target timestamp
anchor/history timestamps strictly before origin
all model fitting/training rows before each origin or origin block
no target-window actual price used as input
no validation/holdout leakage into train-origin models
no holdout selection/fitting
no live API/device/runtime actions
git diff --check
no large generated data/model artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- forecast-origin-safe SE1 price forecast log exists with train, validation and holdout coverage.
- chosen training protocol is documented and leakage-safe.
- leakage review passes.
- downstream contract for P0054F/P0054I retry is explicit.
- no forbidden runtime/API/device/live-data work occurred.
```

WARN is acceptable if:

```text
- safe log exists but uses a simpler anchored baseline instead of M4.
- train coverage is sparser than validation/holdout but enough for downstream modeling and documented.
- validation/holdout differs from P0053C-B but comparison is reported.
```

STOP if:

```text
- no forecast-origin-safe train-period SE1 price forecast can be generated.
- safe generation would require unavailable local source data or live API calls.
- implementation would require future price leakage.
- existing earlier forecast-log logic cannot be safely adapted and no simpler safe baseline is acceptable.
- device/API/runtime work would be required.
```

## Expected Codex output

```text
PASS/WARN/STOP status
chosen training protocol
created/updated table name
schema summary
target/origin coverage by split
leakage review result
validation/holdout comparison to P0053C-B if available
commands/tests run
files changed
confirmation no live API/device/A61/leakage work
confirmation no large artifacts committed
downstream contract for P0054F/P0054I retry
next package recommendation
commit SHA after push
```

## Completion notes

To be filled after implementation.
