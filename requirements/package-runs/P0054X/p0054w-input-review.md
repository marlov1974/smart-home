# P0054X P0054W input review

Status: `NOT USABLE FOR FULL SE3 MGA TAXONOMY`

## P0054W Loaded Data

P0054W created:

- `esett_mga_masterdata_v1`
- `esett_mga_consumption_native_v1`
- `esett_mga_consumption_ingestion_checkpoint_v1`

Loaded P0054W facts:

```text
SE3 MGA masterdata rows: 211
MGAs with EXP18 rows: 170
native rows: 14,875,628
resolution: 15 minutes
settlement_class: profiled_load_profile
loaded range: 2023-10-31T23:00:00Z..2026-06-05T23:45:00Z
```

## Coverage Against SE3 Total Load

P0054W SE3 sanity check:

```text
joined_hours: 22,709
average eSett MGA load-profile hourly MWh: 2,345.319
average ENTSO-E SE3 actual load MW: 9,807.543
average ratio: 0.232195
```

Interpretation: P0054W loaded the per-MGA profiled/load-profile component, not total SE3 consumption.

## Endpoint Cross-Check

Public eSett Open Data endpoints inspected:

```text
EXP03/MeteringGridAreas
EXP15/Aggregate
EXP15/Consumption
EXP18/Aggregate
EXP18/LoadProfile
```

`EXP18/Aggregate` per MGA returns monthly aggregates for the same load-profile component.

`EXP18/Aggregate` without an MGA filter matches the `profiled` component of `EXP15/Aggregate`, not `metered`.

`EXP15/Aggregate` exposes `metered`, `profiled`, and `total`, but only by MBA/SE3, not by MGA.

## Conclusion

The measured/monthly-read per-MGA component remains missing. P0054X cannot produce a trustworthy full SE3 MGA taxonomy until that source exists.
