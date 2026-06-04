# P0054A Input Classification Taxonomy

| label | meaning |
|---|---|
| `forecast_safe` | Available at forecast time or deterministically known in advance. |
| `proxy` | Not truly available as used, but approximates a future feed in LABB. |
| `oracle_diagnostic` | Deliberately uses future truth to understand upper bound or mechanism. |
| `historical_observed_only` | Useful for explaining history, not directly available for future forecast. |
| `requires_separate_forecast_model` | Potentially useful but must itself be forecast before use. |
| `excluded_leakage` | Not allowed for model comparisons except explicitly labeled oracle diagnostics. |

Durable path:

```text
memory/energy-market-ai-lab.md
```
