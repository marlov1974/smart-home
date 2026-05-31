# P0034 consistency review

Result: PASS for dependency availability; holdout outcome remains WARN.

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

Initial P0034 run found `scikit-learn` missing:

```text
NO_SKLEARN ModuleNotFoundError No module named 'sklearn'
```

Follow-up on 2026-05-31 installed:

```text
scikit-learn 1.6.1
numpy 2.0.2
scipy 1.13.1
joblib 1.5.3
threadpoolctl 3.6.0
```

HGB was tested but did not complete within a practical rebuild window, so P0034 now uses a deterministic scikit-learn pipeline:

```text
PolynomialFeatures(degree=2, include_bias=False) + Ridge(alpha=1.0)
```

This removes the dependency blocker. The holdout result is still classified as `WARN` because M4 does not beat the P0033 M1 baseline.

## Existing baseline

Existing older index baseline:

```text
src.mac.services.spot_forecast
docs/functions/mac/spot-forecast.md
```

It provides a 21-period weekly price index service. P0034 will compare directly against P0033 M1 baseline and document the older index service as an architectural predecessor rather than a like-for-like hourly SE1/area-diff baseline.

## Safety review

No weather features are allowed in the M4 feature matrix. No live devices or network calls are required.

Decision: PASS to build with scikit-learn; WARN on model quality versus M1.
