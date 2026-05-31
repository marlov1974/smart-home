# P0040 Function Design

## New Functions

### `run_p0040_analysis(...)`

- Purpose: orchestrate weekly anchored backtest, evidence generation and result status.
- Inputs: DB paths and evidence directory.
- Outputs: `P0040Result`.
- Side effects: writes package-run evidence files.
- Test coverage: exercised by module verification.

### `forecast_origins(rows, start_date, end_date)`

- Purpose: find eligible Monday 06 forecast origins with 16 known spot hours and 168 horizon hours.
- Inputs: diagnostic rows and date bounds.
- Outputs: origin descriptors with skipped reasons excluded from comparisons.
- Side effects: none.
- Test coverage: Monday origin, 16h context and 168h horizon tests.

### `fit_static_strict_components(rows)`

- Purpose: fit M1, M1B, existing M3A/M3B, M1B-trained M3A/M3B, M3C/M3D and optional M4_area using strict pre-backtest training windows.
- Inputs: diagnostic rows.
- Outputs: mutates scored row dictionaries with component predictions.
- Side effects: row dictionaries only.
- Test coverage: no horizon actual feature use via origin split test and variant formula tests.

### `build_variant_predictions(rows, variant)`

- Purpose: produce SE1, area_diff and recomposed SE3 unanchored predictions for a variant.
- Inputs: scored rows and variant name.
- Outputs: target-series mapping.
- Side effects: none.
- Test coverage: recomposed SE3 equals SE1 + area_diff.

### `anchor_predictions(known_actual, known_predicted, horizon_predicted, method)`

- Purpose: deterministic additive 16h level calibration.
- Inputs: known actuals, known model predictions, horizon predictions and method.
- Outputs: anchored horizon predictions plus anchor metadata.
- Side effects: none.
- Test coverage: mean/median/robust anchoring and zero/negative price safety.

### `compute_absolute_metrics(actual, predicted)`

- Purpose: anchored absolute MAE/RMSE/signed error and daily/weekly aggregates.
- Inputs: actual and predicted horizon series.
- Outputs: metrics dict.
- Side effects: none.
- Test coverage: metric sanity.

### `compute_shape_metrics(actual, predicted)`

- Purpose: centered/scaled/rank/top-bottom shape diagnostics.
- Inputs: actual and predicted horizon series.
- Outputs: metrics dict.
- Side effects: none.
- Test coverage: centered shape invariance to additive shifts and rank/top/bottom metrics.

### `write_p0040_evidence(...)`

- Purpose: write all required markdown/JSON P0040 evidence files.
- Inputs: rows, origin results, aggregates and warnings.
- Outputs: path mapping.
- Side effects: writes package-run files.
- Test coverage: module verification.

## Changed Functions

None planned in existing modules.

## Removed Functions

None.
