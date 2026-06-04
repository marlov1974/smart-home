# P0054F Input Classification

## Intended Inputs

| input | classification | status |
|---|---|---|
| calendar/time | forecast_safe | available |
| historical SE1 consumption lags/rollups strictly before origin | forecast_safe | available through P0053B logic |
| SE1 weather normals / `se1_core_weather` proxy | proxy / forecast_safe normals depending feature | available for no-price setup |
| P0053C-B anchored SE1 price forecast | forecast_safe for validation/holdout origins | blocked for training because train coverage is absent |
| actual future spot price | excluded_leakage | not used |
| production/export/import/flow/A61 | excluded_leakage | not used |

## Decision

The price forecast source is not rejected for leakage. It is rejected for P0054F model training because it lacks train rows.
