# P0047 spread regime definitions

selected_strategy = T3_robust_sigma_thresholds

## T1_fixed_ore_or_currency_thresholds

- near_zero_abs: 0.010000
- positive: 0.050000
- negative: -0.050000
- spike_positive: 0.200000
- spike_negative: -0.200000

## T2_quantile_thresholds

- near_zero_abs: 0.039762
- positive: 0.434923
- negative: 0.031085
- spike_positive: 1.083767
- spike_negative: -0.010630

## T3_robust_sigma_thresholds

- near_zero_abs: 0.050000
- positive: 0.201919
- negative: -0.201919
- spike_positive: 0.807675
- spike_negative: -0.807675
- median: 0.249630
- robust_sigma: 0.403838

Recommendation: use robust-sigma thresholds as the next modeling baseline because they are data-driven, less sensitive to rare spikes than pure quantiles, and preserve a fixed near-zero floor.
