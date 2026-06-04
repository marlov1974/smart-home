# P0053B-A2 Required Answers

1. Consumption target source: `physical_balance_se1_se4_hourly_v1`, target `consumption_se1_mw`.
2. Anchored price forecast log: `m4_48h_anchored_absolute_price_forecast_log_p0053cb_v1`.
3. Weekly holdout origins: yes, 50 weekly origins from `2025-06-01T23:00:00Z` through `2026-05-10T23:00:00Z`; 348 complete daily 168h holdout paths existed and every seventh complete origin was selected.
4. Weather forecast proxy: realized weather outcome labeled `weather_actual_as_forecast_proxy`.
5. G7 features created: target price, horizon, 24h/168h relative price, 168h/day ranks, top4/top8/bottom4 day flags, daily spread, first-24h volatility, daily peak-half and low-half flags.
6. Ridge plus_G7 holdout improvement: no; Ridge plus_G7 degraded all reported direct horizons and weekly path MAE.
7. HGB plus_G7 holdout improvement: no material improvement; small direct-horizon improvements appeared at some longer horizons, but weekly 168h MAE worsened slightly.
8. Weekly 168h path improvement: no; M4 Ridge worsened and M7 HGB worsened slightly with plus_G7.
9. Conditional top/bottom price-hour improvement: no robust improvement; most high/top price-hour subsets worsened, with only tiny isolated HGB low/holiday subset improvements.
10. SE1 price response detectable: no, classified `no_price_response_detected`.
11. Keep price forecast features for SE1 consumption: no for current SE1 consumption model path.
12. Repeat for SE2/SE3/SE4: only after train-period forecast-feature coverage exists, or as an explicitly offline diagnostic.
13. Deployable: no; offline only because weather uses realized proxy and P0053C-B price log lacks canonical train-period coverage.
14. Leakage/API/device confirmation: no actual future price leakage, no future A09/A11 leakage, no production/export/import model, no A61 utilization, no API and no device actions.
