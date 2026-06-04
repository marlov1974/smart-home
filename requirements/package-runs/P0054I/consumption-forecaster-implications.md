# P0054I Consumption Forecaster Implications

The next SE1 consumption ablation must train all compared models on:

```text
2022-06-01T00:00:00Z <= target_timestamp_utc < 2025-06-01T00:00:00Z
```

and report final metrics only on:

```text
target_timestamp_utc >= 2025-06-01T00:00:00Z
```

This applies to:

- SE1 no-price consumption models
- SE1 with P0054H forecast-safe price feature models
- future SE4 or spread/flaskhals consumption-response reruns that explicitly join this P0054 LABB chain

No holdout rows may be used for training, fitting, early stopping, feature normalization, hyperparameter selection or model selection.

For with-price features, use forecast-origin rows only. Do not use actual future spot prices.
