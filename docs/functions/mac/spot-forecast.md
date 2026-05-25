# Spot Forecast Service

Last changed: P0017

## Module

```text
src.mac.services.spot_forecast
```

## Purpose

Mac-side provider for compact 21-period weekly price indexes used by the winter heat-pump planner.

## CLI

```bash
python3 -m src.mac.services.spot_forecast --once --week 2
python3 -m src.mac.services.spot_forecast --host 127.0.0.1 --port 8080
```

## HTTP Contract

```text
GET /spot/period-index?week=WW
```

Default success response is a compact JSON array of exactly 21 numbers rounded to two decimals.

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

`load_history(path)` loads the committed winter period-index JSON source into validated historical records.

`week_weight(distance)` implements the P0017 distance weights: 1.00, 0.70, 0.40 for distances 0, 1 and 2.

`weighted_average_indexes(target_week, history)` computes the unnormalized 21-period weighted vector.

`normalize_indexes(indexes)` normalizes the 21 values to arithmetic mean 1.0 before output rounding.

`forecast_period_indexes(target_week, history)` runs the full model and returns rounded compact output.

`build_handler(history)` creates the HTTP handler for `/spot/period-index`.

`run_once(week_arg, out, err)` prints one compact response for package verification and scripts.
