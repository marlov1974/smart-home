# P0056F Implementation Design

## Package Interpretation

Test cumulative weather feature stacks W0-W12 for SE1 and SE2 using P0056D weather features. Keep all non-weather features fixed so the experiment isolates marginal weather signal value.

## Implementation Structure

Create:

```text
src/mac/services/spotprice_model_diagnostics/p0056f.py
tests/mac/services/spotprice_model_diagnostics/test_p0056f.py
```

P0056F will reuse P0056C row building and model helpers. It will use P0056D weather rows for SE1/SE2, build one base row set per area, and run `HorizonBiasCorrected_WeightedEnsemble_no_price` for each weather stack W0-W12.

## Intended Changes

- Add P0056F runner and unit tests.
- Add P0056F package-run evidence.
- Fill P0056F completion notes after verification.
- Create P0056F local SQLite forecast/metrics tables.

## Deliberate Refactoring Decisions

- Do not alter P0056C/D/E behavior.
- Keep P0056F helpers package-local.
- Do not run optional SE3 or optional area-specific methods unless the required W0-W12 pass is complete and runtime budget clearly remains.

## Test Strategy

Run:

```bash
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056f
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056e tests.mac.services.spotprice_model_diagnostics.test_p0056f
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056f
git diff --check
```

Verification also checks:

- W0-W12 constructed in exact order.
- Non-weather features are identical across stacks.
- P0056F DB rows exist for SE1 and SE2.
- Leakage review passes.

## Risks And Uncertainties

- Runtime is expected to be several minutes because 26 HBC ensemble fits are required.
- Snow depth is unavailable in P0056D weather and should be documented as an added-but-uninformative feature.
- Holdout peak choice remains LABB exploratory, not production selection.
