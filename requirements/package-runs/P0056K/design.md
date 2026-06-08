# P0056K Implementation Design

## Package Interpretation

P0056K restarts the consumption forecast comparison under a realistic DayAhead market-emulator protocol.

The first robust baseline uses `DA-L3 seasonal_safe` features:

- calendar/holiday/time features for target hours
- previous-week and previous-two-week same-hour consumption
- origin-known load history and rolling statistics before forecast origin
- actual-weather proxy features for target hours, clearly labeled LABB proxy

No target-window actual load is used in primary features.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0056k.py`.

The module supports:

- `run`: long-running package execution
- `status`: print current progress from evidence files

Runtime state/evidence:

- `progress-log.md` appended throughout execution
- `job-status.csv` machine-readable progress by area/model
- `job-status.md` human-readable status
- `checkpoint-resume.md` with resume/poll commands
- compact result CSV/Markdown/JSON

## Model Set

Required practical set:

- M0 seasonal naive previous-week same-hour
- M1 Ridge
- M2 HGB
- M3 ExtraTrees
- M4 LightGBM if dependency is available
- M5 XGBoost if dependency is available
- M6 WeightedEnsemble_no_price from completed base model predictions
- M7 HorizonBiasCorrected_WeightedEnsemble_no_price using only prior-origin residuals where available

Neural models are skipped and documented.

## Checkpointing

The run writes one job-status row per area/model outcome. It can be polled with:

```text
PYTHONPYCACHEPREFIX=/private/tmp/p0056k-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056k status
```

## Test Strategy

- Unit-test DayAhead origin construction.
- Unit-test that generated lag feature names are forecast-safe and do not use target-window actual load.
- Compile the module.
- Start/monitor the long run.
- Verify required evidence and `git diff --check`.

## Risks and Uncertainties

- Runtime may be long because models are refit per area/model/origin.
- Optional LightGBM/XGBoost may be unavailable or slow.
- Actual-weather proxy means results are LABB-only.
- DA-L2 recursive lagging is deferred to a later package.
