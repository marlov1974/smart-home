# P0056D Attempts

## Attempt 1

- Command: `python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d`
- Result: failed before network because the feature DB is outside the workspace sandbox and opened read-only.
- Fix: reran with approved escalated prefix for local SQLite writes and Open-Meteo network access.

## Attempt 2

- Command: `python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d`
- Result: Open-Meteo returned `HTTP Error 429: Too Many Requests` at `FI_TURKU_PORI_PORI` after 22 representative locations.
- Finding: the initial implementation committed only after the full fetch phase, so the failed run did not preserve completed location rows.
- Fix: changed P0056D to preserve location rows across reruns, skip complete cached locations, add fetch backoff and commit after each completed location.

## Attempt 3

- Command: `python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d`
- Result: fetched and committed all SE1 and SE2 representative locations, then Open-Meteo returned persistent `HTTP Error 429: Too Many Requests` for the first FI location.
- Backoff tried: 60 seconds, 180 seconds, 420 seconds and 900 seconds.
- Independent check: a tiny `curl -I` archive request for Helsinki over two days also returned `HTTP/1.1 429 Too Many Requests`.

## Current State

- Local P0056D location rows committed in SQLite:
  - `SE1`: 7 locations, 245448 rows.
  - `SE2`: 9 locations, 315576 rows.
  - `FI`: 0 P0056D locations.
- P0056D cannot complete under package rules until Open-Meteo archive access is available again for FI representative locations.

