# Energy-Market AI Lab

P0054A sets the default label for energy-market, AI, spot-price, physical-balance and simulator work:

```text
energy_market_ai_default_label = LABB
```

`LABB` is the default until the human operator explicitly asks for `G2-KANDIDAT` evaluation.

## Labels

### LABB

`LABB` means research, learning and exploration mode.

Allowed in `LABB` when clearly documented:

- bold hypotheses and fast experiments
- realized weather used as a weather forecast proxy
- historical observed flow/exchange used for explanation
- oracle diagnostics that deliberately use future truth
- complex AI models and experimental feature engineering
- counterfactual and simulation ideas
- non-deployable datasets
- failures that teach something about the market

Still required in `LABB`:

- no hidden leakage
- every input classified by availability and leakage risk
- chronological train/validation/holdout discipline unless explicitly justified
- simple and strong benchmark comparisons
- reproducible package evidence
- clear interpretation of what was learned, not only which model had lowest MAE
- explicit statement that lab evidence is not runtime candidate evidence

### G2-KANDIDAT

`G2-KANDIDAT` means a lab result is being evaluated as a possible future G2 runtime/control candidate.

Only the human operator may request `G2-KANDIDAT` evaluation.

Additional requirements for `G2-KANDIDAT`:

- inputs are forecast-safe or have explicit live input contracts
- runtime freshness, stale handling and fallback behavior are defined
- serving path is deterministic or bounded
- failure behavior is clear
- no proxy or oracle dependency remains
- holdout and stress-period stability are sufficient
- no device/runtime side effects occur unless a separate package explicitly allows them

## Input Classification

Every non-trivial lab experiment must classify inputs:

| label | meaning | allowed use |
|---|---|---|
| `forecast_safe` | Available at forecast time or deterministically known in advance. | Allowed for lab and candidate work. |
| `proxy` | Not truly available as used, but approximates a future feed in `LABB`. | Allowed in `LABB`; not deployable without replacement. |
| `oracle_diagnostic` | Deliberately uses future truth to estimate upper bound or mechanism. | Allowed only when explicitly labeled as oracle. |
| `historical_observed_only` | Explains history but is not directly available for future forecasts. | Diagnostic/explanatory use only. |
| `requires_separate_forecast_model` | Potentially useful but must itself be forecast before future use. | Lab use if labeled; candidate use requires forecast model/contract. |
| `excluded_leakage` | Would leak target/future information into a model comparison. | Excluded except in explicitly marked oracle diagnostics. |

Realized weather may be used as `proxy` in `LABB`, labeled as actual-as-forecast proxy. Actual future spot price, target-window actual flow/exchange, future production, future consumption and target outcome values are `excluded_leakage` for ordinary model comparisons.

Historical observed A09/A11 flow/exchange may be `historical_observed_only` for market explanation and regime discovery. It becomes `requires_separate_forecast_model` if a future predictor wants to use it as an input.

## Benchmarks

Every non-trivial AI lab must compare against simple baselines unless the package explicitly justifies why not.

Default baselines:

- same-hour previous day/week
- calendar profile
- Ridge or linear model
- HGB or equivalent strong tabular benchmark
- simple rule/bucket model where relevant

Price, spread and regime work should include relevant metrics:

- MAE, RMSE, bias, sMAPE
- rank and Spearman
- top/bottom precision
- spike/regime precision, recall and F1
- 168h path metrics
- conditional metrics by hour, day, weekend, season, weather and regime

## Interpretation Categories

Reusable categories:

- `supports_hypothesis`
- `weak_support`
- `no_effect_detected`
- `contradicts_hypothesis`
- `model_learns_proxy_not_causal_signal`
- `inconclusive_due_to_data_or_proxy`
- `interesting_failure`
- `candidate_for_followup`
- `candidate_for_g2_review`

`candidate_for_g2_review` does not automatically mean `G2-KANDIDAT`. It means the human operator should decide whether to open a separate `G2-KANDIDAT` evaluation package.

## Promotion Path

Promotion path:

```text
LABB result
→ repeated under stricter forecast-safe assumptions
→ stress-tested across seasons/regimes
→ input feed contracts identified
→ runtime/fallback implications understood
→ human explicitly requests G2-KANDIDAT evaluation
→ separate package evaluates G2 fit
```

P0054A does not promote any existing result.
