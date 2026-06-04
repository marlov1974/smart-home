# Package P____: <LABB experiment name>

## Status

planned

## Package order

P____

## Label

```text
LABB
```

Use `G2-KANDIDAT` only when the human operator explicitly requests evaluation for possible G2 runtime/control use.

## Hypothesis

What market, price, spread, consumption, production or regime hypothesis is being tested?

## Learning Objective

What should we learn about the market even if the model fails?

## Target

Define target, unit, source table/file and timestamp semantics.

## Dataset And Period

Define row construction, coverage, train/validation/holdout policy and any skipped periods.

## Input Classification

Classify every input:

| input | source | classification | reason | future-use note |
|---|---|---|---|---|
|  |  | `forecast_safe` / `proxy` / `oracle_diagnostic` / `historical_observed_only` / `requires_separate_forecast_model` / `excluded_leakage` |  |  |

## Proxy/Oracle Policy

State which proxies or oracle diagnostics are used and why they are allowed in `LABB`.

## Forecast-Safety Notes

Identify what would need to change before any future `G2-KANDIDAT` review.

## Baselines

Include simple and strong baselines such as same-hour previous day/week, calendar profile, Ridge/linear, HGB and relevant rule/bucket models.

## AI/ML Models To Test

List models and why each belongs in the experiment.

## Evaluation Splits

Define train/validation/holdout and whether holdout is report-only.

## Metrics

Include aggregate metrics and path metrics when relevant.

## Conditional/Regime Metrics

Define spike, top/bottom, bottleneck, weather, holiday, weekend, season or regime subsets.

## Interpretation Categories

Choose from:

```text
supports_hypothesis
weak_support
no_effect_detected
contradicts_hypothesis
model_learns_proxy_not_causal_signal
inconclusive_due_to_data_or_proxy
interesting_failure
candidate_for_followup
candidate_for_g2_review
```

## What Would Change Our Understanding?

State the evidence threshold that would change the next package or market model.

## Promotion Criteria Toward G2-KANDIDAT

Define what would be needed before asking the human operator for `G2-KANDIDAT` evaluation.

## Forbidden Shortcuts

Forbid hidden leakage, unclassified proxies, holdout selection, production/runtime changes and unsupported causal claims.

## Evidence Files

List required package-run files.

## Required Answers

Every LABB experiment should answer:

1. What did we learn about the market?
2. Did the result support the hypothesis?
3. Which baseline was hardest to beat?
4. Which inputs were forecast-safe, proxy, oracle, historical-only or leakage-excluded?
5. Which regimes or conditions changed the result?
6. What is the next experiment?
7. Is this only LABB, or should the human consider G2-KANDIDAT review?

## Tests

List verification checks for data coverage, split discipline, input classification, leakage controls, baseline fairness and evidence completeness.
