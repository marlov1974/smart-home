# P0054W next package recommendation

Recommended next step: source acquisition for missing per-MGA `metered/non_profiled` 15m/60m consumption, or explicit residual-aware modeling.

Do not use `esett_mga_consumption_native_v1` as full SE3 consumption. It currently contains the `EXP18/LoadProfile` component only.

Use it as source of truth only for the loaded `profiled/load_profile` component and keep `settlement_class` plus `resolution_minutes` in every feature.

For full bottom-up SE3 modeling, first obtain a defensible per-MGA source for the missing `metered/non_profiled` component, or create a package-approved residual plan:

```text
SE3_residual_load = ENTSO-E_SE3_actual_load - sum(P0054W_EXP18_LoadProfile_per_MGA)
```
