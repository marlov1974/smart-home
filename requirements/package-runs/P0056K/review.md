# P0056K Consistency Review

## Classification

WARN

## Consistency Result

P0056K is implementable as a LABB realistic DayAhead restart for SE1, SE2, SE3 and FI.

P0056J confirms that the old static P0056C/P0056F figures are not representative DayAhead performance because they are not on the same origin-realistic grid. P0056K must therefore treat them as old static upper-bound/model-ranking context only.

## Package Interpretation

Use a forecast-safe DayAhead protocol:

- forecast origin: D-1 12:00 Europe/Stockholm
- delivery block: D 00:00..23:00 Europe/Stockholm
- train rows: target rows strictly before forecast origin
- lag protocol: `DA-L3 seasonal_safe` for this restart
- weather: `actual_weather_proxy_LABB`

## WARN Rationale

This package deliberately starts with `DA-L3 seasonal_safe` instead of full recursive `DA-L2`, because recursive path models add substantial implementation and leakage risk. Neural models are optional and skipped unless already trivial. Actual weather remains a LABB proxy.

## Scope/Safety

No Shelly, Home Assistant, devices, runtime writes, production deployment, G2-KANDIDAT promotion, spot price, flow/exchange/A61/capacity, old physical_balance target, future actual load features or large artifacts are allowed.
