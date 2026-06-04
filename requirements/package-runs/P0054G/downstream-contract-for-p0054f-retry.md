# P0054G Downstream Contract For P0054F Retry

P0054F should not be retried yet.

## Required Source Contract

A retry needs a SE1 price forecast feature table with:

| requirement | required value |
|---|---|
| `prediction_kind` | `anchored_absolute_price` or clearly labeled alternative |
| area | SE1 |
| splits | train, validation, holdout |
| origin metadata | `forecast_origin_timestamp_utc`, `input_data_cutoff_utc`, `target_timestamp_utc`, `horizon_hours` |
| price column | `predicted_price` or `predicted_price_or_index` with unit/kind |
| target coverage | joinable to SE1 consumption target rows in all three splits |
| cutoff rule | no model input or training row after `input_data_cutoff_utc` for each origin |
| holdout use | no fitting, normalization or selection on holdout |

## Not Acceptable For Retry

Do not use P0053C-B alone for normal P0054F retry because it has zero train rows.

Do not train downstream consumption models on validation-origin rows and call it canonical train/validation/holdout modeling. That was acceptable only as P0053B-A2 offline diagnostic labeling.

## Current Status

No compliant source is available after P0054G.
