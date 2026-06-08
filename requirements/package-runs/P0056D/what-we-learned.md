# P0056D What We Learned

- SE1, SE2 and FI can be retested with explicit zone-weighted Open-Meteo proxies without changing P0056B defaults.
- Manual zone weights are useful for first-pass LABB exploration but should be replaced by population/load metadata before candidate evaluation.
- `snow_depth` is not requested by the existing weather-history Open-Meteo helper; P0056D labels it unavailable rather than expanding older package contracts.
- Historical actual-weather proxy results remain diagnostic only and require a separate forecast-safe weather model before production use.
