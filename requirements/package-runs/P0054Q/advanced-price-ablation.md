# P0054Q LABB

Status: `PASS`

```json
{
  "advanced_price_should_be_kept_for_future_se3_36h_experiments": false,
  "per_model_family": [
    {
      "advanced_price_helped_dayahead": false,
      "advanced_price_helped_full36": false,
      "dayahead_no_price_hourly_MAE": 633.9756164783805,
      "dayahead_relative_change_percent": 3.785940117110817,
      "dayahead_with_advanced_price_hourly_MAE": 657.9775536753361,
      "dayahead_with_minus_no_hourly_MAE": 24.001937196955623,
      "family": "HGB",
      "full36_no_price_MAE": 650.4293204412376,
      "full36_relative_change_percent": 4.045547188382479,
      "full36_with_advanced_price_MAE": 676.7427455267633,
      "full36_with_minus_no_MAE": 26.31342508552575
    },
    {
      "advanced_price_helped_dayahead": false,
      "advanced_price_helped_full36": true,
      "dayahead_no_price_hourly_MAE": 682.2040938064617,
      "dayahead_relative_change_percent": 0.558537536591901,
      "dayahead_with_advanced_price_hourly_MAE": 686.0144597465375,
      "dayahead_with_minus_no_hourly_MAE": 3.8103659400757124,
      "family": "ExtraTrees",
      "full36_no_price_MAE": 694.1610644264334,
      "full36_relative_change_percent": -0.2479664333318366,
      "full36_with_advanced_price_MAE": 692.4397779933969,
      "full36_with_minus_no_MAE": -1.7212864330365392
    },
    {
      "advanced_price_helped_dayahead": false,
      "advanced_price_helped_full36": false,
      "dayahead_no_price_hourly_MAE": 632.7869013389628,
      "dayahead_relative_change_percent": 3.7204815610332043,
      "dayahead_with_advanced_price_hourly_MAE": 656.3296213239123,
      "dayahead_with_minus_no_hourly_MAE": 23.542719984949485,
      "family": "LightGBM",
      "full36_no_price_MAE": 644.9873394113744,
      "full36_relative_change_percent": 4.145029185259476,
      "full36_with_advanced_price_MAE": 671.7222528712044,
      "full36_with_minus_no_MAE": 26.734913459830068
    },
    {
      "advanced_price_helped_dayahead": false,
      "advanced_price_helped_full36": false,
      "dayahead_no_price_hourly_MAE": 634.078904190088,
      "dayahead_relative_change_percent": 5.001722725542657,
      "dayahead_with_advanced_price_hourly_MAE": 665.7937728388355,
      "dayahead_with_minus_no_hourly_MAE": 31.714868648747483,
      "family": "XGBoost",
      "full36_no_price_MAE": 648.0211775938925,
      "full36_relative_change_percent": 5.402175932980352,
      "full36_with_advanced_price_MAE": 683.0284216904856,
      "full36_with_minus_no_MAE": 35.007244096593126
    }
  ],
  "required_model_pairs_complete": true
}
```
