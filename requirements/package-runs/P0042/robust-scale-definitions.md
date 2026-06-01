# P0042 robust scale definitions

SE1 uses P0041 generic robust scale with floor `0.001`.

area_diff uses `max(generic_robust_scale, area_diff_scale_floor)`, where `area_diff_scale_floor` is the median generic complete fixed-CET day scale for area_diff in the available historical dataset.

area_diff_scale_floor = 0.105683

No primary clipping is applied.
