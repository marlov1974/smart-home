# P0041 robust scale definitions

fixed_min_scale = 0.001

robust_scale(values) = max(percentile_75(values) - percentile_25(values), median_absolute_deviation(values) * 1.4826, abs(mean(values)) * 0.10, fixed_min_scale)

Ratio diagnostics use null when `abs(denominator) < fixed_min_scale`. Negative prices are valid for shape targets because additive centered differences and robust positive scales are used.
