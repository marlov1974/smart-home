# P0041 next model training plan

P0042 should train AI-2 first because the fixed hour-to-day target is simpler, has far more rows, and directly validates intraday shape quality before the lower-row AI-1 day-to-local-week model is trained. Use bounded tabular gradient boosting such as `HistGradientBoostingRegressor`; do not start with neural or transformer models.
