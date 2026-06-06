# P0054W operator clarification: profiled/monthly load is critical

## Status

clarification for P0054W and P0054X

## Operator finding

Current eSett/MGA discovery appears to find only measured 15m/60m series. Without monthly-settled/profiled series, the loaded MGA data covers only approximately 23% of SE3 consumption.

This is not sufficient as a complete SE3 bottom-up consumption source.

## Required interpretation

If P0054W finds only measured 15m/60m series and total coverage is around 23%, it must not present the dataset as complete SE3 MGA consumption.

It must classify the result as one of:

```text
WARN: measured-only MGA source found, profiled/monthly source missing, bottom-up coverage incomplete
STOP: no defensible way to include or model the missing profiled/monthly majority
```

Do not proceed to P0054X full 32-cluster taxonomy as if all consumption is covered.

## Required next search

P0054W must explicitly search for the missing profiled/monthly-settled consumption source using all available local/source terms.

Search terms/classes include:

```text
profiled
profile
monthly
monthly_settled
non_hourly
non_metered
annual_profile
load_profile
settlement
consumption_profiled
residual_load
preliminary profiled consumption
final profiled consumption
mga profiled consumption
NBS profiled consumption
esett profiled consumption
```

Also inspect whether eSett/NBS exposes this as:

```text
separate settlement type
separate time series type
profile allocation
residual/proportion series
monthly volume with hourly profile allocation
consumption by balance supplier/customer category
```

## Coverage gate

Before using MGA data as SE3 bottom-up candidate, P0054W must compute coverage versus ENTSO-E SE3 actual load:

```text
measured_15m_60m_coverage_percent
profiled_monthly_coverage_percent
unknown_or_missing_coverage_percent
total_mga_coverage_percent
```

Decision thresholds:

```text
>= 90% total coverage: usable for bottom-up SE3 modeling candidate
70-90% total coverage: WARN, possibly usable with residual model
< 70% total coverage: not usable as complete bottom-up SE3 source without explicit residual/missing-load model
~23% measured-only coverage: incomplete, must search profiled/monthly or create residual plan
```

## Residual load fallback

If profiled/monthly series cannot be found, P0054W must recommend one of these explicit fallback strategies instead of pretending the measured data is complete:

```text
A. measured-MGA model + residual SE3 model
B. measured-MGA clusters only as explanatory submodel, reconciled to SE3 direct model
C. wait for profiled/monthly source before bottom-up modeling
D. use SE3 direct model as production candidate and keep MGA analysis exploratory
```

Residual definition if used later:

```text
SE3_residual_load = ENTSO-E_SE3_actual_load - sum(measured_MGA_load)
```

The residual model would represent missing monthly/profiled load and unmapped/unknown consumption.

## Impact on P0054X

P0054X must not build the final 32-cluster taxonomy as if measured-only coverage represents all SE3 consumption.

If only 23% measured coverage exists, P0054X may still classify measured MGAs, but must label the output:

```text
partial measured-load taxonomy only
not full SE3 consumption taxonomy
```

For the intended full 32-cluster taxonomy, P0054X needs either:

```text
profiled/monthly series included
or an explicit residual/missing-load group
```

## Required evidence additions

P0054W must include:

```text
requirements/package-runs/P0054W/profiled-monthly-source-search.md
requirements/package-runs/P0054W/coverage-vs-entsoe-by-settlement-class.md
requirements/package-runs/P0054W/missing-load-residual-plan.md
```

P0054X, if run on partial data, must include:

```text
requirements/package-runs/P0054X/partial-coverage-warning.md
```

## Relationship to packages

This clarification strengthens and amends:

```text
requirements/packages/P0054W-labb-esett-mga-consumption-discovery.md
requirements/packages/P0054X-labb-se3-mga-cluster-taxonomy.md
requirements/packages/P0054X-operator-clarification-32-clusters.md
```

If there is any conflict, follow this clarification.
