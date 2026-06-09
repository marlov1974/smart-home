# Short chat handoff: Energy market AI lab

Date: 2026-06-09

## How to use

In the new chat, do normal `marlov1974/smart-home` bootstrap first. Then read this file.

## Current focus

We are working on realistic DayAhead consumption forecasts for the energy-market emulator, with special focus on SE2.

Old static consumption results must not be treated as realistic DayAhead performance. P0056J showed that the old static evaluation was closer to row-wise/nowcast-style testing because it could use fresh actual-lag information per target row.

Current truth is the realistic DayAhead protocol from P0056K, plus the DST fix from P0056O.

## Important package status

### P0056J

Static vs rolling row-level audit.

Conclusion:

```text
Old static results are not apples-to-apples with realistic DayAhead.
Use them only as model-ranking / upper-bound diagnostics.
```

### P0056K

Realistic DayAhead model restart.

Protocol:

```text
forecast_origin = D-1 12:00 Europe/Stockholm
delivery_day = D local delivery day
```

Best results:

```text
SE1 best: M6 WeightedEnsemble_no_price, MAE 133.471 MW
SE2 best: M6 WeightedEnsemble_no_price, MAE 232.693 MW
SE3 best: M7 HorizonBiasCorrected_WeightedEnsemble_no_price, MAE 262.426 MW
FI best: M7 HorizonBiasCorrected_WeightedEnsemble_no_price, MAE 301.566 MW
Overall best: M7
SE2 specific best: M6
```

No spot price, no flow/exchange/capacity, no old physical_balance.

### P0056L

SE2 neural smoke test.

Models:

```text
N1 Tabular MLP
N2 Sequence MLP 168h
```

Result:

```text
N1 MAE 309.342 MW
N2 MAE 374.654 MW
P0056K SE2 M6 baseline 232.693 MW
```

Conclusion:

```text
Simple neural models did not beat M6. Do not expand isolated SE2 neural tests now.
```

### P0056M

SE2 M6 DayAhead error slice analysis.

Result:

```text
PASS
240 delivery days
5760 hourly rows
Reconstructed MAE 232.692807 MW
P0056K baseline match true
```

Main pattern:

```text
M6 is mean-reverting.
High-load days: high error and underforecast.
Low-load days: lower error and overforecast.
High-ramp days much worse than low-ramp days.
Worst weekday: Saturday.
Worst season: winter.
```

Suspicious case:

```text
2026-03-28
mean actual ≈ 5487.6 MW
forecast ≈ 1800.4 MW
hourly MAE ≈ 3708.6 MW
neighboring days around 1800..2200 MW
```

### P0056N

SE2 DST and target anomaly audit.

Conclusion:

```text
2026-03-28 = probable_target_source_anomaly.
The spike is already present in native source rows.
Hourly UTC shape is normal, but source coverage is incomplete: 94 native 15-minute rows vs expected 96 and two partial hourly rows.
```

Separate DST bug confirmed:

```text
2026-03-29 Europe/Stockholm spring-forward day has 23 valid local hours.
Old P0056K/P0056M generation emitted 24 positions and created one duplicate UTC target.
```

Decision:

```text
Flag/exclude 2026-03-28 from model selection until independently verified.
Fix DayAhead DST generation before future comparisons.
```

### P0056O

DayAhead DST delivery-day generation fix.

Conclusion:

```text
PASS
Canonical representation = true local delivery-day hours.
Normal day = 24 rows.
Spring-forward day = 23 rows.
Fall-back day = 25 rows.
UTC targets unique and monotonic.
```

Verification:

```text
2026-03-29 before: 24 rows, 23 unique UTC, 1 duplicate UTC.
2026-03-29 after: 23 rows, 23 unique UTC, 0 duplicate UTC, no local 02:00.
2025-10-26 and 2026-10-25 fall-back: 25 rows, local 02:00 twice with different UTC offsets.
```

Important:

```text
2026-03-28 remains probable target/source anomaly.
No model training was performed in P0056O.
```

## Current design idea from user

The user proposed a decomposed forecast approach:

```text
forecast = normal forecast + deviation forecasts
```

Normal case:

```text
normal consumption
normal day
normal temperature for period
normal price
```

Deviation components:

```text
temperature deviation matrix
price deviation matrix
special-day deviation
ramp/regime deviation
```

Temperature idea:

```text
normal_temperature_bucket × temperature_deviation_bucket
5x5 matrix
include year sin/cos or season context
```

Price idea:

```text
normal_price_bucket × price_deviation_bucket
5x5 matrix
include year sin/cos or season context
```

Special days need richer categories:

```text
fixed-date holidays
moving holidays such as Easter
bridge days
holiday before/after workday
long weekends
weekday/weekend variants
```

Suggested later package:

```text
SE2 decomposed DayAhead normal + deviation model
```

But do source verification first.

## Immediate next step

User asked to check ENTSO-E source for the SE2 2026-03-28 anomaly.

Create/check next package:

```text
P0056P: SE2 ENTSO-E source verification for 2026-03-28 anomaly
```

Purpose:

```text
Fetch/check original or fresh ENTSO-E Actual Total Load for SE2 around 2026-03-28 and compare it to area_consumption_native_v1 and area_consumption_hourly_v1.
```

Key questions:

```text
Does the 7279 MW spike exist in fresh/original ENTSO-E?
Is the whole day extremely high?
Are 15-minute rows missing or duplicated?
Is EIC/documentType correct?
Is hourly aggregation correct?
```

Decision logic:

```text
If ENTSO-E fresh source lacks the spike: local import/cache/aggregation bug.
If ENTSO-E fresh source has the spike: source-observed anomaly; flag/exclude until independently verified.
If independent source confirms it: real load regime; then proceed with regime/deviation model work.
```

## Note about uploaded CSV

A cross-border physical-flow CSV was uploaded in the old chat. It was not added to GitHub by this handoff. Treat it as a separate future flow/capacity data task if the user asks.
