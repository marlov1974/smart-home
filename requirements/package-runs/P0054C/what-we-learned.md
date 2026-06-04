# P0054C LABB

P0054C shows that SE4 does not automatically inherit the P0054B SE3 pattern. In this LABB setup, HGB is stronger on direct holdout while MLP is only competitive on some weekly path submetrics. Later spread/flaskhals-regime work should treat SE4 consumption residuals separately instead of assuming one advanced model family generalizes across bidding areas.

```json
{
  "assessment": "contradicts",
  "direct_holdout_confirms_se3_pattern": false,
  "direct_holdout_mlp_relative_MAE_change_percent": 19.540291807997,
  "learning_threshold": "confirm if MLP improves holdout MAE or weekly MAE_full_168h by at least 2%",
  "question": "Does SE4 confirm the SE3 pattern that MLP can beat HGB without price input?",
  "weekly_168h_confirms_se3_pattern": false,
  "weekly_168h_mlp_relative_MAE_change_percent": 1.1069944855692986
}
```
