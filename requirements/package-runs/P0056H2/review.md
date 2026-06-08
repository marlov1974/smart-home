# P0056H2 Consistency Review

## Classification

WARN

## Reasoning

The package is implementable and consistent with the LABB policy. P0056C confirms that older static lag construction uses `area_lag_features_at_origin(values, origin_index)` and `area_rolling_features_at_origin(values, origin_index)`, meaning all 36 target hours from one forecast origin receive the same historical load lag/rolling context anchored at origin.

The package should not be interpreted as production-safe runtime behavior or G2-KANDIDAT evidence. It is a diagnostic comparison that intentionally tests the older static feature shape. It remains LABB-only, uses historical observed target/weather data, and does not call APIs or devices.

## Assumptions

- Use the same P0056H 36h origin schedule and strict complete-window skipping.
- Use P0056H's tractable HGB no-price implementation so the primary comparison isolates lag feature construction against P0056H rather than running a broad model search.
- Use P0056D weather for SE1, SE2 and FI and P0056B weather for SE3, matching P0056H.
- P0056H2 static-style origin lags are forecast-safe because they are anchored before the forecast window, but they are not the same as target-hour actual lag reconstruction.

## Scope Guard

No Shelly, Home Assistant, runtime, API, device, spot-price, flow/exchange/A61/capacity, physical_balance or production activation changes are allowed.
