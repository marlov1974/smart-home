# P0054G Coverage By Split

## Existing P0053C-B Source

Table:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
```

By target timestamp:

| split | rows | origins | target range |
|---|---:|---:|---|
| train | 0 | 0 | none |
| validation | 24192 | 144 | 2025-01-01T23:00:00Z .. 2025-05-31T22:00:00Z |
| holdout | 58464 | 348 | 2025-06-01T23:00:00Z .. 2026-05-21T22:00:00Z |

By forecast origin:

| split | rows | origins | origin range |
|---|---:|---:|---|
| train | 0 | 0 | none |
| validation | 24192 | 144 | 2025-01-01T23:00:00Z .. 2025-05-24T23:00:00Z |
| holdout | 58464 | 348 | 2025-06-01T23:00:00Z .. 2026-05-14T23:00:00Z |

## P0053C-A Shape Source

Table:

```text
m4_price_shape_forecast_origin_log_p0053ca_v1
```

This table is not sufficient as the missing source because it has one holdout origin only and contains shape/index predictions, not train/validation/holdout anchored absolute SE1 price rows.

## P0054G Result

No created table. Train coverage remains unavailable for P0054F retry.
