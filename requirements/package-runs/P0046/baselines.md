# P0046 baselines

B0_anchor_flat: future hours equal mean anchor price.

B1_anchor_last_known: future hours equal last anchor price.

B2_anchor_time_profile: train-only fixed-CET weekday/hour profile, centered as shape and anchored with L1/L2/L3.

B3_P0045_AI1_only_anchor: P0045 AI1-only shape anchored with L1/L2/L3.

B4_P0045_AI2_only_anchor: P0045 AI2-only shape anchored with L1/L2/L3.

B5_oracle_anchor_upper_bound: actual future centered shape anchored with L1/L2/L3; diagnostic only and excluded from deployable selection.
