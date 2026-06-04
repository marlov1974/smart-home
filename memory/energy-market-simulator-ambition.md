# Energy-Market Simulator Ambition

The long-term lab ambition is to build a deeply thought-through energy-market simulator that can predict how the Nordic/Swedish market will behave one week ahead with enough accuracy to become one of the strongest spot-price forecast approaches available for the smart-home use case.

This is a `LABB` ambition by default. It is not a G2 runtime/control commitment.

## Why The Lab Exists

The project should learn energy-market AI and complex simulation with the speed and openness of a focused lab, without inheriting legacy assumptions from large traditional organizations. The goal is not only lower error metrics. The goal is to understand market mechanisms well enough to build better forecasts, better experiments and eventually better smart-home optimization candidates.

## Market Reasoning Stack

Suggested reasoning stack:

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

## Desired Simulator Qualities

A useful simulator should:

- explain market behavior in terms of physical and economic pressure, not only fit curves
- separate forecast-safe inputs from proxies, oracles and historical observations
- model bidding-zone balances and spread regimes
- handle 168h paths, not only independent hourly points
- expose conditional behavior during spikes, bottlenecks, weekends, holidays and weather regimes
- produce evidence that can be compared against simple baselines
- be reproducible enough for package review
- make failed hypotheses useful by identifying which market assumption broke

## Speed And No-Legacy Principle

The lab may move quickly and test advanced methods because it is not production runtime. It should avoid inherited assumptions when data and evidence suggest a better model. Fast iteration is allowed, but conclusions must stay disciplined.

## Complex AI In LABB

Advanced AI is allowed in `LABB`, including:

- RandomForest and ExtraTrees
- HGB, LightGBM or XGBoost when dependency-safe
- small neural networks
- LSTM and GRU
- TCN
- simple transformer-style sequence models when dependency-safe
- representation and embedding experiments
- hybrid physics plus ML models

Each experiment must still document leakage controls, train/validation/holdout discipline, baseline comparison, where the model improves or fails, and what it teaches about the energy market.

## Why Simple Baselines Remain Mandatory

Simple baselines prevent false confidence. If an advanced model cannot beat same-hour previous week, a calendar profile, Ridge or HGB under fair conditions, the lab should learn why before making larger claims.

## Why Failures Are Useful

Failures can reveal:

- wrong causal assumptions
- proxy dependence
- missing forecast inputs
- regime instability
- insufficient target definition
- overfitting to rare events
- inputs that require separate forecasting before they can be useful

An interesting failure is a valid lab outcome when it changes the next hypothesis.
