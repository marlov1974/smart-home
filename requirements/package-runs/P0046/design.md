# P0046 implementation design

## Package interpretation

P0046 builds a Mac-only anchored absolute-price historical backtest for the seven-day AI forecast track. The primary product question is whether P0045's selected SE1 168h shape (`combined_scaled`) can be anchored to known early spot hours and produce useful absolute forecasts for the remaining horizon.

## Implementation structure

Add a new diagnostics module:

```text
src/mac/services/spotprice_model_diagnostics/p0046.py
```

The module will:

- load P0042 corrected AI-1/AI-2 rows using P0045 helpers
- reuse P0045 deterministic regeneration of AI-1/AI-2 predictions
- build Monday 06:00 fixed-CET 168h forecast windows as the primary origin policy
- evaluate anchor scenarios A11, A16, A24 and A35
- fit deterministic anchor formulas L1, L2 and L3 on anchor hours only
- compare P0045 combined SE1 against flat, last-known, time-profile, AI1-only, AI2-only and oracle diagnostics
- write required P0046 evidence files

Add tests:

```text
tests/mac/services/spotprice_model_diagnostics/test_p0046.py
```

Update durable function catalog:

```text
docs/functions/mac/spotprice-model-diagnostics.md
```

## Intended changes

- New `p0046.py` module with constants, dataclasses, anchoring formulas, window construction, metrics and evidence writers.
- New tests covering anchor leakage, 168h windows, formula guardrails, validation/holdout split preservation and forbidden path constants.
- P0046 evidence files under `requirements/package-runs/P0046/`.
- Package status/completion notes in `requirements/packages/P0046-se1-anchored-absolute-price-backtest.md`.

## Intentionally not changed

- No P0043/P0044 model selection or retraining logic.
- No production forecast API or server module.
- No optimizer/control integration.
- No Shelly, Home Assistant, KVS, deploy artifacts or live device paths.
- No changes to P0045 evidence.

## Refactoring decisions

Reuse P0045 helpers instead of duplicating prediction regeneration and shape construction. P0046 may add small local adapters for Monday 06:00 windows because P0045's native windows start at fixed-CET day 00:00.

## Test strategy

Run package-scoped unit tests:

```bash
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0046
```

Run adjacent regression tests:

```bash
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0045
```

Run the package verification/backtest:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m src.mac.services.spotprice_model_diagnostics.p0046
```

Run final repository hygiene:

```bash
git diff --check
```

## Risks and uncertainties

- Local feature DB coverage may limit complete Monday 06:00 holdout windows. If primary coverage is insufficient, P0046 will report the coverage issue and use the package's diagnostic-origin allowance only if necessary.
- P0045 shape forecasts are centered shape signals, so anchored absolute performance depends heavily on whether early anchor hours identify the week level and scale.
- Area_diff/recomposed SE3 remains diagnostic only and must not override the SE1-first decision.
