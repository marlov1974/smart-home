# P0054Y P0054W input review

Status: `NOT_USABLE_AS_MEASURED_INPUT`

## Available local input

```text
table: esett_mga_consumption_native_v1
source_name: EXP18/LoadProfile
settlement_class: profiled_load_profile
rows: 14,875,628
MGAs with rows: 170
range: 2023-10-31T23:00:00Z..2026-06-05T23:45:00Z
```

## Coverage evidence

P0054W coverage evidence:

```text
loaded_component_coverage_percent: 23.2195
missing_or_residual_percent: 76.7805
```

Public eSett cross-check for Jan-Apr 2025 shows local P0054W monthly sums match `EXP15.profiled`, not `EXP15.metered` or `EXP15.total`.

## Consequence for P0054Y

The available P0054W rows can be used only as a `profiled/load_profile` component.

They must not be used as:

```text
measured 15m/60m MGA load
metered/non_profiled MGA load
full SE3 per-MGA load
```
