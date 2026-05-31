# P0040 Review

Status: WARN

## Consistency Result

P0040 is consistent with current Mac-side spotprice diagnostics and can be implemented without M5, M6/API, M7, Shelly, Home Assistant, KVS, optimizer, production endpoint, or live device changes.

The package is broad. The safe interpretation is:

- build a package-scoped weekly backtest diagnostics module
- use Monday origins with 16 known Monday spot hours and 168-hour horizons
- keep M1 as the baseplate
- use M1B only for training M3A_m1b/M3B_m1b deltas
- use actual historical weather as explicitly labeled weather-oracle proxy
- make anchored absolute forecast accuracy the primary evidence
- keep M3C/M3D/M4 as diagnostics only unless evidence supports them

## Repository Truth Checked

- `P0039` corrected that M1B is a training/normalization base only; forecast chains apply M1B-trained deltas on top of M1.
- `src/mac/services/spotprice_model_diagnostics/p0037.py` provides M1/M2/M3A/M3B helpers and strict component patterns.
- `src/mac/services/spotprice_model_diagnostics/p0038.py` provides solar/wind proxy transforms and M3C/M3D diagnostic concepts.
- `src/mac/services/spotprice_model_diagnostics/p0039.py` provides M1B row policy and M1B-trained M3A/M3B helpers.

## Warnings and Assumptions

- P0040 uses static strict pre-backtest component fits rather than per-origin expanding-window refits. The fit period ends before the primary origin range, so this is strict for P0040 forecast-horizon spot leakage.
- M3C/M3D use P0038-style diagnostic deltas and actual historical weather as `weather_oracle`.
- M4_area_diff is not production-promoted; if used, it is reported as diagnostic only.
- The latest complete Monday-start week is determined from available local data.

## Safety

No live device access is allowed or needed. P0040 must not call Shelly, Home Assistant, KVS, MCP, actuator/device APIs, or expose a production forecast API.
