# P0056D Implementation Design

## Interpretation

P0056D builds a LABB-only weather proxy retune for SE1, SE2 and FI. It creates explicit weather zones, assigns documented zone weights, fetches Open-Meteo historical hourly weather for representative locations, aggregates those observations into versioned area weather proxy/features tables, then reruns the same no-price P0056C consumption model for the three scoped areas.

The package does not promote a new default proxy. It only decides whether each area would be a candidate default under the package decision rules.

## Implementation Structure

Add `src/mac/services/spotprice_model_diagnostics/p0056d.py` as a package-scoped runner.

The runner will:

1. Define immutable zone, location and weight catalogs for SE1, SE2 and FI.
2. Create P0056D-only SQLite tables in the feature DB:
   - `area_weather_zone_openmeteo_hourly_p0056d_v1`
   - `area_weather_proxy_hourly_p0056d_v1`
   - `area_weather_features_hourly_p0056d_v1`
   - `area_weather_proxy_weights_p0056d_v1`
   - `area_consumption_forecast_log_p0056d_v1`
   - `area_consumption_forecast_metrics_p0056d_v1`
3. Fetch Open-Meteo archive weather one location-period chunk at a time for `2022-06-01..2026-05-31`, the latest complete overlap currently used by P0056C/P0056B evidence.
4. Use quarterly chunks for resume after the rate-limit clarification; skip any chunk whose expected row count is already present.
5. Upsert location-hour observations and weight rows after every completed chunk.
6. Build zone hourly means and weighted area proxy/features rows.
7. Load P0056A targets, join with P0056D weather features, and reuse P0056C model helper functions for split, fitting and metric calculation.
8. Persist P0056D forecast logs/metrics for SE1, SE2 and FI only.
9. Compare metrics against P0056C baseline evidence and write required evidence files.

If Open-Meteo returns persistent `429`, the runner writes checkpoint/progress/resume evidence and returns a resumable WARN before proxy building/model retest.

## Deliberate Refactoring Decisions

- Do not modify `weather_history` core variable lists to add `snow_depth`; that would affect older packages. P0056D documents `snow_depth` unavailable from the existing helper.
- Do not alter P0056C defaults or tables. The retest gets versioned P0056D tables and evidence.
- Do not delete already fetched P0056D location rows on rerun. Only derived proxy/forecast/metrics tables are rebuilt.
- Reuse P0056C modeling functions to keep model method and split policy identical.

## Test Strategy

Add focused tests for:

- Zone weights sum to exactly 1.0 per area.
- Every zone has at least one representative location and every location belongs to a scoped area.
- Aggregation from location rows to area feature rows is deterministic.
- Decision-rule comparison against P0056C baseline.
- Forbidden feature contract excludes spot price, flow/exchange/A61/capacity and future actual load terms.

Final commands:

```bash
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056d
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d
python3 -B -m unittest tests.mac.services.spotprice_model_diagnostics.test_p0056a tests.mac.services.spotprice_model_diagnostics.test_p0056b tests.mac.services.spotprice_model_diagnostics.test_p0056c tests.mac.services.spotprice_model_diagnostics.test_p0056d
git diff --check
```

## Risks And Uncertainties

- Manual weights may be a weak proxy for actual load distribution.
- Open-Meteo availability can lag or rate-limit; missing chunks must be checkpointed and resumed.
- Retest may not improve all three areas. That is acceptable under WARN if evidence and default decisions are clear.
- Historical actual-weather proxies remain LABB-only because production would require a separate forecast-safe weather model.
