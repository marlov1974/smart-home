# P0056D Open-Meteo Resume Instructions

Resume command:

```bash
python3 -B -m src.mac.services.spotprice_model_diagnostics.p0056d
```

The runner skips chunks whose expected row count is already present in `area_weather_zone_openmeteo_hourly_p0056d_v1` and fetches only missing location-period chunks.

Current blocking location: ``
Current blocking period: `..`
Last error: ``
