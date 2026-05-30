# Spot Forecast Service

Last changed: P0030

## Module

```text
src.mac.services.spot_forecast
```

## Purpose

Mac-side provider for compact 21-period weekly price indexes used by the winter heat-pump planner.

P0030 changed the default service source from the committed P0017 winter fixture to the local historical SQLite store:

```text
~/.smart-home/data/spotprice_history.sqlite3
```

The old fixture loader remains available for deterministic compatibility callers and tests, but the CLI and HTTP service fail clearly when the SQLite DB is missing or incomplete. They do not silently fall back to the old fixture.

## CLI

```bash
python3 -m src.mac.services.spot_forecast --once --week 2 --db ~/.smart-home/data/spotprice_history.sqlite3
python3 -m src.mac.services.spot_forecast --host 127.0.0.1 --port 8080 --db ~/.smart-home/data/spotprice_history.sqlite3
```

## HTTP Contract

```text
GET /spot/period-index?week=WW
GET /spot/period-index/meta?week=WW
```

`/spot/period-index` success response remains a compact JSON array of exactly 21 numbers rounded to two decimals.

`/spot/period-index/meta` returns source metadata including DB path, area, coverage dates, row counts, gap count, negative-price count and per-year counts.

Invalid week input returns:

```json
{"error":"invalid week"}
```

Valid but unmodelable week input returns:

```json
{"error":"week not found"}
```

## Important Functions

`parse_week(raw)` validates ISO week input in the range 1..53.

`load_history(path)` loads the committed P0017 winter period-index JSON source. It is retained for compatibility and deterministic tests.

`load_history_from_db(path, area, require_start_date)` loads P0030 SQLite hourly actual spot prices, validates continuity, derives 21 period indexes for complete ISO weeks and returns `HistoricalWeek` records.

`db_history_metadata(path, area)` returns public source metadata for the DB-backed HTTP metadata endpoint.

`week_weight(distance)` implements the P0017 distance weights: 1.00, 0.70, 0.40 for distances 0, 1 and 2.

`weighted_average_indexes(target_week, history)` computes the unnormalized 21-period weighted vector.

`normalize_indexes(indexes)` normalizes the 21 values to arithmetic mean 1.0 before output rounding.

`forecast_period_indexes(target_week, history, db_path, area)` runs the full model and returns rounded compact output. If `history` is omitted it reads the P0030 SQLite DB.

`build_handler(history, metadata)` creates the HTTP handler for `/spot/period-index` and `/spot/period-index/meta`.

`run_once(week_arg, db_path, area, out, err)` prints one compact response for package verification and scripts.

`serve(host, port, db_path, area, history)` runs the trusted-local HTTP service.

## Operational Notes

Startup validates the local DB before binding the HTTP server. A missing or incomplete DB is an operator-visible configuration error.

The weekly home optimizer POC injects the legacy fixture history explicitly to keep its older deterministic lab contract separate from the P0030 service default.
