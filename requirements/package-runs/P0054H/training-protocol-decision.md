# P0054H Training Protocol Decision

Decision:

```text
origin_local_no_fit_pre_origin_history
```

P0054H does not train an upstream AI1/AI2 M4 model. It uses an origin-local baseline with no fitted parameters crossing forecast origins.

Why not M4:

Safe train-period M4 would require rolling-origin, expanding-origin or blocked out-of-fold AI1/AI2 training. That is larger and slower than needed to unblock a forecast-safe downstream ablation source. The package allows a simpler anchored baseline when clearly labeled.

Method:

```text
previous_week_same_hour_else_hist48_same_hour_else_hist48_median
```

Status: `WARN`
