# P0054F Dataset Contract

## Status

No P0054F modeling dataset was created.

## Reason

The P0054F dataset requires paired no-price and with-price examples with identical target rows per model. The with-price variant requires a forecast-safe price forecast feature for the train split.

The available P0053C-B price forecast log has no train-period rows, so a valid P0054F training dataset cannot be constructed.

## Existing SE1 Consumption Source

P0053B uses:

```text
source_table = physical_balance_se1_se4_hourly_v1
target = consumption_se1
unit = MW hourly mean
dataset_table = se1_consumption_forecast_warmup_v1
```

Those rows remain usable for no-price SE1 consumption modeling, but P0054F's core ablation is incomplete without train-period price forecast features.
