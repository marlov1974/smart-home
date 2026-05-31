# P0033 climate weight selection

## SE1 system climate weights

P0033 uses the package-required Level 2 SE1 signal weights:

```text
0.70 * se1_core_weather
0.25 * nordic_connected_weather
0.05 * south_connected_weather
```

The weights are applied independently to:

- `weighted_temperature_2m`
- `weighted_apparent_temperature`
- `heating_degree_hours`
- `cooling_degree_hours`

Rationale: SE1 should be dominated by northern Sweden and connected northern-area conditions while retaining a small southern connected component for broader market climate pressure.

## Area-diff climate signals

P0033 keeps P0032 gradients separate instead of collapsing them to one scalar:

- `se3_load_temperature`
- `temp_gradient_se3_load_minus_se1_core`
- `apparent_temp_gradient_se3_load_minus_se1_core`
- `heating_degree_gradient_se3_load_minus_se1_core`
- `south_temp_gradient_minus_se1_core`

Rationale: the area-diff target is a spread target, so gradients are useful diagnostics and preserve the P0032 SE1 plus SE3-area-diff decomposition. `se3_load_temperature` is the primary M3 anomaly signal so the area-diff target also exposes a price-delta function of deviating temperature.

## Deferred signals

Wind is not used by M3 in P0033. Cloud, radiation, precipitation, snowfall and forecast weather are also deferred.
