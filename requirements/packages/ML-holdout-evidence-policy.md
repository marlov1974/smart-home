# ML holdout evidence policy

## Status

active policy for P0034 and all later ML/model packages

## Applies to

This policy applies to every package that trains, evaluates, benchmarks or compares a model, including but not limited to:

```text
P0034: M4 ML normal spot model
P0035: M5 ML temperature forecast delta model
P0036: forecast API/model composition
P0037: futures/absolute long-term model
any later ML/backtest/forecast package
```

## Decision

All ML holdout results must be persisted in repository evidence files.

Terminal output, local SQLite tables, local model directories and informal Codex summaries are not sufficient evidence.

A package is not complete until holdout metrics and holdout baseline comparisons have been written to package-run evidence under:

```text
requirements/package-runs/<PACKAGE>/
```

## Required evidence files

Each ML/model package must include, as applicable:

```text
holdout-results.md
baseline-comparison.md
backtest-summary.md
model-artifact-summary.md
```

If a package uses JSON/CSV in addition to Markdown, store concise text/JSON summaries in repo evidence and keep large generated prediction files local.

Recommended optional machine-readable files:

```text
holdout-results.json
baseline-comparison.json
```

## Required holdout contents

The evidence must include:

```text
package id
model id/version
model class/algorithm
fallback/WARN/STOP status if relevant
input DBs and artifact paths
feature schema/version
target schema/version
train period
validation period
holdout period
row counts per split
excluded rows and reasons
random seed if any
time split method
leakage controls
```

## Required metrics by target

For spotprice model packages, holdout metrics must be reported separately for:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

For each target, include as applicable:

```text
hourly MAE
hourly RMSE
level MAE
level RMSE
curve-index MAE
curve-index RMSE
week-of-year index error
week-within-month index error
monthly clipped-curve error
rank accuracy for cheapest/most expensive hours where meaningful
top/bottom quantile precision where meaningful
```

If a metric is not applicable, state why.

## Required baseline comparisons

Every ML holdout result must include baseline comparisons.

For P0034/M4, the required baseline is at least:

```text
P0033 M1 calm normal price v1
```

If an existing/pre-P0034 weekly index model exists and is accessible, it must also be included or documented as unavailable.

Baseline comparison must show both model and baseline values in the same table, for example:

```text
target | split | metric | candidate_model | baseline_m1 | delta | winner
```

Do not write only a narrative such as `model does not beat M1`. Persist the actual numbers.

## Required status interpretation

Evidence must classify the holdout result:

```text
PASS: candidate model materially improves relevant holdout metrics without violating constraints.
WARN: candidate model is reproducible but does not beat baseline, dependency fallback was used, or metrics are mixed/uncertain.
STOP: required holdout cannot be computed, leakage is detected, required baseline is missing, or required dependency/model class is unavailable and no acceptable fallback was approved.
```

If a fallback model is used because a dependency such as scikit-learn is missing, the evidence must clearly state:

```text
- real ML dependency missing or unavailable
- fallback model used
- fallback is not production M4/M5 unless explicitly approved
- follow-up dependency/model package required if applicable
```

## Repository storage policy

Commit concise evidence only.

Allowed in repo:

```text
Markdown summaries
small JSON metric summaries
small CSV metric summaries
small deterministic fixtures
schema/manifest files
```

Do not commit:

```text
large prediction dumps
large trained binary model artifacts
full local SQLite model databases
full model directories
secrets
```

Large artifacts stay local under `~/.smart-home/data/...`, but their paths, sizes, hashes if cheap, and concise summaries must be recorded in repo evidence.

## Validation requirement

The package validation command must check that holdout evidence files exist and contain required sections before the package is marked complete.

For P0034, validation must ensure at least:

```text
requirements/package-runs/P0034/holdout-results.md
requirements/package-runs/P0034/baseline-comparison.md
```

or equivalent files documented in design.

## P0034 immediate amendment

P0034 must update its evidence so that `baseline-comparison.md` or `holdout-results.md` includes explicit M1 holdout metrics for:

```text
SE1 system_proxy
SE3-SE1 area_diff_proxy
recomposed SE3
```

and includes model-vs-M1 comparisons for:

```text
hourly MAE/RMSE
level MAE/RMSE where applicable
curve-index MAE/RMSE where applicable
```

If pure-Python Ridge fallback is used because scikit-learn is unavailable, P0034 must classify the result as WARN unless it clearly beats required baselines and the fallback has been explicitly accepted as production-worthy.

## Expected Codex behavior

Before completing any ML/model package, Codex must:

```text
1. run holdout evaluation
2. run baseline evaluation on the same holdout split
3. persist all required metrics in repo evidence
4. classify PASS/WARN/STOP
5. mention the evidence paths in final output
```

Completion claims without persisted holdout evidence are incomplete.
