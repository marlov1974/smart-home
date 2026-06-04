# P0053B error review

```json
{
  "best_forecast_safe_model_by_holdout": {
    "horizon_h": 1,
    "model": "M4_Ridge_G4_calendar_load_lags_weather"
  },
  "patterns": {
    "bridge_day": {
      "MAE": 33.76152140277778,
      "rows": 72
    },
    "early_morning": {
      "MAE": 22.09309471274373,
      "rows": 1436
    },
    "evening": {
      "MAE": 20.729287323537605,
      "rows": 1795
    },
    "holiday": {
      "MAE": 23.648826321614578,
      "rows": 384
    },
    "summer": {
      "MAE": 10.523941124830104,
      "rows": 2207
    },
    "weekend": {
      "MAE": 21.903609823553264,
      "rows": 2471
    }
  },
  "selected_reference": "B1_same_hour_previous_week on holdout, used for transparent top-day review",
  "top_error_days": [
    {
      "MAE": 99.88227570833334,
      "date": "2026-01-18",
      "hours": 24
    },
    {
      "MAE": 98.8659732604167,
      "date": "2026-01-17",
      "hours": 24
    },
    {
      "MAE": 89.29973579166665,
      "date": "2026-01-16",
      "hours": 24
    },
    {
      "MAE": 88.70966342708334,
      "date": "2026-01-03",
      "hours": 24
    },
    {
      "MAE": 82.03272269791667,
      "date": "2026-01-15",
      "hours": 24
    },
    {
      "MAE": 78.45069997916666,
      "date": "2026-01-04",
      "hours": 24
    },
    {
      "MAE": 76.99906627083332,
      "date": "2026-01-02",
      "hours": 24
    },
    {
      "MAE": 75.09634311458332,
      "date": "2025-11-20",
      "hours": 24
    },
    {
      "MAE": 72.79576546874999,
      "date": "2026-01-19",
      "hours": 24
    },
    {
      "MAE": 70.86007863541668,
      "date": "2026-01-01",
      "hours": 24
    },
    {
      "MAE": 70.11406396875003,
      "date": "2025-11-11",
      "hours": 24
    },
    {
      "MAE": 70.10245651041667,
      "date": "2025-12-03",
      "hours": 24
    },
    {
      "MAE": 69.177211125,
      "date": "2026-01-05",
      "hours": 24
    },
    {
      "MAE": 67.56278675,
      "date": "2026-01-20",
      "hours": 24
    },
    {
      "MAE": 65.1193101875,
      "date": "2026-01-06",
      "hours": 24
    },
    {
      "MAE": 64.37558797916667,
      "date": "2025-11-29",
      "hours": 24
    },
    {
      "MAE": 64.25087734374999,
      "date": "2025-11-12",
      "hours": 24
    },
    {
      "MAE": 63.71139609374999,
      "date": "2026-03-18",
      "hours": 24
    },
    {
      "MAE": 62.99360713541665,
      "date": "2026-01-24",
      "hours": 24
    },
    {
      "MAE": 62.296692447916676,
      "date": "2026-01-21",
      "hours": 24
    }
  ]
}
```
