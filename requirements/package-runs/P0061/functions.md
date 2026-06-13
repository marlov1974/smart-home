# P0061 Function Design

## New Functions

None.

## Changed Functions

No function behavior is intentionally changed.

## Removed From G2 Ownership

The following function catalogs move from G2 ownership to Market-Simulator ownership:

- `docs/functions/mac/spot-forecast.md`
- `docs/functions/mac/spotprice-history.md`
- `docs/functions/mac/weather-history-dataset.md`
- `docs/functions/mac/spotprice-temperature-normalization.md`
- `docs/functions/mac/spotprice-ml-normal-model.md`
- `docs/functions/mac/spotprice-model-diagnostics.md`
- `docs/functions/mac/swedish-special-day-calendar.md`
- `docs/functions/mac/weekly-home-optimizer-poc.md`

## Side Effects

G2 imports/tests that depended on moved modules are removed with the modules. Market-Simulator keeps the original import namespace for compatibility.

## Test Coverage

Verification is migration-focused: remaining G2 tests must still pass and migrated Market-Simulator smoke tests must import/run under preserved paths.
