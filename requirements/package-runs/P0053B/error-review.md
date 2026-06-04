# P0053B error review

```json
{
  "best_forecast_safe_model_by_holdout": {
    "horizon_h": 1,
    "model": "M4_Ridge_G4_calendar_load_lags_weather"
  },
  "patterns": {
    "bridge_day": {
      "MAE": 42.06666486979166,
      "rows": 48
    },
    "early_morning": {
      "MAE": 29.415615514655173,
      "rows": 580
    },
    "evening": {
      "MAE": 28.38857707448276,
      "rows": 725
    },
    "holiday": {
      "MAE": 28.683888398437507,
      "rows": 192
    },
    "summer": {
      "MAE": null,
      "rows": 0
    },
    "weekend": {
      "MAE": 30.171860926587286,
      "rows": 1008
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
    },
    {
      "MAE": 59.597730895833315,
      "date": "2026-03-26",
      "hours": 24
    },
    {
      "MAE": 57.54526148958333,
      "date": "2026-01-07",
      "hours": 24
    },
    {
      "MAE": 53.162135802083334,
      "date": "2026-01-08",
      "hours": 24
    },
    {
      "MAE": 50.26667476041664,
      "date": "2026-03-19",
      "hours": 24
    },
    {
      "MAE": 48.513294572916685,
      "date": "2026-03-23",
      "hours": 24
    }
  ]
}
```
