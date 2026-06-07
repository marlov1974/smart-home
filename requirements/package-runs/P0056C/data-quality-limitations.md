# P0056C Data Quality Limitations

- P0056B weather actual-proxy coverage ends at `2026-05-31T21:00Z`; later P0056A consumption-only rows are not modeled.
- P0056B fallback weather areas: `DE_LU, DK1, EE, LT, LV, NL, PL`.
- Weather rows are actual-weather LABB proxies, not production weather forecasts.
- `snow_depth` is unavailable from P0056B and represented as a zero-filled nullable source feature for model matrix safety.
