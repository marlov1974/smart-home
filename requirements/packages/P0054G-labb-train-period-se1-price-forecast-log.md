# Package P0054G: LABB train-period SE1 price forecast-origin log

## Status

planned

## Package order

P0054G

## Label

```text
LABB
```

This package is research/lab work under P0054A. It is not a G2-KANDIDAT evaluation.

## Purpose

Unblock P0054F by creating or extending a forecast-origin-safe SE1 anchored absolute price forecast log that covers train, validation and holdout origins under the P0053C global split.

P0054F stopped correctly because the available forecast-safe source:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
```

has validation and holdout coverage only, with zero train-period rows. That makes it unusable as a training feature for a paired SE1 consumption no-price vs with-price-forecast ablation.

P0054G must build the missing train-period forecast-origin-safe price forecast coverage, or prove why it cannot be built safely.

## Important context from operator

The operator notes that this forecast was used earlier today for a similar purpose with another model. P0054G must explicitly investigate and document that apparent contradiction.

Required distinction:

```text
1. Was the prior use a price forecast model evaluation/logging package rather than a downstream consumption model feature package?
2. Did the prior use cover only validation/holdout, not train?
3. Did the prior model use a different split, target, area, horizon or feature contract?
4. Was the earlier use evidence-summary only rather than trainable feature matrix usage?
5. Is there another local table/log/source with train-period forecast-origin rows that P0054F did not find?
```

Do not assume P0054F was wrong. Verify.

## Core questions

P0054G must answer:

```text
1. What exact forecast-safe SE1 price forecast sources exist locally?
2. Which previous package/model used them earlier today, and under what contract?
3. Why did P0054F find zero train-period rows in P0053C-B?
4. Can we generate train-period forecast-origin rows using the same M4 anchored method without leakage?
5. Does the resulting log cover train, validation and holdout sufficiently for P0054F-style modeling?
6. What source should P0054H/P0054F-retry use for SE1 price forecast features?
```

## Target artifact

Create a durable local forecast log/table or documented equivalent with train/validation/holdout coverage.

Preferred table name if compatible with existing naming:

```text
m4_48h_anchored_absolute_price_forecast_log_p0054g_se1_v1
```

If extending or reusing an existing table is safer, Codex may choose a different name, but must document:

```text
source table
created/updated table
schema
row counts
coverage by split
forecast origin semantics
leakage checks
```

## Forecast method

Use the same or closest repository-approved method as P0053C-B:

```text
prediction_kind = anchored_absolute_price
area = SE1
forecast_origin_timestamp_utc = first target timestamp in a 168h rolling path
input_data_cutoff_utc = forecast_origin_timestamp_utc - 1h
target_window = [forecast_origin_timestamp_utc, forecast_origin_timestamp_utc + 167h]
anchor_history_window = [forecast_origin_timestamp_utc - 48h, forecast_origin_timestamp_utc)
```

The generated forecast may use a simple anchored method if that is what P0053C-B used, but it must preserve forecast-origin safety.

Do not create a new advanced price model unless the existing P0053C-B implementation already does so and can be reused safely.

## Required period and split coverage

Use P0053C global policy:

```text
train:      2022-06-01T00:00:00Z .. 2024-12-31T23:00:00Z
validation: 2025-01-01T00:00:00Z .. 2025-05-31T23:00:00Z
holdout:    2025-06-01T00:00:00Z .. latest_available_timestamp_utc
```

For P0054F downstream use, P0054G must produce forecast rows whose target timestamps can join to SE1 consumption target rows in all three splits.

Minimum acceptable coverage:

```text
train:      enough origins/target rows to train downstream models without changing the global split
validation: enough origins/target rows for model selection/comparison
holdout:    enough origins/target rows for final report
```

If exact P0053C-B validation/holdout coverage can be retained and only train is added, that is preferred.

## Forecast-origin cadence

Use the same origin cadence as P0053C-B where possible.

P0053C-B evidence from P0054F found:

```text
validation origins = 144
holdout origins = 348
168h rolling paths
```

Codex must determine whether those origins are weekly, daily, sliding or otherwise selected, then apply the same origin-selection logic to train unless there is a documented reason not to.

## Leakage restrictions

The forecast log must not use:

```text
actual future spot price inside target_window
future actual production
future actual export/import
future actual A09/A11 flow/exchange
A61 capacity/utilization/margin
holdout for selection or fitting
any data after input_data_cutoff_utc for a given origin
```

Anchor/history windows must be strictly before origin.

For every row:

```text
input_data_cutoff_utc <= forecast_origin_timestamp_utc
forecast_origin_timestamp_utc <= target_timestamp_utc
anchor_price_timestamp_utc < forecast_origin_timestamp_utc
no target-window actual price used for anchor
```

## Allowed data and actions

Allowed:

```text
local SQLite/database reads
local SQLite/database writes for forecast log generation
local package-run evidence files
reusing existing local M4/P0053C-B code
small source changes needed to allow train-period generation
small tests for forecast-origin/leakage/coverage
```

Not allowed:

```text
live market API calls
Shelly/Home Assistant/device/runtime actions
G2-KANDIDAT promotion
production deployment
large raw dataset commits
model binary commits
broad refactor unrelated to forecast-log generation
```

## Relationship to P0054F

P0054G does not rerun the SE1 consumption price-ablation models. It only creates and validates the forecast-safe price forecast source needed by that work.

After P0054G, a follow-up package should retry the P0054F ablation, likely as:

```text
P0054H LABB SE1 consumption price forecast ablation retry
```

## Required evidence files

Create:

```text
requirements/package-runs/P0054G/CHANGELOG.md
requirements/package-runs/P0054G/review.md
requirements/package-runs/P0054G/design.md
requirements/package-runs/P0054G/functions.md
requirements/package-runs/P0054G/labb-label.md
requirements/package-runs/P0054G/prior-use-investigation.md
requirements/package-runs/P0054G/source-discovery.md
requirements/package-runs/P0054G/forecast-method-contract.md
requirements/package-runs/P0054G/forecast-log-schema.md
requirements/package-runs/P0054G/coverage-by-split.md
requirements/package-runs/P0054G/leakage-review.md
requirements/package-runs/P0054G/verification-results.md
requirements/package-runs/P0054G/downstream-contract-for-p0054f-retry.md
requirements/package-runs/P0054G/what-we-learned.md
requirements/package-runs/P0054G/next-package-recommendation.md
```

Optional compact evidence:

```text
forecast-log-summary.json
coverage-by-origin.csv
leakage-check-summary.json
```

Do not commit large raw datasets or generated full forecast tables if they are large. Commit summaries and schema/evidence instead.

## Files to inspect

```text
requirements/package-runs/P0054F/CHANGELOG.md
requirements/package-runs/P0054F/review.md
requirements/package-runs/P0054F/price-forecast-source-contract.md
requirements/package-runs/P0054F/next-package-recommendation.md
requirements/packages/P0053C-B-M4-48h-anchored-absolute-price-forecast-log.md or nearest matching P0053C-B package
requirements/package-runs/P0053C-B/** if present
requirements/package-runs/P0053C*/** relevant price forecast evidence
memory/spotprice-forecast-period-policy.md
memory/energy-market-ai-lab.md
docs/functions/mac/spotprice-model-diagnostics.md
local source files that created P0053C-B forecast logs
local SQLite schema/table metadata for price forecast logs
```

Do not read large raw spot-price data files during package bootstrap unless the actual verification/generation step requires local SQL inspection.

## Files allowed to change

```text
requirements/packages/P0054G-labb-train-period-se1-price-forecast-log.md
requirements/package-runs/P0054G/**
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
No large raw dataset commits.
No model binary commits.
No virtualenv/wheel/cache commits.
No broad refactor unrelated to P0054G.
No rerun of P0054F downstream consumption models in this package.
```

## Verification commands

Codex must define final commands in `design.md`, but must run equivalent checks for:

```text
source discovery for all local SE1 price forecast tables/logs
prior-use investigation documented
forecast log schema exists and has required timestamp/origin columns
coverage by target timestamp for train/validation/holdout
coverage by forecast origin for train/validation/holdout
input cutoff not after origin
forecast origin not after target timestamp
anchor/history timestamps strictly before origin
no target-window actual price used for anchor
no holdout selection/fitting
no live API/device/runtime actions
git diff --check
no large generated data/model artifacts staged
```

## Pass / WARN / STOP interpretation

PASS requires:

```text
- P0054F STOP cause is confirmed or corrected with evidence.
- Prior-use contradiction is resolved in writing.
- Forecast-origin-safe SE1 price forecast log exists with train/validation/holdout coverage.
- Leakage review passes.
- Downstream contract for P0054F retry is explicit.
```

WARN is acceptable if:

```text
- train-period coverage can be created but is shorter/sparser than validation/holdout and this is documented.
- exact P0053C-B origin cadence cannot be reproduced, but a forecast-origin-safe cadence is created and clearly labeled.
- prior-use investigation finds the earlier model used a different contract but no bug.
```

STOP if:

```text
- no forecast-origin-safe train-period SE1 price forecast can be generated.
- generating train-period rows would require actual future spot price leakage.
- required source data is missing locally and live API calls would be needed.
- existing earlier use appears to have used leakage and must be quarantined.
- device/API/runtime work would be required.
```

## Expected Codex output

```text
PASS/WARN/STOP status
prior-use investigation result
source-discovery result
forecast method and schema
target/origin coverage by split
leakage review result
created/updated table name
commands/tests run
files changed
confirmation no live API/device/A61/leakage work
confirmation no large artifacts committed
next package recommendation
commit SHA after push
```

## Completion notes

To be filled after implementation.
