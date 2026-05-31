# P0039 component attribution summary

Status: WARN

## Required Answers

1. M1B improves training cleanliness versus M1 by excluding 1128 of 13945 train rows from baseline fitting.
2. M1B alone worsens or does not improve full-year holdout recomposed SE3 MAE: M1=0.384666, M1B=0.422423.
3. M3A trained on holiday-clean data changes recomposed SE3 MAE from M1B=0.422423 to M1B+M3A=0.414329.
4. M3B trained after M3A changes recomposed SE3 MAE from M1B+M3A=0.414329 to M1B+M3A+M3B=0.408190.
5. M1B sequential chain does not beat previous M1-based chain: M1B chain=0.408190, existing chain=0.376549.
6. Recommendation: keep M1 as production reference until M1B downstream components beat the existing chain.

## Local Diagnostic Tables

`m1b_holiday_clean_normal_price`, `m1b_training_row_policy`, and `m3abcd_normalized_prices_m1b` are written for train/validate/holdout rows.
`m3a_temperature_delta_m1b` and `m3b_special_day_delta_m1b` are written per target and train/validate/holdout hour.
`m3c_solar_delta_m1b`, `m3d_wind_delta_m1b`, and M4_m1b outputs are deferred; their sequential target formulas are in `sequential-residual-contract.md`.

No M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
