# P0053C-A Holdout Metrics

| target | split | predictor | windows | scaled_MAE | centered_MAE | spearman | top20 | bottom20 | best8 | worst8 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| system_proxy_se1 | holdout | combined_scaled selected | 348.000000 | 1.077082 | 0.164976 | 0.612268 | 0.485920 | 0.399713 | 0.307471 | 0.254310 |
| system_proxy_se1 | holdout | combined_dimensionless | 348.000000 | 4.550798 | 0.447488 | 0.624263 | 0.487644 | 0.432328 | 0.311782 | 0.298491 |
| system_proxy_se1 | holdout | B1_AI2_only | 348.000000 | 3.873009 | 0.414478 | 0.406120 | 0.272270 | 0.311063 | 0.142241 | 0.190014 |
| system_proxy_se1 | holdout | B2_AI1_day_only | 348.000000 | 0.853885 | 0.166166 | 0.496976 | 0.377299 | 0.262787 | 0.147270 | 0.168103 |
| system_proxy_se1 | holdout | B3_time_profile_168h | 348.000000 | 1.071285 | 0.188504 | 0.406306 | 0.293391 | 0.241954 | 0.147989 | 0.129310 |
| area_diff_proxy_se3 | holdout | combined_scaled selected | 348.000000 | 0.829498 | 0.193085 | 0.344933 | 0.339368 | 0.221121 | 0.215876 | 0.115302 |
| area_diff_proxy_se3 | holdout | combined_dimensionless | 348.000000 | 1.952737 | 0.306003 | 0.344933 | 0.339368 | 0.221121 | 0.215876 | 0.115302 |
| area_diff_proxy_se3 | holdout | B1_AI2_only | 348.000000 | 1.463970 | 0.267842 | 0.274802 | 0.315948 | 0.126724 | 0.178879 | 0.036279 |
| area_diff_proxy_se3 | holdout | B2_AI1_day_only | 348.000000 | 0.821261 | 0.204838 | 0.202669 | 0.202730 | 0.217241 | 0.137213 | 0.080819 |
| area_diff_proxy_se3 | holdout | B3_time_profile_168h | 348.000000 | 1.263383 | 0.237489 | 0.205702 | 0.277730 | 0.115661 | 0.175647 | 0.045618 |
