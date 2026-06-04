# P0053C-A M4 Rebuild Results

| target | split | predictor | windows | scaled_MAE | centered_MAE | spearman | top20 | bottom20 | best8 | worst8 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| system_proxy_se1 | validate | combined_scaled selected | 144.000000 | 1.680672 | 0.157886 | 0.557256 | 0.447222 | 0.441319 | 0.290799 | 0.321181 |
| system_proxy_se1 | validate | combined_dimensionless | 144.000000 | 6.104664 | 0.435454 | 0.562026 | 0.436111 | 0.455556 | 0.278646 | 0.345486 |
| system_proxy_se1 | validate | B1_AI2_only | 144.000000 | 6.037225 | 0.441282 | 0.317523 | 0.218750 | 0.331597 | 0.140625 | 0.221354 |
| system_proxy_se1 | validate | B2_AI1_day_only | 144.000000 | 1.186173 | 0.136674 | 0.514550 | 0.392708 | 0.265278 | 0.156250 | 0.190104 |
| system_proxy_se1 | validate | B3_time_profile_168h | 144.000000 | 1.747543 | 0.173219 | 0.346391 | 0.245833 | 0.291667 | 0.098958 | 0.131076 |
| system_proxy_se1 | holdout | combined_scaled selected | 348.000000 | 1.077082 | 0.164976 | 0.612268 | 0.485920 | 0.399713 | 0.307471 | 0.254310 |
| system_proxy_se1 | holdout | combined_dimensionless | 348.000000 | 4.550798 | 0.447488 | 0.624263 | 0.487644 | 0.432328 | 0.311782 | 0.298491 |
| system_proxy_se1 | holdout | B1_AI2_only | 348.000000 | 3.873009 | 0.414478 | 0.406120 | 0.272270 | 0.311063 | 0.142241 | 0.190014 |
| system_proxy_se1 | holdout | B2_AI1_day_only | 348.000000 | 0.853885 | 0.166166 | 0.496976 | 0.377299 | 0.262787 | 0.147270 | 0.168103 |
| system_proxy_se1 | holdout | B3_time_profile_168h | 348.000000 | 1.071285 | 0.188504 | 0.406306 | 0.293391 | 0.241954 | 0.147989 | 0.129310 |
| area_diff_proxy_se3 | validate | combined_scaled selected | 144.000000 | 0.610974 | 0.238237 | 0.475685 | 0.431597 | 0.316319 | 0.343750 | 0.191840 |
| area_diff_proxy_se3 | validate | combined_dimensionless | 144.000000 | 0.853625 | 0.294827 | 0.475685 | 0.431597 | 0.316319 | 0.343750 | 0.191840 |
| area_diff_proxy_se3 | validate | B1_AI2_only | 144.000000 | 0.774218 | 0.275189 | 0.395374 | 0.327778 | 0.181944 | 0.199653 | 0.083333 |
| area_diff_proxy_se3 | validate | B2_AI1_day_only | 144.000000 | 0.656377 | 0.255575 | 0.263676 | 0.249653 | 0.206597 | 0.122396 | 0.055556 |
| area_diff_proxy_se3 | validate | B3_time_profile_168h | 144.000000 | 0.734943 | 0.269888 | 0.289377 | 0.332292 | 0.153125 | 0.189236 | 0.068576 |
| area_diff_proxy_se3 | holdout | combined_scaled selected | 348.000000 | 0.829498 | 0.193085 | 0.344933 | 0.339368 | 0.221121 | 0.215876 | 0.115302 |
| area_diff_proxy_se3 | holdout | combined_dimensionless | 348.000000 | 1.952737 | 0.306003 | 0.344933 | 0.339368 | 0.221121 | 0.215876 | 0.115302 |
| area_diff_proxy_se3 | holdout | B1_AI2_only | 348.000000 | 1.463970 | 0.267842 | 0.274802 | 0.315948 | 0.126724 | 0.178879 | 0.036279 |
| area_diff_proxy_se3 | holdout | B2_AI1_day_only | 348.000000 | 0.821261 | 0.204838 | 0.202669 | 0.202730 | 0.217241 | 0.137213 | 0.080819 |
| area_diff_proxy_se3 | holdout | B3_time_profile_168h | 348.000000 | 1.263383 | 0.237489 | 0.205702 | 0.277730 | 0.115661 | 0.175647 | 0.045618 |
