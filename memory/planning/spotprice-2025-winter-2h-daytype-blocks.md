# Winter 2025 spot cost by 2h daytype block

This file stores the reduced planning table derived from:

```text
memory/planning/spotprice-2025-winter-2h-weekly-blocks.md
```

The 84 weekly blocks are converted into 36 daytype blocks:

```text
12 weekday blocks = average of Monday-Friday for each 2h block
12 Saturday blocks
12 Sunday blocks
```

Unit: SEK/kWh, including VAT, Tibber markup, energy tax and Vattenfall grid tariff.

## Average total cost by daytype and 2h block

| 2h block | Vardag | Lördag | Söndag |
|---|---:|---:|---:|
| 00:00-02:00 | 5.185 | 3.603 | 2.867 |
| 02:00-04:00 | 4.955 | 3.089 | 2.818 |
| 04:00-06:00 | 5.283 | 2.975 | 2.964 |
| 06:00-08:00 | 8.082 | 3.105 | 3.281 |
| 08:00-10:00 | 9.515 | 3.200 | 3.850 |
| 10:00-12:00 | 9.198 | 3.268 | 4.113 |
| 12:00-14:00 | 8.985 | 3.259 | 4.240 |
| 14:00-16:00 | 9.100 | 3.355 | 4.629 |
| 16:00-18:00 | 9.269 | 3.467 | 5.798 |
| 18:00-20:00 | 8.678 | 3.398 | 6.396 |
| 20:00-22:00 | 7.351 | 3.259 | 5.356 |
| 22:00-00:00 | 5.557 | 3.062 | 4.981 |

## Planning interpretation

The reduced table is useful when the planner needs a compact winter default rather than full weekday-specific pricing.

Main observations:

- Weekday 08:00-20:00 is consistently expensive.
- Saturday is broadly cheap across the full day, with especially low prices before 10:00 and after 20:00.
- Sunday is cheapest before 06:00, but Sunday evening can become relatively expensive.
- For weekday heat-pump planning, 22:00-06:00 is much better than 06:00-22:00, but 02:00-04:00 is the cheapest weekday block in this reduced view.
