# P0054Y design

Status: `STOP before implementation`

## Intended package design if the input conflict is resolved

If a future package supplies actual `metered/non_profiled` per-MGA data, P0054Y can create:

```text
se3_measured_mga_cluster_hourly_v1
se3_consumption_residual_hourly_v1
se3_consumption_decomposition_hourly_v1
```

The measured cluster table would aggregate only defensibly measured/non-profiled 15m/60m MGA rows.

The residual table would compute:

```text
residual = ENTSO-E SE3 actual total load - measured_cluster_sum
```

## Why implementation is stopped now

Current P0054W data is `profiled_load_profile`, not measured/non-profiled load. Using it as measured input would create mislabeled outputs and misleading downstream forecasting targets.

## Files intentionally not changed

```text
src/mac/**
tests/mac/**
docs/functions/**
local database tables
```

## Verification strategy for this STOP package

Evidence-only verification:

```text
git diff --check
```

No unit/model tests are required because no source code or database writes are performed.
