# P0039 component attribution summary

Status: PASS

## Required Answers

1. M1B improves training cleanliness versus M1 by excluding 1128 of 13945 train rows from baseline fitting.
2. M1B as a standalone prediction base is diagnostic-only and worsens or does not improve full-year holdout recomposed SE3 MAE: M1=0.384666, M1B_training_base_only=0.422423.
3. M3A trained on holiday-clean data and applied on M1 changes recomposed SE3 MAE from M1=0.384666 to M1+M3A_m1b=0.376722.
4. M3B trained after M3A and applied on M1 changes recomposed SE3 MAE from M1+M3A_m1b=0.376722 to M1+M3A_m1b+M3B_m1b=0.372997.
5. M1 baseplate plus M1B-trained deltas beats previous M1-based chain: corrected chain=0.372997, existing chain=0.374846.
6. Recommendation: M1 remains the baseplate; M1B-trained deltas are promising enough for downstream experiments.

## Local Diagnostic Tables

`m1b_holiday_clean_normal_price`, `m1b_training_row_policy`, and `m3abcd_normalized_prices_m1b` are written for train/validate/holdout rows.
`m3a_temperature_delta_m1b` and `m3b_special_day_delta_m1b` are written per target and train/validate/holdout hour.
`m3c_solar_delta_m1b`, `m3d_wind_delta_m1b`, and M4_m1b outputs are deferred; their sequential target formulas are in `sequential-residual-contract.md`.

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
