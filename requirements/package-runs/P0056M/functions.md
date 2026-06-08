# P0056M Function Design

## Package

`P0056M`

## Scope

Mac-side LABB diagnostics for SE2 M6 realistic DayAhead error slice analysis.

## New functions

### `run_p0056m_error_slice_analysis()`

Purpose: Reconstruct SE2 M6 P0056K DayAhead predictions, compute day/hour metrics, write required evidence.

Inputs: Optional feature DB path and evidence directory.

Outputs: Result object with status, row counts and evidence paths.

Side effects: Writes package-run evidence files only.

Reason: Package entry point.

Tests: Module execution plus unit coverage of pure helper functions.

### `reconstruct_se2_m6_predictions()`

Purpose: Reuse P0056K model logic to generate per-hour M6 predictions for SE2 only.

Inputs: SE2 target rows, SE2 weather rows and origins.

Outputs: Day rows, hour rows and reconstruction failures.

Side effects: None except optional progress writes by caller.

Reason: P0056K did not persist hour-level prediction dump.

Tests: Verified through generated baseline comparison; pure supporting helpers are unit tested.

### `load_p0056d_weather()`

Purpose: Wrap P0056D area-weather loading for the SE2 actual-weather proxy source used by P0056K.

Inputs: SQLite connection.

Outputs: P0056D weather rows and source contract.

Side effects: None.

Reason: Keeps the P0056M runner explicit about its inherited weather source.

Tests: Covered by module execution.

### `build_day_metrics()`

Purpose: Convert 24 hourly prediction rows for one delivery day into package-required day-level metrics.

Inputs: Origin descriptor and hourly rows.

Outputs: Day-level metric dictionary.

Side effects: None.

Reason: Required day-level forecast quality evidence.

Tests: Unit-tested with synthetic hourly rows.

### `build_hour_rows()`

Purpose: Create compact hour-level rows containing target timestamp, horizon, actual, forecast, error and context.

Inputs: P0056K forecast rows, predictions and origin.

Outputs: Hour-level row dictionaries.

Side effects: None.

Reason: Required hour-level quality inputs.

Tests: Covered indirectly by day metrics and module run.

### `slice_summary()`

Purpose: Aggregate MAE, bias, daily energy error and counts for requested slice dimensions.

Inputs: Day or hour rows and a grouping key.

Outputs: Sorted list of slice metric dictionaries.

Side effects: None.

Reason: Required weekday/month/season/temperature/load/ramp/horizon/local-hour slices.

Tests: Unit-tested with synthetic rows.

### `top_bottom_tests()`

Purpose: Rank five best and five worst DayAhead tests by hourly MAE and daily energy error.

Inputs: Day-level metric rows.

Outputs: Top and bottom row lists with rank and explanation candidate.

Side effects: None.

Reason: Required readable best/worst evidence.

Tests: Unit-tested with synthetic rows.

### `interpret_patterns()`

Purpose: Produce explicit answers to the package's twelve interpretation questions.

Inputs: Slice summaries, top/bottom rows and aggregate metrics.

Outputs: Pattern review and decision dictionaries/Markdown.

Side effects: None.

Reason: Required human-readable interpretation.

Tests: Verified through generated evidence; supporting classification helpers are unit-tested.

## Changed functions

None planned.

## Removed functions

None planned.

## Important unchanged functions

### `p0056k.dayahead_origins()`

Reason for no change: Defines the P0056K realistic DayAhead origin protocol; changing it would break package comparability.

### `p0056k.build_dayahead_rows()`

Reason for no change: Owns P0056K forecast-safe feature row construction; reused unchanged.

### `p0056k.weighted_ensemble_predictions()`

Reason for no change: Owns M6 behavior; reused unchanged.

### `p0056k.score_origin()`

Reason for no change: Owns P0056K aggregate metric calculation; used to verify reconstructed baseline.

## Design deviations during implementation

None yet.
