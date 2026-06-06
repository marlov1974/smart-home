# P0054W coverage versus SE3 total by settlement class

Status: `PARTIAL_COVERAGE`

## Local DB coverage

Local table:

```text
esett_mga_consumption_native_v1
```

Current loaded settlement classes:

```text
profiled_load_profile
```

Rows:

```text
14,875,628
```

MGAs with rows:

```text
170
```

Range:

```text
2023-10-31T23:00:00Z..2026-06-05T23:45:00Z
```

Total positive source energy loaded:

```text
53,326,849.770846 MWh
```

## ENTSO-E total coverage sanity

Comparison:

```text
sum(-eSett EXP18 LoadProfile MGA MWh per hour)
versus
ENTSO-E SE3 actual load MW for the same UTC hour
```

Observed overlap:

```text
joined_hours: 22,709
range: 2023-10-31T23:00:00Z..2026-06-05T10:00:00Z
avg_mga_hour_mwh: 2,345.31913091039
avg_entsoe_mw: 9,807.54264828923
loaded_component_coverage_ratio: 0.232195464720034
missing_or_residual_ratio: 0.767804535279966
```

Interpretation:

```text
loaded_component_coverage_percent: 23.2195%
unknown_or_missing_coverage_percent: 76.7805%
total_mga_coverage_percent_available_in_local_db: 23.2195%
```

This is below the `<70%` gate for use as a complete bottom-up SE3 source.

## eSett EXP15 cross-check

Public `EXP15/Consumption` exposes SE3/MBA 15m consumption split by measurement class:

```text
month    intervals  metered_MWh       profiled_MWh      total_MWh
2025-01  2976       -6,049,824.620    -2,437,945.982    -8,487,770.602
2025-02  2688       -5,593,783.595    -2,217,665.555    -7,811,449.150
2025-03  2976       -5,508,071.038    -1,921,013.711    -7,429,084.749
2025-04  2880       -4,824,065.606    -1,455,851.428    -6,279,917.035
```

Local P0054W `EXP18/LoadProfile` per-MGA sum for the same months:

```text
month    local_source_sum_MWh
2025-01  -2,437,927.120
2025-02  -2,217,647.043
2025-03  -1,920,995.885
2025-04  -1,455,836.649
```

The local P0054W series matches `EXP15.profiled`, not `EXP15.metered` or `EXP15.total`.

## Settlement coverage table

```text
settlement_or_measurement_class       local_per_mga_source      coverage_status
profiled/load_profile                 EXP18/LoadProfile         loaded per MGA
metered/non_profiled                  not found per MGA         missing per MGA
flex                                  not found per MGA         missing or null in sampled SE3 EXP15
SE3/MBA total                         EXP15/Consumption.total   available only at MBA level
```

## Gate result

`STOP` for complete per-MGA SE3 bottom-up modeling.

`WARN/PASS` only for exploratory analysis explicitly scoped to the loaded `profiled/load_profile` component or for later residual modeling that reconciles against SE3 total.
