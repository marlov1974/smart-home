# P0054Y function design

Status: `STOP before code`

No functions are created, changed or removed.

The package is stopped because its required input class conflicts with repository evidence:

```text
expected input: measured 15m/60m MGA load
available input: profiled/load-profile per-MGA component
missing input: metered/non_profiled per-MGA component
```

If the input conflict is resolved in a future package, the likely function set should include:

```text
load_measured_mga_hourly_rows(...)
assign_measured_mga_clusters(...)
aggregate_measured_clusters_hourly(...)
compute_se3_residual_hourly(...)
write_decomposition_tables(...)
validate_decomposition_quality(...)
write_p0054y_evidence(...)
```
