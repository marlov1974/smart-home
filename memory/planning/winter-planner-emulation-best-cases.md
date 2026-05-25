# Winter planner emulation best cases

This file stores manually accepted planner calibration cases from discussion.

## Best so far for constant -5 C week, LOW comfort

Scenario:

```text
Start: Monday 06:00
Start house temperature: 22.0 C
Start house charge: 100%
Target/setpoint: 20.0 C
Comfort band: LOW, +/-2 C
House battery: 400 kWh
Outdoor temperature: -5 C all week
Solar: 0
Heat model: 12.5 * (target_temp - outdoor_temp) - 42
Daily heat need: 270.5 kWh/day
8h period heat loss: 90.2 kWh
Total production to next Monday 06: 1893.5 kWh
```

Accepted calibration:

```text
Mån- Tor:
  mass_weight = 1.5
  price_exponent = 2.0

Fre 06:00-22:00:
  mass_weight = 1.0
  price_exponent = 2.0

Fre 22:00 -> Mån 06:00:
  mass_weight = 1.7
  price_exponent = 0.8
```

Result:

```text
Mån 06 -> Fre 22 production: 893.4 kWh
Fre 22 -> Mån 06 production: 1000.1 kWh
Energy shifted to weekend vs previous form model: about +248 kWh
Minimum simulated house temperature: about 18.31 C
Maximum period production: Lör 22:00-06:00 = 173.8 kWh / 8h = 21.7 kW
End state Monday 06:00: 22.0 C / 100% charge
```

Interpretation:

```text
This calibration is the current best LOW-comfort shape for a -5 C constant winter week.
It keeps weekend production below about 22 kW, allows meaningful weekday discharge, and reaches Monday 06 full charge without hard constraints.
```
