# Spot period index API contract

This contract belongs to the Mac spot forecast / price-index service.

The purpose is to expose a very compact JSON response with 21 period price indexes for a requested ISO week.

The initial service has no authentication or authorization. It is intended for trusted LAN / local Mac use only.

## Forecast endpoint

```text
GET /spot/period-index?week=WW
```

Examples:

```text
GET /spot/period-index?week=2
GET /spot/period-index?week=52
```

The `week` argument is ISO week number. Forecast mode does not need a year argument in v1. It returns the normal/expected period shape for that week number using the current Mac model.

## Period order

The response array must always contain exactly 21 values in this order:

```text
0   mon 06-14
1   mon 14-22
2   mon 22-06
3   tue 06-14
4   tue 14-22
5   tue 22-06
6   wed 06-14
7   wed 14-22
8   wed 22-06
9   thu 06-14
10  thu 14-22
11  thu 22-06
12  fri 06-14
13  fri 14-22
14  fri 22-06
15  sat 06-14
16  sat 14-22
17  sat 22-06
18  sun 06-14
19  sun 14-22
20  sun 22-06
```

Night periods use operational-night attribution:

```text
D 22-06 = D 22-00 + D+1 00-06
```

## Compact response

Default response is only a JSON array of 21 numbers.

Values are rounded to two decimals.

Example:

```json
[0.97,0.73,0.38,0.49,0.48,0.33,0.59,0.62,0.77,2.14,3.34,1.73,3.12,2.74,0.57,0.37,0.41,0.34,0.30,0.30,0.29]
```

Each value is:

```text
period_price_index = period_price / week_mean_price
```

So:

```text
1.00 = expected weekly mean price
0.50 = half expected weekly mean price
2.00 = double expected weekly mean price
```

The 21 returned values should have arithmetic mean approximately 1.00 before rounding. Rounding to two decimals may make the displayed mean slightly different.

## Optional historical lookup endpoint

Historical/debug lookup may use year + week, but this is not the default planner API:

```text
GET /spot/period-index/history?year=YYYY&week=WW
```

The historical endpoint may return the same compact array or a debug object if explicitly requested by a future tool. The planner should use the compact forecast endpoint.

## Error responses

Missing or invalid week:

```json
{"error":"invalid week"}
```

Unknown week:

```json
{"error":"week not found"}
```

The service should use HTTP 400 for invalid input and HTTP 404 for missing week data.

## Data source

Initial historical source file:

```text
data/spot/spotprices-2025-winter-8h-weekly-period-index.json
```

This file stores absolute prices and indexes derived from uploaded `SpotPrices2h.xlsx` using the total-cost model including VAT, energy tax, Vattenfall grid tariff and Tibber markup.

## Future model use

The same endpoint can later serve a Mac ML / analog forecast instead of a historical week lookup.

The planner should depend only on the compact response contract, not on whether the data came from:

```text
- week-weight analog model
- later weather-aware model
- fallback static table
```
