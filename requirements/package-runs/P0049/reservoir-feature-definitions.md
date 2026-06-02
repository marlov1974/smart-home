# P0049 reservoir feature definitions

{
  "base_pressure": "z(wind_south_minus_north) + z(temp_south_minus_north) - z(solar_south_minus_north) + 0.25*evening_peak + 0.20*morning_peak + 0.30*se1_price_p90 - 0.20*south_wind_proxy",
  "learned_pressure_score": "train-only standardized linear proxy: 0.45*lag1_spread + 0.25*wind_gradient + 0.20*price_delta + 0.10*peak"
}

Reservoir EMA half-lives tested: 6h, 12h, 24h, 48h, 72h and 168h.
