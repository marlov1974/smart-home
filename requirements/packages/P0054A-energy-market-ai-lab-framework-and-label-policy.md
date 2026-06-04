# Package P0054A: Energy-market AI lab framework and label policy

## Status

planned

## Package order

P0054A

## Primary area

G2 / Mac tooling / spotprice V2 / energy-market simulator / AI lab governance / lab labeling / experiment framework / market-model research

## Decision summary

Smart Home G2 remains the long-term production target for a smart home control environment.

The current energy-market, spot-price, physical-balance and AI workstream is now explicitly classified as a research/lab workstream unless the human operator says otherwise.

Default label from this package onward:

```text
LABB
```

A package, experiment or model may be treated as:

```text
G2-KANDIDAT
```

only when the human operator explicitly asks for that classification or asks to evaluate promotion toward G2 runtime use.

The purpose of the LABB workstream is not only to minimize error metrics. It is to learn how to model the Nordic/Swedish energy market with a speed, openness and lack of legacy assumptions that large traditional organizations may not have.

Long-term research ambition:

```text
Build a deeply thought-through energy-market simulator that can predict how the market will behave one week ahead with enough accuracy to become one of the strongest spot-price forecast approaches available for the use case.
```

This package creates the governance, vocabulary, evidence structure and experiment standards for that lab.

## Why this exists

The project owner wants to learn AI and complex energy-market simulation at a level that historically would have required a dedicated research department.

The lab should therefore allow:

```text
- bold hypotheses
- fast experiments
- complex AI trials
- proxies when clearly labeled
- counterfactual simulation
- physical-market reasoning
- systematic comparison against strong simple baselines
- learning even from failed experiments
```

The lab must not become vague or hand-wavy. Every experiment must preserve enough discipline to avoid false conclusions.

## Label system

Create and document two labels:

### LABB

Meaning:

```text
Research, learning and exploration mode.
```

Allowed in LABB when explicitly documented:

```text
- realized weather used as weather-forecast proxy
- historical observed flow/exchange used for explanatory diagnostics
- oracle diagnostics clearly marked as oracle
- complex AI models
- experimental feature engineering
- alternative target definitions
- counterfactual/simulation ideas
- non-deployable datasets
```

Still required in LABB:

```text
- no hidden leakage
- explicit proxy/oracle/forecast-safe classification
- baseline comparison
- chronological split discipline
- reproducible evidence
- clear interpretation of what was learned
```

### G2-KANDIDAT

Meaning:

```text
A lab result is being evaluated as a possible future G2 runtime/control candidate.
```

Additional requirements for G2-KANDIDAT:

```text
- forecast-safe inputs or explicit live input contract
- runtime freshness and fallback behavior
- deterministic serving path or bounded model runtime
- clear failure behavior
- no oracle/proxy dependency
- sufficient stability across holdout and stress periods
- no device/runtime side effects unless separately packaged
```

P0054A must set:

```text
energy_market_ai_default_label = LABB
```

and must document:

```text
Only the human operator may explicitly promote an experiment/package to G2-KANDIDAT evaluation.
```

## Scope

P0054A owns:

```text
1. Create durable lab/governance memory for the energy-market AI workstream.
2. Create a reusable experiment template for LABB packages.
3. Add label terminology and default-label rules to future package guidance.
4. Define proxy/oracle/forecast-safe classification rules for lab experiments.
5. Define benchmark and evidence requirements for advanced AI experiments.
6. Define how a lab result may later be promoted toward G2-KANDIDAT review.
7. Define first recommended follow-up AI lab package(s).
```

## Hard non-goals

P0054A must not:

```text
- train an AI model
- change any production/runtime control behavior
- deploy anything to Mac/Home Assistant/Shelly runtime
- call Shelly/Home Assistant/KVS/devices
- ingest new external market data
- create forecast API
- change existing P0053 results
- mark any existing experiment as G2-KANDIDAT unless explicitly requested
```

P0054A is governance, documentation and experiment-framework only.

## Required memory/policy artifacts

Create or update durable files, recommended:

```text
memory/energy-market-ai-lab.md
memory/energy-market-simulator-ambition.md
requirements/packages/TEMPLATE-labb-experiment.md
```

If existing memory conventions suggest better file names, use them and document the paths.

### `memory/energy-market-ai-lab.md` must include

```text
- LABB is default for energy-market/AI/forecast experiments.
- G2-KANDIDAT requires explicit human request.
- Difference between learning evidence and runtime candidate evidence.
- Required classification of every input as forecast_safe, proxy, oracle, historical_observed_only, or excluded_leakage.
- Rules for realized weather as proxy.
- Rules for actual future price/flow/consumption leakage.
- Benchmark expectations.
- Experiment interpretation categories.
```

### `memory/energy-market-simulator-ambition.md` must include

```text
- long-term simulator ambition
- market reasoning stack
- speed/no-legacy principle
- desired simulator qualities
- why failures are useful
- why simple baselines remain mandatory
- why complex AI is allowed in lab
```

Suggested market reasoning stack:

```text
weather / calendar / season
→ consumption and production
→ local balance by bidding zone
→ import/export demand as supply/demand terms
→ internal Swedish flow/exchange pressure
→ external export/import pressure
→ bottleneck/spread regimes
→ price-shape and absolute price forecast
→ smart-home optimization candidates
```

## Required experiment template

Create a reusable LABB experiment package template with sections:

```text
Label
Hypothesis
Learning objective
Target
Dataset and period
Input classification
Proxy/oracle policy
Forecast-safety notes
Baselines
AI/ML models to test
Evaluation splits
Metrics
Conditional/regime metrics
Interpretation categories
What would change our understanding?
Promotion criteria toward G2-KANDIDAT
Forbidden shortcuts
Evidence files
Required answers
Tests
```

The template must encourage experiments to answer:

```text
What did we learn about the market?
```

not only:

```text
Which model had the lowest MAE?
```

## Input classification taxonomy

P0054A must define these labels:

```text
forecast_safe
proxy
oracle_diagnostic
historical_observed_only
requires_separate_forecast_model
excluded_leakage
```

Definitions:

```text
forecast_safe:
  available at forecast time or deterministically known in advance.

proxy:
  not truly available as used, but used to approximate a future feed in LABB.

oracle_diagnostic:
  deliberately uses future truth to understand theoretical upper bound or mechanism.

historical_observed_only:
  useful for explaining history, not directly available for future forecast.

requires_separate_forecast_model:
  potentially useful but must itself be forecast before use in a future model.

excluded_leakage:
  not allowed for model comparisons except explicitly labeled oracle diagnostics.
```

## Benchmark requirements

Every non-trivial AI lab must compare against simple baselines unless the package explicitly explains why not.

Default baselines:

```text
same-hour previous day/week
calendar profile
Ridge/linear model
HGB or equivalent strong tabular benchmark
simple rule/bucket model where relevant
```

For price/spread/regime work, include appropriate metrics:

```text
MAE/RMSE/bias/sMAPE
rank/spearman
top/bottom precision
spike/regime precision/recall/F1
168h path metrics
conditional metrics by hour/day/weekend/season/weather/regime
```

## Interpretation categories

P0054A must define reusable interpretation categories:

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

`candidate_for_g2_review` must not automatically mean G2-KANDIDAT. It means the human should decide whether to open a G2-KANDIDAT evaluation package.

## Advanced AI allowance

P0054A should explicitly allow advanced AI in LABB, including:

```text
- RandomForest / ExtraTrees
- HGB / LightGBM / XGBoost if dependency-safe
- small neural networks
- LSTM/GRU
- TCN
- simple transformer-style sequence models if dependency-safe
- representation/embedding experiments
- hybrid physics + ML models
```

But every such model must still document:

```text
- data leakage controls
- train/validation/holdout discipline
- baseline comparison
- where it improves or fails
- what it teaches about the energy market
```

## Promotion path toward G2-KANDIDAT

Define a later promotion path:

```text
LABB result
→ repeated under stricter forecast-safe assumptions
→ stress-tested across seasons/regimes
→ input feed contracts identified
→ runtime/fallback implications understood
→ human explicitly requests G2-KANDIDAT evaluation
→ separate package evaluates G2 fit
```

P0054A must not promote anything by itself.

## First follow-up recommendation

P0054A should recommend the next experiment package:

```text
P0054B: Advanced AI lab for SE3-SE1 spread and bottleneck regimes
```

Possible first targets:

```text
- SE3-SE1 spread regression
- SE3-SE1 regime classification: low / normal / high / spike
- bottleneck persistence / transition modeling
- 168h path of spread regimes
```

Candidate inputs:

```text
- weather/calendar/daytype
- P0051 production/consumption/net-load
- P0053A A09/A11 internal flow/exchange actuals as historical_observed_only diagnostics
- forecasted/proxy consumption/production where available
- M4 anchored SE1 price forecast
- flow-based flag
- lag/rollup/hink features
```

## Required evidence files

P0054A must create:

```text
requirements/package-runs/P0054A/CHANGELOG.md
requirements/package-runs/P0054A/review.md
requirements/package-runs/P0054A/design.md
requirements/package-runs/P0054A/functions.md
requirements/package-runs/P0054A/lab-label-policy.md
requirements/package-runs/P0054A/energy-market-simulator-ambition.md
requirements/package-runs/P0054A/input-classification-taxonomy.md
requirements/package-runs/P0054A/labb-experiment-template.md
requirements/package-runs/P0054A/promotion-path-to-g2-candidate.md
requirements/package-runs/P0054A/next-package-recommendation.md
requirements/package-runs/P0054A/component-attribution-summary.md
```

No code evidence is required unless implementation creates helper constants/templates.

## Required answers

P0054A must explicitly answer:

```text
1. What is the default label for energy-market/AI experiments?
2. Who may change a LABB item into G2-KANDIDAT evaluation?
3. What does LABB allow that G2-KANDIDAT would not allow?
4. What must still be controlled even in LABB?
5. What is the long-term energy-market simulator ambition?
6. What template should future lab packages use?
7. How are proxy/oracle/forecast-safe inputs classified?
8. How can a lab result later become a G2-KANDIDAT review?
9. What is the recommended next lab package?
10. Confirm no runtime/device/API/model training work was done.
```

## Tests / verification

Required checks:

```text
- durable lab policy file exists
- simulator ambition file exists
- LABB template exists
- default LABB rule is stated clearly
- G2-KANDIDAT requires explicit human request
- input classification taxonomy is present
- promotion path is present
- no runtime/device/API/model training files changed unless deliberately documented as template/helper only
```

## Pass/fail interpretation

PASS requires:

```text
- LABB/G2-KANDIDAT label policy documented
- LABB default documented
- simulator ambition documented
- lab experiment template created
- proxy/oracle/forecast-safe taxonomy documented
- next lab package recommendation explicit
- no runtime/device/model-training side effects
```

WARN is acceptable if:

```text
- template location differs from recommended path but is documented
- some package guidance still needs later update
```

STOP if:

```text
- Codex attempts to train models or change runtime behavior in P0054A
- label policy conflicts with existing G2/G1 boundary
- G2-KANDIDAT is made default without explicit human request
```

## Expected Codex output

- PASS/WARN/STOP status
- files created/updated
- summary of LABB default policy
- summary of simulator ambition
- template path
- next-package recommendation
- tests/checks run
- confirmation of no API/device/runtime/model-training work
- commit SHA after push

## Completion notes

To be filled after implementation.
