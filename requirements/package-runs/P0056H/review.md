# P0056H Consistency Review

## Classification

`WARN`

## Evidence

- Repository synchronized with `origin/main`; P0056H was pulled by fast-forward.
- Required target rows exist for SE1, SE2, SE3 and FI from 2022-06-01 through 2026-06-07.
- P0056D weather exists for SE1, SE2 and FI through 2026-05-31 23:00Z.
- P0056B weather exists for SE3 through 2026-05-31 21:00Z.
- P0056C/E/F/G evidence supplies required static and weekly comparison values.

## Consistency Result

P0056H is package-scoped and compatible with repository safety rules. It is LABB-only and does not authorize API calls, device writes, runtime changes, Shelly changes, Home Assistant changes, production activation or G2-KANDIDAT promotion.

## WARN Assumptions

- Running full `HorizonBiasCorrected_WeightedEnsemble_no_price` for every area and every 5-day origin would be expensive. P0056H will use a deterministic `HGB_no_price` rolling-origin implementation to isolate lag protocol behavior.
- Primary modes will be forecast-safe:
  - `L1_origin_known_fallback`: forecast-window lags are replaced by seasonal `lag_168h` style values with availability flags.
  - `L2_recursive_lags`: short lags can use the model's own earlier forecast inside the 36h window.
- Oracle/future-actual lag sensitivity is optional and will be skipped unless the first two modes leave material ambiguity.
- Actual weather proxy will be used and labeled LABB.

## STOP Checks

- Required inputs are present.
- Lag availability and primary leakage safety are verifiable in code.
- Scope excludes forbidden spot/flow/A61/capacity/physical_balance features.

Result: continue under `WARN`.
