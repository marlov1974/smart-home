# Winter 2025 spot cost by 2h weekly block

This file stores the reusable result for planning discussions: average actual electricity cost per 2h weekly block for the winter tariff months in 2025.

## Scope

Input workbook:

```text
SpotPrices2h.xlsx
```

Filtered dates:

```text
2025-01-01 through 2025-03-31
2025-11-01 through 2025-12-31
```

Block count:

```text
1812 two-hour blocks
84 weekly blocks = 7 days × 12 two-hour blocks
```

The input spot prices are treated as SEK/kWh excluding VAT.

## Cost model

Model copied from `src/shelly/spotprice/spotprice.js` at the time of analysis.

```text
VAT: 25%
Tibber retailer markup: 0.06 SEK/kWh excluding VAT
Retailer variable cost: 0.00 SEK/kWh excluding VAT
Energy tax: 0.36 SEK/kWh excluding VAT

Vattenfall grid, low tariff: 0.305 SEK/kWh including VAT
Vattenfall grid, high tariff: 0.765 SEK/kWh including VAT

High grid tariff:
  months: January, February, March, November, December
  weekdays: Monday-Friday
  hours: 06:00-22:00
```

Formula:

```text
total_inc_vat =
  spot_ex_vat * 1.25
  + (0.06 + 0.00) * 1.25
  + 0.36 * 1.25
  + grid_tariff_inc_vat
```

Overall means for the filtered period:

```text
Average spot, excluding VAT: 4.330 SEK/kWh
Average total, including VAT/tax/markup/grid: 6.459 SEK/kWh
```

## Average total cost by weekly 2h block

Unit: SEK/kWh, including VAT, Tibber markup, energy tax and Vattenfall grid tariff.

| 2h block | Mån | Tis | Ons | Tor | Fre | Lör | Sön |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00-02:00 | 4.511 | 5.383 | 5.376 | 5.011 | 5.644 | 3.603 | 2.867 |
| 02:00-04:00 | 4.528 | 4.833 | 4.988 | 4.930 | 5.497 | 3.089 | 2.818 |
| 04:00-06:00 | 5.131 | 5.007 | 5.143 | 5.523 | 5.612 | 2.975 | 2.964 |
| 06:00-08:00 | 7.634 | 7.151 | 7.832 | 8.857 | 8.938 | 3.105 | 3.281 |
| 08:00-10:00 | 9.607 | 8.379 | 9.055 | 9.996 | 10.540 | 3.200 | 3.850 |
| 10:00-12:00 | 9.505 | 8.051 | 8.646 | 9.599 | 10.188 | 3.268 | 4.113 |
| 12:00-14:00 | 9.699 | 8.332 | 8.482 | 9.132 | 9.278 | 3.259 | 4.240 |
| 14:00-16:00 | 9.280 | 8.875 | 8.739 | 9.091 | 9.515 | 3.355 | 4.629 |
| 16:00-18:00 | 9.048 | 9.388 | 9.101 | 9.353 | 9.456 | 3.467 | 5.798 |
| 18:00-20:00 | 8.392 | 8.925 | 8.510 | 9.378 | 8.185 | 3.398 | 6.396 |
| 20:00-22:00 | 7.444 | 7.570 | 7.376 | 8.111 | 6.256 | 3.259 | 5.356 |
| 22:00-00:00 | 5.778 | 5.818 | 5.530 | 6.168 | 4.493 | 3.062 | 4.981 |

## Cheapest weekly blocks

| Rank | Veckoblock | kr/kWh |
|---:|---|---:|
| 1 | Sön 02:00-04:00 | 2.818 |
| 2 | Sön 00:00-02:00 | 2.867 |
| 3 | Sön 04:00-06:00 | 2.964 |
| 4 | Lör 04:00-06:00 | 2.975 |
| 5 | Lör 22:00-00:00 | 3.062 |
| 6 | Lör 02:00-04:00 | 3.089 |
| 7 | Lör 06:00-08:00 | 3.105 |
| 8 | Lör 08:00-10:00 | 3.200 |
| 9 | Lör 12:00-14:00 | 3.259 |
| 10 | Lör 20:00-22:00 | 3.259 |

## Most expensive weekly blocks

| Rank | Veckoblock | kr/kWh |
|---:|---|---:|
| 1 | Fre 08:00-10:00 | 10.540 |
| 2 | Fre 10:00-12:00 | 10.188 |
| 3 | Tor 08:00-10:00 | 9.996 |
| 4 | Mån 12:00-14:00 | 9.699 |
| 5 | Mån 08:00-10:00 | 9.607 |
| 6 | Tor 10:00-12:00 | 9.599 |
| 7 | Fre 14:00-16:00 | 9.515 |
| 8 | Mån 10:00-12:00 | 9.505 |
| 9 | Fre 16:00-18:00 | 9.456 |
| 10 | Tor 18:00-20:00 | 9.378 |

## Planning interpretation

The winter tariff/spot pattern strongly supports moving heat-pump energy away from weekday daytime high-tariff blocks when COP loss does not erase the price gain.

For ventilation, the physical efficiency penalty at high airflows is large enough that spot-price shifting should be secondary to air quality, humidity, VVX sweet spot and safety constraints.
