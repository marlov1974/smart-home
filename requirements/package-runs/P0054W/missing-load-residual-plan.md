# P0054W missing load residual plan

Status: `REQUIRED_FOR_FUTURE_MODELING_IF_METERED_PER_MGA_SOURCE_REMAINS_MISSING`

## Problem

P0054W loaded valid per-MGA `EXP18/LoadProfile` data, but that source covers only about 23.2% of SE3 total load over the current overlap with ENTSO-E actual load.

The missing component is primarily `metered/non_profiled` consumption visible at SE3/MBA level in `EXP15/Consumption.metered`, but not found per MGA in public eSett Open Data.

## Do not do this

Do not treat `EXP18/LoadProfile` as total SE3 MGA consumption.

Do not allocate `EXP15.metered` to MGAs by a naive static share and label the result observed per-MGA load.

Do not build P0054X full 32-cluster taxonomy as if the current native table covers all consumption.

## Allowed future fallback options

### A. Obtain the missing per-MGA source

Preferred path.

Possible source classes:

```text
operator-provided local export
authenticated eSett/NBS Information Service query with MGA and SettlementMethodType
approved DSO/Svenska kraftnät/eSett source that exposes metered/non_profiled per MGA
```

The source must preserve:

```text
MGA
timestamp
native 15m/60m resolution
settlement method or measurement class
unit and sign convention
publication/version if available
```

### B. Measured residual model

If no per-MGA metered source is available, model the missing part explicitly:

```text
SE3_residual_load = ENTSO-E_SE3_actual_load - sum(P0054W_EXP18_LoadProfile_per_MGA)
```

This residual must be labeled as `se3_residual_missing_metered_or_unmapped_load`, not as per-MGA observed load.

### C. Hybrid exploratory hierarchy

Use the loaded per-MGA `EXP18/LoadProfile` component as an explanatory submodel, then reconcile against the direct SE3 model or residual model.

P0054X output under this path must be labeled:

```text
partial load-profile taxonomy only
not full SE3 consumption taxonomy
```

### D. Direct SE3 production candidate

Keep SE3 direct consumption forecasting as the production candidate until full per-MGA coverage exists.

## Recommended next package

Create a source-acquisition package specifically for per-MGA `metered/non_profiled` 15m/60m consumption.

The package should first test whether an authenticated eSett/NBS Information Service query can request:

```text
MGA
SettlementMethodType = E02 Non-profiled
BusinessType = A04 Consumption
Resolution = PT15M or PT60M
```

No credentials should be committed. If authenticated access is required, store only source contract evidence and operator instructions unless the package explicitly approves a local secret integration.
