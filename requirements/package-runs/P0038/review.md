# P0038 review

## Consistency result

WARN.

P0038 is implementable and the required weather variables exist after adding/backfilling the P0038 proxy locations. The model result is mixed: M3D improves recomposed SE3 full-year MAE modestly, M3C is neutral/slightly harmful, and M4 area-only improves area_diff but worsens recomposed SE3.

## Evidence

- `wind_speed_100m`, `wind_speed_10m`, `wind_gusts_10m`, `shortwave_radiation` and `cloud_cover` are available.
- Direct/diffuse radiation, sunshine duration and explicit solar elevation are not stored.
- P0038 wind/solar locations were added to local weather history config and backfilled from Open-Meteo.

## Safety

No M5/M6/M7/API, optimizer, Shelly, Home Assistant, KVS or device path is in scope.
