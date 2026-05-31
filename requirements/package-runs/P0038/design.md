# P0038 design

## Interpretation

P0038 adds conservative observed-weather exogenous normalization diagnostics for solar/cloud/radiation (`M3C`) and wind (`M3D`) before residual M4.

## Weather proxy design

Wind uses the required P0038 production-area locations:

```text
south_wind_proxy = Malmo 0.55 + Kalmar 0.45
central_wind_proxy = Kristinehamn 1.00
north_wind_proxy = Pitea 0.35 + Ange 0.35 + Harnosand 0.30
```

Solar uses:

```text
south_solar_proxy = Malmo 0.55 + Kalmar 0.45
se3_load_solar_proxy = Orebro 0.55 + Borlange 0.45
north_solar_proxy = Umea 0.55 + Pitea 0.45
```

## Feature design

Solar proxy:

```text
shortwave_radiation * (1 - 0.35 * cloud_cover / 100)
```

Wind proxy:

```text
0 below 3 m/s, cubic ramp to rated, capped at 1 above 15 m/s
```

Both M3C and M3D use train-only day-of-year/hour normals and train-only anomaly buckets. Deltas are median residuals with sample-count shrinkage and caps.

## Model policy

M4_SE1 remains disabled. P0038 evaluates M4_area_diff-only after M3C/M3D and labels the result according to full-year holdout behavior.
