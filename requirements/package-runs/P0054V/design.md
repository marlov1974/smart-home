# P0054V design

## Interpretation

P0054V answers whether SE3 spot-price information should be a default, conditional-only, or excluded feature for the SE3 consumption forecast. The active package includes the operator clarification: train_fit target-window price features may use historical actual SE3 spot, while holdout/inference future target-window price features must use forecasted SE3 spot. Actual spot history strictly before forecast origin is allowed as a 48h anchor.

The implementation is LABB-only and local. It must not call external APIs, touch devices, deploy runtime code, use A61/flow data, use old physical-balance consumption as target, or leak holdout target-window actual spot into features.

## Structure

Add `src/mac/services/spotprice_model_diagnostics/p0054v.py` as a package-scoped diagnostic module.

The module will:

1. Reproduce the P0054R no-price M1 baseline gate using temporary P0054R evidence.
2. Build the full P0054R source/direct/path row contract from corrected ENTSO-E SE3 actual load.
3. Load reconstructed actual SE3 spot history from `ai2_hour_to_day_training_targets_v2`.
4. Build package-local forecast-safe SE3 spot predictions for every P0054R origin/target row.
5. Add stitched price features:
   - actual target-hour spot for train_fit rows.
   - forecasted target-hour spot for holdout rows where target is at or after forecast origin.
   - actual spot only for timestamps strictly before forecast origin as history/anchor.
6. Fit M1 `HorizonBiasCorrected_WeightedEnsemble` for P0/P1/P2/P3/P4 feature families on identical full coverage.
7. Evaluate DayAhead, full_36h, daily-energy and regime metrics.
8. Write compact evidence under `requirements/package-runs/P0054V/`.

## Price forecast approach

Use the P0054L2/P0054N local feature and model pattern, not live API calls. Price forecast models are trained only on train_fit-safe historical spot examples. Holdout price predictions are generated from features whose source timestamps are strictly before each forecast origin. This is sufficient for P0054V's forecast-future side of the stitched path.

For train_fit rows, the primary consumption price feature uses actual historical SE3 spot for the target timestamp, as explicitly allowed by the operator clarification. Train-side thresholds and regimes are still learned only inside train_fit/internal validation.

## Feature families

P0: no price features from the P0054Q/P0054R no-price feature contract.

P1: raw stitched target-hour price and 48h actual anchor features.

P2: P1 plus path-shape features derived from the forecast future path and anchor.

P3: P2 plus train_fit-learned price regime flags.

P4: P3 plus forecast spike/ramp features.

Optional P5/P6 can be skipped if M1 complete evidence is already sufficient or runtime is high.

## Refactoring

Keep changes package-scoped. Reuse P0054R/P0054T4 helpers for M1 fitting/scoring and P0054L2/P0054N helpers for price forecast examples. Do not rewrite historical package modules.

## Tests

Add focused unit tests for:

- stitched price selection: train_fit actual target price, holdout forecast future price, and actual history before origin only.
- 48h anchor feature construction uses timestamps strictly before origin.
- full coverage check rejects missing stitched price rows.

Final verification commands:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0054v-pycache /usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054v
PYTHONPYCACHEPREFIX=/private/tmp/p0054v-pycache /usr/bin/python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054v.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054v-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054v
git diff --check
find requirements/package-runs/P0054V src/mac/services/spotprice_model_diagnostics tests/mac/services/spotprice_model_diagnostics docs/functions/mac -type f -size +1M -print
```

## Risks

P0054V intentionally trains price relationship on actual train_fit spot and evaluates holdout future horizons on forecasted spot. That skew is allowed by the clarification but must be treated as LABB evidence, not a final deployable feature contract.

Runtime may be high because M1 includes four base learners for each family. If needed, stop after P0/P1/P2/P3/P4 M1 evidence and record skipped optional branches as WARN.
