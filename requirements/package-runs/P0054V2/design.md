# P0054V2 design

## Interpretation

P0054V2 reruns the P0054V complete SE3 consumption spotprice value test with a relaxed but explicit baseline gate. It must answer whether price should be a default, conditional-only, or excluded feature for generic SE3 consumption forecasting, and whether price should still continue into market-emulator layers.

## Implementation Structure

Create `src/mac/services/spotprice_model_diagnostics/p0054v2.py`.

The module will:

1. Reproduce the P0054R no-price baseline using a temporary evidence directory.
2. Apply P0054V2's relaxed baseline gate.
3. Build the full corrected ENTSO-E SE3 consumption P0054R row/origin contract.
4. Load reconstructed SE3 actual spot history locally from `ai2_hour_to_day_training_targets_v2` through P0054L2/P0054K helpers.
5. Build a full holdout forecast-safe SE3 spot forecast source for every P0054R holdout origin/target row without requiring actual holdout target-window spot.
6. Attach stitched price features:
   - train_fit target-hour actual spot.
   - holdout target-hour forecast spot.
   - 48h actual-history anchor strictly before origin.
7. Evaluate M1 `HorizonBiasCorrected_WeightedEnsemble` for P0/P1/P2/P3/P4 on identical full coverage.
8. Write required evidence and compact CSV/JSON summaries.

## Feature Families

P0: P0054Q/P0054R no-price feature contract.

P1: raw stitched target-hour price plus actual 48h anchor.

P2: P1 plus path/daily shape features.

P3: P2 plus train_fit-learned regime flags.

P4: P3 plus spike/ramp features.

Optional P5/P6/M2/M3/weather-noise repeats are skipped unless M1 completes cheaply enough. This is acceptable WARN if skipped, but P0054V2 should still PASS when required M1 families complete.

## Safety

Holdout target-window actual spot is never used as a feature. The holdout price forecast feature matrix uses only history strictly before each origin. Regime thresholds are learned from train_fit rows only. Holdout is final evaluation only.

## Tests

Add focused tests for:

- relaxed baseline gate.
- stitched train/holdout price selection.
- actual 48h anchor source timestamps strictly before origin.
- coverage summary rejects missing stitched price rows.

Verification commands:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0054v2-pycache /usr/bin/python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0054v2
PYTHONPYCACHEPREFIX=/private/tmp/p0054v2-pycache /usr/bin/python3 -m py_compile src/mac/services/spotprice_model_diagnostics/p0054v2.py
PYTHONPYCACHEPREFIX=/private/tmp/p0054v2-pycache /usr/bin/python3 -m src.mac.services.spotprice_model_diagnostics.p0054v2
git diff --check
find requirements/package-runs/P0054V2 src/mac/services/spotprice_model_diagnostics tests/mac/services/spotprice_model_diagnostics docs/functions/mac -type f -size +1M -print
```

## Risks

The train/inference spotprice skew is intentional and package-authorized, but the result should remain LABB. A future stricter package may need out-of-fold train-period price forecasts before any G2-KANDIDAT promotion.
