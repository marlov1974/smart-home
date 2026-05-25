# Winter 2025 spot cost by 8h weekly strategy period

This file stores the 21-period weekly strategy table derived from:

```text
memory/planning/spotprice-2025-winter-2h-weekly-blocks.md
```

The 84 weekly 2h blocks are converted into 21 weekly 8h strategy periods:

```text
7 days × 3 periods/day
```

Strategy periods:

```text
22:00-06:00
06:00-14:00
14:00-22:00
```

Unit for absolute prices: SEK/kWh, including VAT, Tibber markup, energy tax and Vattenfall grid tariff.

## Attribution model

This table uses operational-night attribution for `22:00-06:00`:

```text
D 22:00-00:00 + D+1 00:00-06:00
```

Examples:

```text
Mån 22:00-06:00 = Mån 22:00-00:00 + Tis 00:00-06:00
Sön 22:00-06:00 = Sön 22:00-00:00 + Mån 00:00-06:00
```

This makes the 21 periods contiguous around the operational week and suitable for plan-to-Monday-06 scheduling.

## Mean weekly price

The mean weekly price is calculated as the arithmetic mean of the 21 period prices, which is equivalent to the arithmetic mean of the stored 84 rounded weekly 2h block prices because all periods have equal duration.

```text
mean_week_price = 6.502 SEK/kWh
```

Note: this is derived from the stored rounded 84-block table. It can differ slightly from raw-block weighted averages in the source analysis.

## Period price index

```text
period_price_index = period_price / mean_week_price
```

So:

```text
1.000 = average weekly period price
0.500 = half average weekly period price
2.000 = double average weekly period price
```

## 21 weekly strategy periods

| Day | Period | Absolute price | Price index |
|---|---|---:|---:|
| Mån | 22:00-06:00 | 5.250 | 0.808 |
| Mån | 06:00-14:00 | 9.111 | 1.401 |
| Mån | 14:00-22:00 | 8.541 | 1.314 |
| Tis | 22:00-06:00 | 5.331 | 0.820 |
| Tis | 06:00-14:00 | 7.978 | 1.227 |
| Tis | 14:00-22:00 | 8.689 | 1.337 |
| Ons | 22:00-06:00 | 5.248 | 0.807 |
| Ons | 06:00-14:00 | 8.504 | 1.308 |
| Ons | 14:00-22:00 | 8.431 | 1.297 |
| Tor | 22:00-06:00 | 5.730 | 0.881 |
| Tor | 06:00-14:00 | 9.396 | 1.445 |
| Tor | 14:00-22:00 | 8.983 | 1.382 |
| Fre | 22:00-06:00 | 3.540 | 0.544 |
| Fre | 06:00-14:00 | 9.736 | 1.497 |
| Fre | 14:00-22:00 | 8.353 | 1.285 |
| Lör | 22:00-06:00 | 2.928 | 0.450 |
| Lör | 06:00-14:00 | 3.208 | 0.493 |
| Lör | 14:00-22:00 | 3.370 | 0.518 |
| Sön | 22:00-06:00 | 4.788 | 0.736 |
| Sön | 06:00-14:00 | 3.871 | 0.595 |
| Sön | 14:00-22:00 | 5.545 | 0.853 |

## Source calculation

Each period price is the mean of four stored 2h block prices.

| Day | Period | Included 2h blocks |
|---|---|---|
| Mån | 22:00-06:00 | Mån 22:00-00:00, Tis 00:00-02:00, Tis 02:00-04:00, Tis 04:00-06:00 |
| Mån | 06:00-14:00 | Mån 06:00-08:00, Mån 08:00-10:00, Mån 10:00-12:00, Mån 12:00-14:00 |
| Mån | 14:00-22:00 | Mån 14:00-16:00, Mån 16:00-18:00, Mån 18:00-20:00, Mån 20:00-22:00 |
| Tis | 22:00-06:00 | Tis 22:00-00:00, Ons 00:00-02:00, Ons 02:00-04:00, Ons 04:00-06:00 |
| Tis | 06:00-14:00 | Tis 06:00-08:00, Tis 08:00-10:00, Tis 10:00-12:00, Tis 12:00-14:00 |
| Tis | 14:00-22:00 | Tis 14:00-16:00, Tis 16:00-18:00, Tis 18:00-20:00, Tis 20:00-22:00 |
| Ons | 22:00-06:00 | Ons 22:00-00:00, Tor 00:00-02:00, Tor 02:00-04:00, Tor 04:00-06:00 |
| Ons | 06:00-14:00 | Ons 06:00-08:00, Ons 08:00-10:00, Ons 10:00-12:00, Ons 12:00-14:00 |
| Ons | 14:00-22:00 | Ons 14:00-16:00, Ons 16:00-18:00, Ons 18:00-20:00, Ons 20:00-22:00 |
| Tor | 22:00-06:00 | Tor 22:00-00:00, Fre 00:00-02:00, Fre 02:00-04:00, Fre 04:00-06:00 |
| Tor | 06:00-14:00 | Tor 06:00-08:00, Tor 08:00-10:00, Tor 10:00-12:00, Tor 12:00-14:00 |
| Tor | 14:00-22:00 | Tor 14:00-16:00, Tor 16:00-18:00, Tor 18:00-20:00, Tor 20:00-22:00 |
| Fre | 22:00-06:00 | Fre 22:00-00:00, Lör 00:00-02:00, Lör 02:00-04:00, Lör 04:00-06:00 |
| Fre | 06:00-14:00 | Fre 06:00-08:00, Fre 08:00-10:00, Fre 10:00-12:00, Fre 12:00-14:00 |
| Fre | 14:00-22:00 | Fre 14:00-16:00, Fre 16:00-18:00, Fre 18:00-20:00, Fre 20:00-22:00 |
| Lör | 22:00-06:00 | Lör 22:00-00:00, Sön 00:00-02:00, Sön 02:00-04:00, Sön 04:00-06:00 |
| Lör | 06:00-14:00 | Lör 06:00-08:00, Lör 08:00-10:00, Lör 10:00-12:00, Lör 12:00-14:00 |
| Lör | 14:00-22:00 | Lör 14:00-16:00, Lör 16:00-18:00, Lör 18:00-20:00, Lör 20:00-22:00 |
| Sön | 22:00-06:00 | Sön 22:00-00:00, Mån 00:00-02:00, Mån 02:00-04:00, Mån 04:00-06:00 |
| Sön | 06:00-14:00 | Sön 06:00-08:00, Sön 08:00-10:00, Sön 10:00-12:00, Sön 12:00-14:00 |
| Sön | 14:00-22:00 | Sön 14:00-16:00, Sön 16:00-18:00, Sön 18:00-20:00, Sön 20:00-22:00 |

## Planning interpretation

- Cheapest period is `Lör 22:00-06:00` with index `0.450`.
- Saturday daytime and evening are also very cheap, with indexes around `0.493-0.518`.
- Friday night into Saturday is cheap, index `0.544`, because the night crosses into Saturday low prices.
- Sunday 06:00-14:00 remains cheap at index `0.595`.
- Sunday 14:00-22:00 is more expensive than the rest of the weekend but still below the weekly average at index `0.853`.
- Weekday daytime periods are expensive, especially `Fre 06:00-14:00` at index `1.497` and `Tor 06:00-14:00` at index `1.445`.
- The table supports a Monday-06 anchored planner: weekday production is biased away from daytime, while weekend production receives high energy weights through low price indexes.
