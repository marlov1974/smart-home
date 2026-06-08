# P0056G Consistency Review

## Classification

`WARN`

## Evidence

- Repository was synchronized with `origin/main` before package lookup.
- Active package: `requirements/packages/P0056G-labb-weekly-walk-forward-consumption-emulator.md`.
- Target table `area_consumption_hourly_v1` has SE1, SE2, SE3 and FI rows from 2022-06-01 through 2026-06-07.
- P0056B weather rows for SE1, SE2, SE3 and FI run through 2026-05-31 21:00Z.
- P0056D weather rows for SE1, SE2 and FI run through 2026-05-31 23:00Z.
- Existing P0056C/P0056D/P0056E/P0056F evidence supplies static baselines for scoped areas.

## Consistency Result

P0056G is package-scoped, LABB-only and compatible with repository safety rules. It does not authorize API calls, devices, runtime writes, Shelly writes, spot-price features, flow/exchange/A61/capacity features, or production activation.

## WARN Assumptions

- P0056G requires weekly retraining over a full post-2025-06 period. Repeating the complete P0056C/P0056E/P0056F weighted ensemble for every area-week would be too expensive for this first package. The implementation will run a deterministic, checkpointed weekly no-price HGB variant with the same P0056 feature family and weather protocols, and compare it to the committed static baselines.
- Static baseline `A` is represented by the latest committed static evidence level per area, not by re-running static models for every week.
- Weekly model `B` is the executable weekly retrain model. The result is LABB evidence for whether weekly retraining helps; it is not a production candidate claim.
- Optional NO3/NO4 are skipped.
- Future actual weather proxy is used and labeled `actual_weather_proxy` / LABB sensitivity.

## STOP Checks

- Inputs are present for required areas.
- Weekly split and leakage safety can be verified in code.
- Scope excludes forbidden features and runtime writes.

Result: continue with implementation under `WARN`.
