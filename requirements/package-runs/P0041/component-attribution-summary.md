# P0041 component attribution summary

Status: PASS
source_row_counts = {'train': 13945, 'validate': 8784, 'holdout': 8760, 'future': 3503}
AI-1 row counts = {'area_diff_proxy_se3': 1396, 'system_proxy_se1': 1396}
AI-2 row counts = {'area_diff_proxy_se3': 34800, 'system_proxy_se1': 34800}
skipped incomplete AI-1 center dates = 62
all robust scales strictly positive = True
AI-2 max abs mean hour_shape by date/target = 0.000000
Near-zero and negative prices are handled by additive centered targets and diagnostic ratios are null when denominators are unsafe.
Weather actual/normal/delta features are present for temperature, solar and wind.
SE1 and SE3-SE1 are separate throughout.
No AI training, M5/M6/M7/API, Shelly, Home Assistant, KVS or device action was performed.
