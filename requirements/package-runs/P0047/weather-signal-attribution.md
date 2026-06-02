# P0047 weather signal attribution

Available AI2 v2 weather fields are system-level temperature, solar and wind proxies. South/north/central gradient columns are unavailable in this source table and are listed as missing.

missing_requested_columns = ['temperature_se3_or_south_actual', 'temperature_south_minus_north', 'solar_se3_or_south_actual', 'solar_south_minus_north', 'wind_south_proxy', 'wind_central_proxy', 'wind_north_proxy', 'wind_south_minus_north', 'wind_central_minus_north']

## Pearson Correlation To Spread

- temperature_se1_or_system_actual: -0.191649
- solar_se1_or_system_actual: -0.203907
- wind_system_proxy: -0.076373
- se1_price: -0.092977
- se3_price: 0.755313
- abs_se3_minus_se1: 0.998242

## Means By Regime

{
  "abs_se3_minus_se1": {
    "spread_near_zero": 0.01242771901709401,
    "spread_negative": 0.23121600000000003,
    "spread_positive": 0.3954568099144083,
    "spread_small_nonzero": 0.1255322232404691,
    "spread_spike_positive": 1.2328491834319537
  },
  "se1_price": {
    "spread_near_zero": 0.252563841880342,
    "spread_negative": 1.001634,
    "spread_positive": 0.12536498751783168,
    "spread_small_nonzero": 0.257058284457478,
    "spread_spike_positive": 0.17297620710059164
  },
  "se3_price": {
    "spread_near_zero": 0.2551712745726491,
    "spread_negative": 0.770418,
    "spread_positive": 0.5208217974322401,
    "spread_small_nonzero": 0.3738257423020531,
    "spread_spike_positive": 1.4058253905325442
  },
  "solar_se1_or_system_actual": {
    "spread_near_zero": 157.10174340833336,
    "spread_negative": 141.9454252,
    "spread_positive": 66.31449079914105,
    "spread_small_nonzero": 99.06684545862339,
    "spread_spike_positive": 49.47435650377217
  },
  "temperature_se1_or_system_actual": {
    "spread_near_zero": 6.76076431623931,
    "spread_negative": 11.9483,
    "spread_positive": 5.2249247384688475,
    "spread_small_nonzero": 5.544507184750735,
    "spread_spike_positive": 1.061634319526625
  },
  "wind_system_proxy": {
    "spread_near_zero": 0.9051585392234218,
    "spread_negative": 0.91775275577908,
    "spread_positive": 0.8810667038647155,
    "spread_small_nonzero": 0.8941129311432322,
    "spread_spike_positive": 0.8571534737489985
  }
}
