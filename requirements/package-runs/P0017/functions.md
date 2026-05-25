# P0017 Function Design

## Mac Service: `src.mac.services.spot_forecast.schema`

### `parse_week`

- Status: new
- Purpose: validate the API/CLI week argument.
- Inputs: raw string or missing value.
- Outputs: integer ISO week 1..53.
- Side effects: none.
- Test coverage: invalid, missing, non-numeric and out-of-range API tests.

### `compact_json`

- Status: new
- Purpose: encode compact JSON responses with stable separators.
- Inputs: JSON-serializable value.
- Outputs: compact JSON string.
- Side effects: none.
- Test coverage: contract shape tests assert array-only output and no metadata.

## Mac Service: `src.mac.services.spot_forecast.model`

### `SpotForecastError`

- Status: new
- Purpose: base package exception for invalid source/model state.
- Inputs: error message.
- Outputs: exception instance.
- Side effects: none.
- Test coverage: invalid source shape tests through loader/model helpers where relevant.

### `WeekNotFoundError`

- Status: new
- Purpose: signal valid but unmodelable week input.
- Inputs: target week.
- Outputs: exception instance.
- Side effects: none.
- Test coverage: missing model data tests.

### `HistoricalWeek`

- Status: new
- Purpose: immutable record for one historical week and its 21 indexes.
- Inputs: ISO year, ISO week, 21 indexes.
- Outputs: dataclass instance.
- Side effects: none.
- Test coverage: model tests use fixture records.

### `load_history`

- Status: new
- Purpose: load and validate the committed historical JSON source.
- Inputs: optional path.
- Outputs: list of `HistoricalWeek`.
- Side effects: reads local JSON file.
- Test coverage: source loading and standard-library import tests.

### `week_weight`

- Status: new
- Purpose: implement P0017 distance weights.
- Inputs: distance integer.
- Outputs: weight float.
- Side effects: none.
- Test coverage: TC3 weight tests.

### `weighted_average_indexes`

- Status: new
- Purpose: compute the unnormalized 21-period weighted average.
- Inputs: target week and historical records.
- Outputs: 21 floats.
- Side effects: none.
- Test coverage: TC3 model contribution tests.

### `normalize_indexes`

- Status: new
- Purpose: normalize a 21-value vector to arithmetic mean 1.0.
- Inputs: 21 floats.
- Outputs: 21 normalized floats.
- Side effects: none.
- Test coverage: TC4 normalization tests.

### `round_indexes`

- Status: new
- Purpose: round public output to two decimals.
- Inputs: 21 floats.
- Outputs: 21 rounded floats.
- Side effects: none.
- Test coverage: TC2 rounding tests.

### `forecast_period_indexes`

- Status: new
- Purpose: full public model operation for one target week.
- Inputs: target week and optional historical records.
- Outputs: 21 rounded floats.
- Side effects: reads source data only when records are not supplied.
- Test coverage: model and CLI/API tests.

## Mac Service: `src.mac.services.spot_forecast.server`

### `build_handler`

- Status: new
- Purpose: create an HTTP handler bound to a history dataset.
- Inputs: historical records.
- Outputs: `BaseHTTPRequestHandler` subclass.
- Side effects: none until used by HTTP server.
- Test coverage: API tests using an in-process HTTP server.

### `run_once`

- Status: new
- Purpose: deterministic CLI verification path that prints one compact response.
- Inputs: week argument and optional output stream.
- Outputs: process-style integer return code.
- Side effects: writes stdout/stderr.
- Test coverage: CLI-style tests.

### `serve`

- Status: new
- Purpose: run the local trusted HTTP service.
- Inputs: host, port and optional historical records.
- Outputs: none until interrupted.
- Side effects: opens local HTTP listener.
- Test coverage: lower-level handler tests cover HTTP behavior; persistent loop is not run in unit tests.

### `main`

- Status: new
- Purpose: CLI entry point for `--once` and service modes.
- Inputs: argv.
- Outputs: process exit code.
- Side effects: prints output or starts HTTP server.
- Test coverage: direct main/run-once tests and package verification command.

## Cross-Package Catalog Updates

- Add `docs/functions/mac/spot-forecast.md` after implementation because the Mac spot forecast service is a durable contract provider for future planner packages.
