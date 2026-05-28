# Weekly Home Optimizer POC

Package: `P0018`

This Mac-only lab module builds a deterministic one-week plan for heat, PPM and RH-policy ventilation tradeoffs.

Run from the repository root:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --format json
```

The module does not control Shelly, Home Assistant, heat pumps or FTX runtime behavior.
