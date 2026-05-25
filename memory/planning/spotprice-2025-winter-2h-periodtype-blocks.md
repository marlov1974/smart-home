# Winter 2025 spot cost by daytype strategy period

This file stores the 9-period reduction derived from:

```text
memory/planning/spotprice-2025-winter-2h-daytype-blocks.md
```

The 36 daytype 2h blocks are converted into 9 strategy-period blocks:

```text
3 weekday periods
3 Saturday periods
3 Sunday periods
```

Strategy periods:

```text
22:00-06:00  charge / recover
06:00-14:00  save
14:00-22:00  balance
```

Unit: SEK/kWh, including VAT, Tibber markup, energy tax and Vattenfall grid tariff.

## Attribution note

This reduction uses the daytype table directly. The `22:00-06:00` period is calculated from these four 2h block values for each daytype:

```text
22:00-00:00
00:00-02:00
02:00-04:00
04:00-06:00
```

This keeps the reduction compact and consistent with the previously stored daytype table. If a future planner needs strict operational-night attribution across calendar days, for example Friday 22:00 through Saturday 06:00 as a weekend-recovery night, that should be defined as a separate operational-calendar contract.

## Period averages, maxima and minima

`Max/Min` shows how much more expensive the most expensive 2h block in the period is than the cheapest 2h block in the same period.

| Daytype | Period | Mean | Max | Min | Max/Min |
|---|---|---:|---:|---:|---:|
| Vardag | 22:00-06:00 | 5.245 | 5.557 | 4.955 | 112.1% |
| Vardag | 06:00-14:00 | 8.945 | 9.515 | 8.082 | 117.7% |
| Vardag | 14:00-22:00 | 8.600 | 9.269 | 7.351 | 126.1% |
| Lördag | 22:00-06:00 | 3.182 | 3.603 | 2.975 | 121.1% |
| Lördag | 06:00-14:00 | 3.208 | 3.268 | 3.105 | 105.2% |
| Lördag | 14:00-22:00 | 3.370 | 3.467 | 3.259 | 106.4% |
| Söndag | 22:00-06:00 | 3.407 | 4.981 | 2.818 | 176.8% |
| Söndag | 06:00-14:00 | 3.871 | 4.240 | 3.281 | 129.2% |
| Söndag | 14:00-22:00 | 5.545 | 6.396 | 4.629 | 138.2% |

## Source block values

| Daytype | Period | Included 2h block values |
|---|---|---|
| Vardag | 22:00-06:00 | 5.557, 5.185, 4.955, 5.283 |
| Vardag | 06:00-14:00 | 8.082, 9.515, 9.198, 8.985 |
| Vardag | 14:00-22:00 | 9.100, 9.269, 8.678, 7.351 |
| Lördag | 22:00-06:00 | 3.062, 3.603, 3.089, 2.975 |
| Lördag | 06:00-14:00 | 3.105, 3.200, 3.268, 3.259 |
| Lördag | 14:00-22:00 | 3.355, 3.467, 3.398, 3.259 |
| Söndag | 22:00-06:00 | 4.981, 2.867, 2.818, 2.964 |
| Söndag | 06:00-14:00 | 3.281, 3.850, 4.113, 4.240 |
| Söndag | 14:00-22:00 | 4.629, 5.798, 6.396, 5.356 |

## Planning interpretation

- Weekday charge period `22:00-06:00` is much cheaper than weekday save/balance periods.
- Weekday `06:00-14:00` and `14:00-22:00` are both expensive; avoiding heat-pump heavy blocks here is valuable when COP loss does not erase the gain.
- Saturday is consistently cheap across all periods.
- Sunday evening/balance period is notably more expensive than Sunday night/morning and should not be treated like Saturday.
- Period-internal price spread is small for Saturday daytime/evening, moderate for weekdays, and largest for Sunday `22:00-06:00` because Sunday 22:00-00:00 is much more expensive than Sunday 00:00-06:00 in this daytype attribution.

## Current winter production strategy derived from this table

The current planning interpretation is:

```text
Weekday:
  PV1 22:00-06:00 is the primary production window.
  Move as much movable VP production as practical from PV2/PV3 into PV1.
  PV2/PV3 normally run only the weather-dependent daytime minimum plus any required correction.
  Weekday planning is now locked as a kWh energy-budget planner, not a fixed-level brute-force planner.

Weekday kWh energy-budget planner:
  The weekday planner starts from the daily heat need, calculated from the heat-loss/weather model.
  It first reserves the minimum hydronic daytime heat for 06:00-22:00.
  Current planning assumption for this minimum is about 25 C flow temperature, approximately 3 kW heat to the house, or 6 kWh per 2h block.
  Therefore the 06:00-22:00 minimum is 8 blocks * 6 kWh = 48 kWh/day.
  If the implementation treats the minimum as 6 kW continuous instead, the value is 6 kW * 16h = 96 kWh/day; this must be explicit and not confused with 6 kWh/block.

  After daytime minimum has been subtracted, the planner allocates as much of the remaining production as practical to PV1 22:00-06:00.
  Night production is bounded by the sustainable VP capacity and by the block regulator's COP/brine/flow-temperature protection.
  A representative planning value is about 20 kW for the combined VP system across 8h, or about 160 kWh per PV1 night, but this should be calibrated from measured delivered heat.
  If the remaining need is lower than night capacity, PV1 only produces what is needed.
  If production still remains after daytime minimum and night allocation, the residual is spread across 06:00-22:00 on top of the daytime minimum.
  Residual daytime production should be smoothed unless live prices give a compelling reason to weight it.

  Formula shape:
    daily_need_kWh = heatNeedKwhDay(...)
    day_min_kWh = 8 * min_day_block_kWh
    remaining_after_day_min = max(0, daily_need_kWh - day_min_kWh)
    night_target_kWh = min(remaining_after_day_min, night_capacity_kWh)
    day_extra_kWh = max(0, remaining_after_day_min - night_target_kWh)
    day_block_target_kWh = min_day_block_kWh + day_extra_kWh / 8
    night_block_target_kWh = night_target_kWh / 4, adjusted for DHW and measured block constraints

  This means Save is not a fixed level. Save means minimum hydronic heat plus any overflow energy that cannot fit into PV1 while still meeting the daily energy budget.
  The goal is still to shift as much energy as possible to 22:00-06:00, while preserving enough daytime floor/ventilation heat to avoid undercooling.

Weekend macroblock 1, recharge:
  LP1, LP2, LP3, SP1 and SP2 form the main weekend recharge macroblock.
  Mission: move house charge from Friday 22:00 lowpoint toward 100%.
  If this macroblock can reach 100%, it should do so.
  Use smooth production across the macroblock rather than aggressive period shifting.
  The point is efficient recharge with good COP, not micro-optimizing small price differences.

Weekend macroblock 2, hold full:
  SP3 and the following Monday PV1 form the weekend hold-full macroblock.
  Mission: keep house charge at 100% until Monday 06:00 if macroblock 1 already reached full charge.
  Use smooth production across SP3 and Monday PV1.
  Do not aggressively shift between SP3 and Monday PV1 because their price difference is below the 40% COP-risk threshold.

VP intraperiod level ordering:
  Intraperiod optimization should normally not move large amounts of energy between 2h blocks.
  The period/macroblock planner first decides the required VP production level counts for the four 2h blocks.
  Because VP levels are discrete L0-L4 and neighbouring blocks will normally have similar required levels, the intraperiod optimizer only orders those already-required levels by price.
  Highest required VP levels should be assigned to the cheapest 2h blocks and lower required VP levels to the more expensive 2h blocks.
  This is not expected to create erratic patterns such as L1, L2, L3, L4 inside one period; typical period outputs should be adjacent or near-adjacent levels, for example two L4 blocks and two L3 blocks.
  In weekday PV1, the 00:00-02:00 block is a standing DHW charging exception and should always receive L4 for VP1.
  The remaining PV1 blocks should then carry similar levels and be price-ordered around that fixed DHW block.

Legacy weekday daily brute force:
  Previous discussion used a fixed-level brute-force model where the weekday 22:00 planner built a next-day plan from 12 two-hour blocks, starting with L1 base heat in all blocks plus fixed 00:00-02:00 L4 DHW.
  That legacy model only raised the three remaining PV1 blocks around the fixed DHW block:
    block 2: 22:00-00:00
    block 3: 02:00-04:00
    block 4: 04:00-06:00
  It did not raise period 2, period 3 or period 4.
  This is retained only as historical fallback context.
  The locked weekday strategy is the kWh energy-budget planner above, assuming block-level kWh production control is available.
```

These are strategy defaults. Comfort, humidity, DHW minimum, safety, stale fallback and unacceptable COP loss may override them.
