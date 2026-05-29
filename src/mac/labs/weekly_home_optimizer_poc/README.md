# Weekly Home Optimizer POC

Package: `P0018`, updated by `P0020`, `P0021`, `P0022`, `P0023` and `P0024`

This Mac-only lab module builds a one-week plan for heat, PPM and RH-policy ventilation tradeoffs.

Heat production uses the P0022 discrete DP optimizer with 2..22 kW hourly heat modes and a virtual 300 kWh heat battery SOC. Output preserves the established heat fields and adds optimizer metadata plus optional DP diagnostics.

P0023 adds a deterministic COP emulator and compares optimized heat electric cost with flat production, where flat production means each hour produces that hour's heat need directly. The comparison is an emulated POC estimate, not measured savings.

P0024 adds an hourly spot plan. The internal forecast baseline still starts from the P0017 period-index model, but public optimizer output is always 168 hourly values. When 2025 actual spot fixture prices overlap the requested week, actual price shape is patched into the forecast while preserving the forecast sum over the overlap period.

Run from the repository root:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --people 6 --format json
```

Manual runs prefer Open-Meteo archive weather and fall back explicitly if real weather is unavailable. Offline deterministic fixture weather is available for tests and development:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22 --people 3 --fixture-weather
```

The module does not control Shelly, Home Assistant, heat pumps or FTX runtime behavior.

## Browser UI

Start the local browser UI on the Mac:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081
```

For phone testing on the same LAN, explicitly bind to all interfaces:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Then open:

```text
http://<mac-lan-ip>:8081/
```

Direct phone URL with stronger occupancy pressure:

```text
http://<mac-lan-ip>:8081/?week=2&ppm=500&houseTemp=22&people=6
```

The server is trusted-local read-only POC tooling. It runs the local planner and does not write to devices.

## Spot Fixture

P0024 reads:

```text
data/spot/spot_2025_hourly_europe_stockholm.csv
```

The fixture is keyed by `utc_hour_start` to avoid DST ambiguity. The POC public input is still week-only, so actual spot patching maps requested weeks to ISO year 2025.
