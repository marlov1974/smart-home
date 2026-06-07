# Package P0056C Implementation Design

## Package

`P0056C`

## Package interpretation

Build a LABB multi-area consumption forecast layer using P0056A consumption targets and P0056B weather actual-proxy features. The default method is `HorizonBiasCorrected_WeightedEnsemble_no_price`, fitted per area using only train-fit and internal-validation rows before holdout.

## Chosen implementation structure

Add a package-scoped module:

```text
src/mac/services/spotprice_model_diagnostics/p0056c.py
```

The runner will:

1. Validate P0056A/P0056B area coverage.
2. Build forecast-origin modeling rows per area for 36 horizons.
3. Run two visible phases per area: `learn` and `test`.
4. Persist compact forecast-log and metrics tables in the local feature DB.
5. Write required P0056C evidence files and compact CSV/JSON summaries.

## Intended changes

### Files/modules to change

- `src/mac/services/spotprice_model_diagnostics/p0056c.py`: new package runner.
- `tests/mac/services/spotprice_model_diagnostics/test_p0056c.py`: split/leakage/progress/aggregation unit tests.
- `requirements/packages/P0056C-labb-multi-area-consumption-forecast.md`: completion status and notes.
- `requirements/package-runs/P0056C/**`: required evidence files.

### Files/modules intentionally not changed

- P0056A/P0056B builders remain unchanged.
- P0054R/P0055A logic remains unchanged and is reused.
- No Shelly, Home Assistant, deploy, API, or runtime files.

## Refactoring decisions

No broad refactor is planned. P0056C will import and reuse narrow helper functions from P0054R/P0055A where safe:

- P0054R origin construction and internal split policy.
- P0054R weighted ensemble and horizon-bias correction helpers.
- P0055A full-model/fallback fitting pattern.

P0056C will own area-specific target/weather loading because P0056A and P0056B schemas are different from the SE3-only historical helpers.

## Feature contract

Allowed feature families:

- calendar/time features
- holiday/weekend features
- historical area load lags
- rolling area load statistics
- P0056B area weather features

Forbidden feature families:

- spot price
- flow/exchange/net position
- A61/capacity/utilization
- old physical_balance target
- future actual load
- holdout-derived weighting or bias correction

Weather input is `weather_actual_proxy`, not production forecast weather.

## Output tables

If local DB write is allowed, create and populate:

```text
area_consumption_forecast_log_p0056c_v1
area_consumption_forecast_metrics_p0056c_v1
```

No model binaries or full prediction dumps are committed.

## Test strategy

Run:

```text
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056c
python3 -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056a tests.mac.services.spotprice_model_diagnostics.test_p0056b tests.mac.services.spotprice_model_diagnostics.test_p0056c
PYTHONPYCACHEPREFIX=/private/tmp/p0056c-pycache python3 -m src.mac.services.spotprice_model_diagnostics.p0056c
git diff --check
```

Equivalent checks must confirm:

- P0056A consumption input exists for all 18 areas.
- P0056B weather input exists for all 18 areas.
- split policy is applied.
- 36 learn/test jobs complete or checkpoint.
- all completed area results persist.
- no holdout fitting/selection.
- no forbidden features.
- aggregate forecast equals sum of area forecasts.
- leakage review passes.
- no large artifacts are staged.

## Build / generated artifact strategy

The package runner writes required Markdown evidence plus compact CSV/JSON summaries. It prints progress lines and appends them to `requirements/package-runs/P0056C/progress-log.md` after every job phase.

## Risks and uncertainties

- Runtime may be material because 18 per-area model fits are required.
- Optional ML backends may vary. If the full four-model ensemble cannot run for an area, P0056C will use the documented fallback order and record it.
- Weather input coverage currently ends at `2026-05-31T21:00Z`; evaluation cannot include later consumption-only rows.
- Fallback weather composites mean output is suitable for LABB emulator layers, not production forecast readiness.

## Design deviations during implementation

None yet.
