# P0054Y2 residual definition

```text
se3_residual_metered_non_profiled_mw =
  ENTSO-E SE3 actual total load MW
  - sum(profiled/load-profile MGA cluster MW)
```

Residual is a calculated historical balancing component. It is not directly observed per-MGA measured load and must not be used as a future actual feature.
