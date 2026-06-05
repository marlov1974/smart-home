# P0054L2 Interpretation

```json
{
  "comparison": {
    "any_direct_or_weekly_2pct_improvement": true,
    "baseline": {
      "holdout_MAE": 0.34918660925661843,
      "weekly_MAE_full_168h": 0.34918660925661843
    },
    "best_completed_by_direct_MAE": {
      "bottom20_168h_precision": 0.408522727272727,
      "direct_mae_improvement_percent_vs_p0054k": 13.112984419769349,
      "holdout_MAE": 0.3033978235888772,
      "model": "Ensemble",
      "ramp_f1": 0.23862375138734737,
      "spearman": 0.6116733985652962,
      "spike_f1": 0.003482298316889147,
      "status": "completed",
      "top20_168h_precision": 0.39786931818181837,
      "weekly_MAE_full_168h": 0.3033978235888772,
      "weekly_mae_improvement_percent_vs_p0054k": 13.112984419769349
    },
    "best_completed_by_ranking": {
      "bottom20_168h_precision": 0.408522727272727,
      "direct_mae_improvement_percent_vs_p0054k": 13.112984419769349,
      "holdout_MAE": 0.3033978235888772,
      "model": "Ensemble",
      "ramp_f1": 0.23862375138734737,
      "spearman": 0.6116733985652962,
      "spike_f1": 0.003482298316889147,
      "status": "completed",
      "top20_168h_precision": 0.39786931818181837,
      "weekly_MAE_full_168h": 0.3033978235888772,
      "weekly_mae_improvement_percent_vs_p0054k": 13.112984419769349
    },
    "best_completed_by_weekly_MAE_full_168h": {
      "bottom20_168h_precision": 0.408522727272727,
      "direct_mae_improvement_percent_vs_p0054k": 13.112984419769349,
      "holdout_MAE": 0.3033978235888772,
      "model": "Ensemble",
      "ramp_f1": 0.23862375138734737,
      "spearman": 0.6116733985652962,
      "spike_f1": 0.003482298316889147,
      "status": "completed",
      "top20_168h_precision": 0.39786931818181837,
      "weekly_MAE_full_168h": 0.3033978235888772,
      "weekly_mae_improvement_percent_vs_p0054k": 13.112984419769349
    },
    "models": [
      {
        "bottom20_168h_precision": 0.3727272727272725,
        "direct_mae_improvement_percent_vs_p0054k": 11.783069214040601,
        "holdout_MAE": 0.3080417094017496,
        "model": "HGB",
        "ramp_f1": 0.24482951369480155,
        "spearman": 0.5984922425482891,
        "spike_f1": 0.01086366105377512,
        "status": "completed",
        "top20_168h_precision": 0.3963068181818187,
        "weekly_MAE_full_168h": 0.3080417094017496,
        "weekly_mae_improvement_percent_vs_p0054k": 11.783069214040601
      },
      {
        "bottom20_168h_precision": 0.4025568181818182,
        "direct_mae_improvement_percent_vs_p0054k": 11.871639440733139,
        "holdout_MAE": 0.307732434030351,
        "model": "ExtraTrees",
        "ramp_f1": 0.22886133032694478,
        "spearman": 0.5983748935964608,
        "spike_f1": 0.009044657998869417,
        "status": "completed",
        "top20_168h_precision": 0.37059659090909103,
        "weekly_MAE_full_168h": 0.307732434030351,
        "weekly_mae_improvement_percent_vs_p0054k": 11.871639440733139
      },
      {
        "bottom20_168h_precision": 0.38821022727272736,
        "direct_mae_improvement_percent_vs_p0054k": 10.028855743972287,
        "holdout_MAE": 0.314167187937004,
        "model": "LightGBM",
        "ramp_f1": 0.26321353065539116,
        "spearman": 0.5659957614834716,
        "spike_f1": 0.056116722783389444,
        "status": "completed",
        "top20_168h_precision": 0.3548295454545453,
        "weekly_MAE_full_168h": 0.314167187937004,
        "weekly_mae_improvement_percent_vs_p0054k": 10.028855743972287
      },
      {
        "bottom20_168h_precision": 0.403835227272727,
        "direct_mae_improvement_percent_vs_p0054k": 10.391453556691093,
        "holdout_MAE": 0.3129010449295325,
        "model": "XGBoost",
        "ramp_f1": 0.25504782146652494,
        "spearman": 0.5841218660486119,
        "spike_f1": 0.018952062430323303,
        "status": "completed",
        "top20_168h_precision": 0.39502840909090914,
        "weekly_MAE_full_168h": 0.3129010449295325,
        "weekly_mae_improvement_percent_vs_p0054k": 10.391453556691093
      },
      {
        "bottom20_168h_precision": 0.408522727272727,
        "direct_mae_improvement_percent_vs_p0054k": 13.112984419769349,
        "holdout_MAE": 0.3033978235888772,
        "model": "Ensemble",
        "ramp_f1": 0.23862375138734737,
        "spearman": 0.6116733985652962,
        "spike_f1": 0.003482298316889147,
        "status": "completed",
        "top20_168h_precision": 0.39786931818181837,
        "weekly_MAE_full_168h": 0.3033978235888772,
        "weekly_mae_improvement_percent_vs_p0054k": 13.112984419769349
      }
    ]
  },
  "recommendation": {
    "create_forecast_log": true,
    "decision": "advanced_holdout_source_recommended",
    "p0054m_recommendation": "A global train_fit price model is holdout-safe for evaluation, but not automatically a train-period feature source for downstream consumption training. P0054M must use holdout-only evaluation or create rolling/out-of-fold train forecasts if it needs train_fit consumption features.",
    "reason": "completed model met the P0054L2 learning threshold versus P0054K baseline",
    "recommended_model": "Ensemble"
  },
  "status": "PASS"
}
```
