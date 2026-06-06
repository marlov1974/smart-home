# P0054W profiled/monthly source search

Status: `FOUND_PARTIAL_SOURCE_BUT_NOT_FULL_MGA_TOTAL`

## Operator clarification

The missing class must not be searched as monthly-resolution data only. The relevant Swedish settlement split can still be delivered as 15/60 minute time series, while being financially settled monthly.

P0054W therefore treats resolution and settlement method as separate dimensions:

```text
resolution: 15m / 60m / monthly / unknown
settlement or measurement class: profiled/load_profile / metered/non_profiled / flex / unknown
```

## Sources inspected

Local:

```text
esett_mga_masterdata_v1
esett_mga_consumption_native_v1
esett_mga_consumption_ingestion_checkpoint_v1
entsoe_consumption_area_hourly_v1
repo source/evidence for EXP15, EXP18, LoadProfile, Aggregate, Consumption, settlement and profile terms
```

Public eSett Open Data contract:

```text
/EXP03/MeteringGridAreas
/EXP15/Consumption
/EXP18/LoadProfile
/EXP18/Aggregate
```

## Findings

`EXP18/LoadProfile` provides per-MGA 15m rows and is what P0054W loaded.

For Jan-Apr 2025, the local P0054W per-MGA sum matches `EXP15/Consumption.profiled` at SE3/MBA level. It does not match `EXP15/Consumption.metered` or `total`.

`EXP15/Consumption` exposes 15m `metered`, `profiled`, `flex` and `total`, but only by MBA. Supplying an `mga` query parameter does not make the response per-MGA; the response still contains only `mba`.

`EXP18/Aggregate` can aggregate `EXP18/LoadProfile` per MGA by month, but this is an aggregation of the same load-profile source, not a separate missing class.

No inspected public eSett Open Data endpoint exposes `metered/non_profiled` consumption per MGA.

## Interpretation

The loaded P0054W source is a valid per-MGA source for the `profiled/load_profile` component. It is not complete SE3 MGA consumption.

The missing majority is the `metered/non_profiled` component, which exists in public eSett Open Data at SE3/MBA level via `EXP15/Consumption.metered`, but was not found per MGA in the public Open Data API.

## Current package decision

P0054W is `STOP` for complete SE3 bottom-up per-MGA consumption until one of these exists:

```text
1. a public/project-approved per-MGA source for metered/non_profiled 15m/60m consumption,
2. an operator-provided local export with MGA and settlement method,
3. a package-approved authenticated eSett/NBS Information Service integration,
4. an explicit later package that models the missing component as SE3 residual rather than per-MGA load.
```
