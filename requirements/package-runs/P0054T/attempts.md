# P0054T Attempts

## Attempt 1

Result: stopped during matrix execution.

Cause: P0054L2-compatible exact-origin price rows only provide train_fit coverage for the March-May 2025 blocked train-price interval, leaving the pre-March internal-train subset empty for price-mode validation weighting.

Fix: price-mode matrix branches now train final models on train_fit and use an explicit equal-weight/zero-bias fallback when internal validation weighting is unavailable for that price-origin coverage. This stays inside train_fit and does not use holdout for tuning.

## Attempt 2

Result: `PASS`.

Runtime: 524.743 seconds.

Completed all 12 summarized combinations and 36 seed/scenario rows with five W1 seeds.

No API, device, runtime, A61, flow, Nord Pool, workplace, old-target or future actual leakage actions were performed.
