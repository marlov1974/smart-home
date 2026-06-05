# P0054N LABB

Status: `PASS`

```json
{
  "advanced_price_should_be_kept_for_future_se3_36h_experiments": true,
  "per_model_family": [
    {
      "advanced_price_helped_dayahead": false,
      "advanced_price_helped_full36": false,
      "dayahead_no_price_hourly_MAE": 149.03724768647368,
      "dayahead_relative_change_percent": 2.6519205188560515,
      "dayahead_with_advanced_price_hourly_MAE": 152.9895970386096,
      "dayahead_with_minus_no_hourly_MAE": 3.9523493521359114,
      "family": "HGB",
      "full36_no_price_MAE": 150.42261836159255,
      "full36_relative_change_percent": 2.1748752620642744,
      "full36_with_advanced_price_MAE": 153.69412267688818,
      "full36_with_minus_no_MAE": 3.27150431529563
    },
    {
      "advanced_price_helped_dayahead": true,
      "advanced_price_helped_full36": true,
      "dayahead_no_price_hourly_MAE": 166.61097844826537,
      "dayahead_relative_change_percent": -1.7227396164650977,
      "dayahead_with_advanced_price_hourly_MAE": 163.74070511715698,
      "dayahead_with_minus_no_hourly_MAE": -2.8702733311083932,
      "family": "ExtraTrees",
      "full36_no_price_MAE": 168.61915663873685,
      "full36_relative_change_percent": -2.0171808761318664,
      "full36_with_advanced_price_MAE": 165.21780325752542,
      "full36_with_minus_no_MAE": -3.401353381211436
    },
    {
      "advanced_price_helped_dayahead": true,
      "advanced_price_helped_full36": true,
      "dayahead_no_price_hourly_MAE": 161.20263771340532,
      "dayahead_relative_change_percent": -1.9814799968529022,
      "dayahead_with_advanced_price_hourly_MAE": 158.00843969271494,
      "dayahead_with_minus_no_hourly_MAE": -3.1941980206903793,
      "family": "LightGBM",
      "full36_no_price_MAE": 165.29492758744647,
      "full36_relative_change_percent": -3.1528158370773567,
      "full36_with_advanced_price_MAE": 160.0834829325839,
      "full36_with_minus_no_MAE": -5.211444654862561
    },
    {
      "advanced_price_helped_dayahead": false,
      "advanced_price_helped_full36": false,
      "dayahead_no_price_hourly_MAE": 151.9629052301118,
      "dayahead_relative_change_percent": 2.9528826175175213,
      "dayahead_with_advanced_price_hourly_MAE": 156.4501914437264,
      "dayahead_with_minus_no_hourly_MAE": 4.4872862136145955,
      "family": "XGBoost",
      "full36_no_price_MAE": 153.95677124793977,
      "full36_relative_change_percent": 2.9719446171397648,
      "full36_with_advanced_price_MAE": 158.5322812237651,
      "full36_with_minus_no_MAE": 4.575509975825327
    }
  ],
  "required_model_pairs_complete": true
}
```
