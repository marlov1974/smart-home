# Weather Feature Contract

- Input class: `historical_observed_only`
- Prediction kind: `weather_actual_proxy`
- Heating base: `17.0 C`
- Cooling base: `22.0 C`
- Rolling windows: `['temperature_2m_roll_mean_24h']`
- UTC/local handling: timestamps are UTC hour starts; no local-time or DST join is performed
- Spot price features: `False`
- Model training: `False`
- Production weather forecast claim: `False`
