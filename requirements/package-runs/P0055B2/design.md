# P0055B2 implementation design

## Package interpretation

P0055B2 redoes P0055B under the operator clarification. The purpose is not to build a production model, but to test whether a better forecast-safe allocation normalization makes the SE3 decomposition forecast useful.

## Implementation structure

Add:

```text
src/mac/services/spotprice_model_diagnostics/p0055b2.py
tests/mac/services/spotprice_model_diagnostics/test_p0055b2.py
```

The implementation will reuse P0055A/P0055B data loading, normalization persistence and forecast helpers where the old logic remains valid.

## Intended changes

- Add pure-Python PAVA/isotonic monotone non-decreasing share fitting per non-zero cluster.
- Fit only on `train_fit` months.
- Use latest stable train-fit reference window, defaulting to the last three train-fit months.
- Keep holdout allocation reference fixed from that train-fit window.
- Compute residual share as the remaining share after fitted clusters, preserving total share sum.
- Normalize hourly components by fitted monthly share to reference share and renormalize per hour to SE3 total.
- Write the four operator-required evidence files plus updated monotonicity, leakage, DB and comparison evidence.

## Deliberate refactoring decisions

The new package gets its own module instead of rewriting P0055B in place. That preserves the historical P0055B run and keeps the stronger operator clarification traceable.

No shared package refactor is planned unless a helper is needed for testability.

## Test strategy

Unit tests cover:

- PAVA output is non-decreasing and can contain jumps/flat stretches.
- Cluster delta metrics include the operator-required fields.
- Reference window ignores holdout months.
- Normalization preserves hourly SE3 total.
- Leakage review rejects holdout fitting/reference usage.

Full package verification will run the P0055B2 module and compare normalized decomposition metrics against direct SE3 and P0055A raw decomposition.

## Risks and uncertainties

- If observed cluster shares are materially decreasing, a non-decreasing fit is a diagnostic correction rather than proof of true migration.
- If many clusters are noisy, `WARN` remains the appropriate result even if normalized decomposition improves raw decomposition.
- The forecast remains LABB because weather uses historical actual-as-proxy inputs.
