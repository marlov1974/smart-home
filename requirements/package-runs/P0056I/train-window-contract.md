# P0056I Train-Window Contract

| variant | train_start | train_end |
| --- | --- | --- |
| TW2 | forecast_origin minus 2 calendar years | forecast_origin exclusive |
| TW3 | forecast_origin minus 3 calendar years | forecast_origin exclusive |
| TWX | 2022-06-01T00:00:00Z | forecast_origin exclusive |

Everything except `train_start` is held fixed across variants.
