# P0054W MGA-type monthly-settlement hypothesis

Status: `TESTED_NOT_SUPPORTED_BY_PUBLIC_EXP18`

## Hypothesis

The operator reported that workplace analysts often speak as if monthly-settled series are separate MGA objects.

P0054W therefore tested whether public eSett Open Data represents the missing monthly-settled/metered component as different `mgaType` objects in `EXP03/MeteringGridAreas`, rather than as a second value in the same `EXP18/LoadProfile` rows.

## Local SE3 MGA masterdata by type

```text
mgaType       count
DISTRIBUTION 179
REGIONAL      21
PRODUCTION     4
NONCON         4
TRANSMISSION   2
BORDER         1
```

## Public EXP18/Aggregate test

Endpoint:

```text
https://api.opendata.esett.com/EXP18/Aggregate
```

Query shape:

```text
mba=10Y1001A1001A46L
mga=<mga_id>
start=2025-01-01T00:00:00.000Z
end=2025-02-01T00:00:00.000Z
resolution=month
```

Important note: `EXP18/Aggregate` can return both the January and February month rows with this boundary. The evidence below filters the returned row to:

```text
timestamp = 2025-01-01T00:00:00
```

## Result by MGA type

```text
mgaType       object_count  nonempty_jan_rows  jan_2025_sum_MWh
BORDER                 1                 0              0.000
DISTRIBUTION         179               167     -2,437,920.270
NONCON                 4                 0              0.000
PRODUCTION             4                 0              0.000
REGIONAL              21                 0              0.000
TRANSMISSION           2                 0              0.000
```

## EXP15 comparison for January 2025

Public `EXP15/Consumption` for SE3/MBA, January 2025:

```text
rows: 2,976
metered_MWh:  -6,049,824.620
profiled_MWh: -2,437,945.982
total_MWh:    -8,487,770.602
```

All public `EXP18/Aggregate` rows across all SE3 `mgaType` objects:

```text
EXP18_sum_MWh: -2,437,920.270
delta_vs_EXP15_profiled_MWh: 25.712
ratio_vs_EXP15_total: 0.287227
```

## Interpretation

Public eSett Open Data does not appear to represent the missing monthly-settled/metered component as separate `REGIONAL`, `NONCON`, `TRANSMISSION`, `PRODUCTION` or `BORDER` MGA objects in `EXP18`.

The workplace phrase "monthly-settled as separate MGA objects" may still be true in an internal settlement/export/Information Service context, but it was not supported by the public Open Data `EXP03` + `EXP18` test.

For public Open Data:

```text
EXP18/Aggregate across all SE3 MGA types ~= EXP15.profiled
EXP18/Aggregate across all SE3 MGA types != EXP15.metered
EXP18/Aggregate across all SE3 MGA types != EXP15.total
```

## Consequence

P0054W remains stopped for complete SE3 per-MGA consumption. The next source search should target authenticated/internal settlement objects or exports where monthly-settled/metered classes may be represented as separate objects.
