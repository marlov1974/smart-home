# P0036 model selection

| target | selected_candidate | algorithm | parameters | validate_mae | elapsed_seconds |
|---|---|---|---|---:|---:|
| area_diff_proxy_se3 | hgb_area_diff_proxy_se3_002 | sklearn_hist_gradient_boosting_regressor | `{"early_stopping": true, "l2_regularization": 0.1, "learning_rate": 0.03, "max_iter": 50, "max_leaf_nodes": 7, "min_samples_leaf": 100, "random_state": 36}` | 0.272021 | 0.189669 |
| system_proxy_se1 | hgb_system_proxy_se1_014 | sklearn_hist_gradient_boosting_regressor | `{"early_stopping": true, "l2_regularization": 0.1, "learning_rate": 0.05, "max_iter": 100, "max_leaf_nodes": 7, "min_samples_leaf": 100, "random_state": 36}` | 0.260905 | 0.146979 |

PolynomialFeatures/Ridge is not used as the P0036 primary M4 model.
