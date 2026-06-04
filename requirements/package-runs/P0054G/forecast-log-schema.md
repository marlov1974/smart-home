# P0054G Forecast Log Schema

No new forecast log table was created.

## Candidate Existing Schema

The existing P0053C-B table has the required shape for validation/holdout downstream use:

```text
m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1
```

Important columns:

| column | meaning |
|---|---|
| `forecast_origin_timestamp_utc` | forecast origin for the 168h path |
| `input_data_cutoff_utc` | latest allowed input timestamp |
| `target_timestamp_utc` | target hour being predicted |
| `horizon_hours` | 0..167 horizon from origin |
| `area` | SE1 |
| `predicted_price` | anchored absolute forecast |
| `prediction_unit` | source hour price unit |
| `prediction_kind` | anchored absolute price |
| `anchor_method` | selected anchor method |
| `source_shape_value` | upstream shape value |

## Missing Target Artifact

Preferred target table was:

```text
m4_48h_anchored_absolute_price_forecast_log_p0054g_se1_v1
```

It was not created because safe train-period generation requires a new origin-local upstream model protocol.
