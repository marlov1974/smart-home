# Spot period index API contract

This contract belongs to the Mac spot forecast / price-index service.

The purpose is to expose a compact JSON response with 21 period price indexes for a requested week.

The initial service has no authentication or authorization. It is intended for trusted LAN / local Mac use only.

## Endpoint

```text
GET /spot/period-index?year=YYYY&week=WW
```

Examples:

```text
GET /spot/period-index?year=2025&week=2
GET /spot/period-index?year=2025&week=52
```

The week is ISO week number.

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

Default response:

```json
{
  "s": "spot_period_index.v1",
  "y": 2025,
  "w": 2,
  "m": 8.468769,
  "i": [0.971471, 0.725192, 0.377093, 0.488928, 0.479794, 0.326416, 0.592105, 0.622359, 0.766493, 2.135052, 3.341794, 1.728326, 3.121192, 2.739403, 0.569829, 0.372741, 0.409023, 0.34195, 0.299863, 0.297909, 0.293067]
}
```

Fields:

```text
s  schema short name
y  ISO year
w  ISO week
m  weekly mean total cost, SEK/kWh including VAT, tax, tariff and Tibber markup
i  21 period indexes, where 1.0 is weekly mean price
```

The indexes should be normalized so that their arithmetic mean is approximately 1.0.

## Optional debug response

For diagnostics, the API may support:

```text
GET /spot/period-index?year=YYYY&week=WW&debug=1
```

Optional debug response may include absolute period prices and labels:

```json
{
  "schema": "smart_home.spot_period_index.v1",
  "iso_year": 2025,
  "iso_week": 2,
  "mean_total_inc_vat_sek_kwh": 8.468769,
  "period_order": ["mon 06-14", "mon 14-22", "mon 22-06"],
  "total_inc_vat_sek_kwh": [8.227161, 6.141487, 3.193515],
  "price_index": [0.971471, 0.725192, 0.377093],
  "source": "spotprices-2025-winter-8h-weekly-period-index.json"
}
```

## Error responses

Missing arguments:

```json
{"error":"missing year or week"}
```

Unknown week:

```json
{"error":"week not found","year":2025,"week":1}
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

The planner should depend on the response contract, not on whether the data came from:

```text
- historical lookup
- week-weight analog model
- later weather-aware model
- fallback static table
```
