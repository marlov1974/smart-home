# P0034 consistency review

Result: WARN

## Package interpretation

P0034 builds M4: a temperature-neutral normal spot model trained from P0033 output.

Primary targets:

- `system_proxy_se1`
- `area_diff_proxy_se3`

SE3 is recomposed only as:

```text
M4_SE3 = M4_SE1 + M4_area_diff_proxy
```

Out of scope: M5/M6/M7, temperature forecast deltas, forecast API/server, launchd, devices, Shelly, Home Assistant, KVS and controls.

## Local input checks

P0033 feature DB exists:

```text
/Users/marcus.lovenstad/.smart-home/data/spotprice_model_features.sqlite3
```

Required table:

```text
m3_temp_normalized_prices_v1
```

Coverage:

```text
start_date = 2022-05-30
end_date = 2026-05-24
row_count = 34944
```

Required target columns exist:

- `temp_normalized_price_v1_se1`
- `temp_normalized_area_diff_v1`
- `temp_normalized_price_v1_se3`

## ML dependency decision

`scikit-learn` is not installed:

```text
NO_SKLEARN ModuleNotFoundError No module named 'sklearn'
```

P0034 allows Ridge/Linear baseline candidates. To avoid adding an unreviewed dependency, P0034 will implement a deterministic pure-Python Ridge regression baseline with fixed feature schema and no external packages.

This is a `WARN`, not `STOP`, because a meaningful reproducible M4 model can still be implemented, trained and backtested without external dependency installation.

## Existing baseline

Existing older index baseline:

```text
src.mac.services.spot_forecast
docs/functions/mac/spot-forecast.md
```

It provides a 21-period weekly price index service. P0034 will compare directly against P0033 M1 baseline and document the older index service as an architectural predecessor rather than a like-for-like hourly SE1/area-diff baseline.

## Safety review

No weather features are allowed in the M4 feature matrix. No live devices or network calls are required.

Decision: WARN, proceed with pure-Python deterministic Ridge M4.
