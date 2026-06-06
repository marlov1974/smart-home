# P0054V2 LABB

Status: `PASS`

```json
{
  "best_broad_family": {
    "MAE_full_36h": 242.5642604364506,
    "absolute_daily_energy_error_MWh": 4346.592563127953,
    "daily_energy_delta_vs_P0_percent": 0.0,
    "family": "P0_no_price",
    "full36_delta_vs_P0_percent": 0.0,
    "hourly_MAE_delivery_day": 252.4272878651775,
    "prediction_column": "pred_HorizonBiasCorrected_WeightedEnsemble_P0_no_price",
    "price_family_delta_vs_P0_MW": 0.0,
    "price_family_delta_vs_P0_percent": 0.0
  },
  "best_high_risk_regime": {
    "delta_percent": -0.6998468530605615,
    "family": "P4_spike_ramp",
    "family_mae": 227.74113924659798,
    "p0_mae": 229.34621149032665,
    "regime": "low_price"
  },
  "conditional_threshold": "high-risk regime improves >=10% and broad DayAhead worsens <=1%",
  "default_threshold": "DayAhead MAE improves >=2%, full36 worsens <=1%, daily energy worsens <=1%",
  "final_decision": "excluded"
}
```
