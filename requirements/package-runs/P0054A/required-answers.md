# P0054A Required Answers

1. Default label: `LABB`.
2. Only the human operator may request `G2-KANDIDAT` evaluation.
3. `LABB` allows clearly labeled proxies, oracle diagnostics, complex AI, counterfactuals, non-deployable datasets and failed experiments as learning evidence. `G2-KANDIDAT` requires forecast-safe/live-contracted inputs and runtime/fallback readiness.
4. Even in `LABB`, hidden leakage, unclassified proxies, weak baselines, holdout selection and vague interpretation are not allowed.
5. Long-term ambition: a deeply thought-through one-week-ahead Nordic/Swedish energy-market simulator that reasons from weather and balance through bottleneck/spread regimes to price forecasts and smart-home optimization candidates.
6. Future lab packages should use `requirements/packages/TEMPLATE-labb-experiment.md`.
7. Inputs are classified as `forecast_safe`, `proxy`, `oracle_diagnostic`, `historical_observed_only`, `requires_separate_forecast_model` or `excluded_leakage`.
8. A lab result can become a G2-KANDIDAT review only through a later package after stricter forecast-safe repetition, stress tests, feed contracts and explicit human request.
9. Recommended next lab package: `P0054B: Advanced AI lab for SE3-SE1 spread and bottleneck regimes`.
10. No runtime, device, API or model-training work was done.
