# P0054X partial coverage warning

Status: `P0054X_REMAINS_STOPPED_FOR_FULL_TAXONOMY`

P0054X must not use the current P0054W native table as full SE3 MGA consumption.

The current P0054W native table contains only the `EXP18/LoadProfile` per-MGA component. It matches `EXP15/Consumption.profiled` at SE3/MBA level and covers about 23.2% of ENTSO-E SE3 actual load over the current overlap.

The missing `metered/non_profiled` component exists at SE3/MBA level in `EXP15/Consumption.metered`, but a public per-MGA source was not found in P0054W clarification evidence.

Allowed P0054X interpretations until the missing source is resolved:

```text
partial load-profile taxonomy only
exploratory submodel taxonomy
residual-aware taxonomy with explicit SE3 residual group
```

Forbidden interpretation:

```text
full SE3 consumption taxonomy
```
