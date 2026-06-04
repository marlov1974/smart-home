# P0053B 168h path metrics

```json
{
  "B1_same_hour_previous_week_path": {
    "holdout": {
      "MAE_0_24h": 29.13947639424817,
      "MAE_24_48h": 28.837499902928737,
      "MAE_48_72h": 28.385941671950476,
      "MAE_72_168h": 27.26253056359451,
      "MAE_full_168h": 27.91614860335792,
      "bias_full_168h": 6.759065883313923,
      "daily_energy_error_proxy": 633.5358607140267,
      "origin_count": 138,
      "peak_hour_error": 60.14896411956522
    },
    "validate": {
      "MAE_0_24h": 20.29067764626142,
      "MAE_24_48h": 20.327487406307082,
      "MAE_48_72h": 20.4319710466895,
      "MAE_72_168h": 20.537123116952063,
      "MAE_full_168h": 20.456946938152303,
      "bias_full_168h": -0.027111789636333018,
      "daily_energy_error_proxy": 451.4888826718201,
      "origin_count": 365,
      "peak_hour_error": 55.29243343972601
    }
  },
  "B4_recent_24h_adjusted_path": {
    "holdout": {
      "MAE_0_24h": 18.541506147503643,
      "MAE_24_48h": 21.145354927247972,
      "MAE_48_72h": 22.85632815032133,
      "MAE_72_168h": 26.863217765955024,
      "MAE_full_168h": 24.285151469841857,
      "bias_full_168h": 4.705175674986432,
      "daily_energy_error_proxy": 450.45267468126434,
      "origin_count": 138,
      "peak_hour_error": 60.71305251282238
    },
    "validate": {
      "MAE_0_24h": 17.392788706973082,
      "MAE_24_48h": 19.548097038550196,
      "MAE_48_72h": 20.703992994758153,
      "MAE_72_168h": 22.875362873668802,
      "MAE_full_168h": 21.30661860499382,
      "bias_full_168h": -0.08945028305113882,
      "daily_energy_error_proxy": 379.6110666106506,
      "origin_count": 365,
      "peak_hour_error": 56.84247301360841
    }
  }
}
```
