# P0054N Review

Status: `WARN`

## Consistency Result

P0054N is implementable inside G2 LABB scope, with one important timing caveat.

Repository truth confirms that P0054M/P0054L2 advanced price forecast logs are safe for consumption modeling, but both persisted tables use only `23:00Z` forecast origins. That origin cadence cannot represent the required Swedish DayAhead decision time:

```text
decision_time_local = 12:00 Europe/Stockholm on D-1
delivery_day_local = D 00:00..23:00 Europe/Stockholm
```

Using those persisted `23:00Z` rows directly for DayAhead would be unsafe for the stated market-time semantics because it would use an origin after the intended decision time. Therefore P0054N must not silently reuse persisted `23:00Z` origins for the DayAhead slice.

## Allowed Resolution

P0054N will build an in-memory package-local exact-origin advanced price feature for the 36h/DayAhead evaluation using the old P0054L2/P0054M feature and model logic:

- train-side advanced price rows: blocked train-price model fitted before `2025-03-01`, predicting exact 12:00-local origins for `2025-03-01..2025-05-31` targets.
- holdout advanced price rows: train-fit-only price model fitted before `2025-06-01`, predicting exact 12:00-local origins for holdout targets.
- no persisted model artifact and no live API/device/runtime work.

This is a documented P0054N exact-origin extension of the P0054M safe protocol, not a production forecast source.

## Scope And Safety

Classification: `WARN`, not `STOP`, because the exact DayAhead timing can be represented safely by generating package-local historical forecasts from local observed history with strict cutoffs.

No package instruction requires live market integration, API calls, devices, Home Assistant, Shelly, runtime changes, Nord Pool submission, A61/utilization, production/export/import/future-flow features, or G2-KANDIDAT promotion.

## Evidence Notes

The run must document:

- persisted P0054M/P0054L2 origin cadence mismatch.
- exact-origin UTC conversion including DST.
- whether all four model families imported and ran.
- identical paired rows for no-price and with-advanced-price comparisons.
- leakage review for train/holdout cutoffs and forbidden feature names.
