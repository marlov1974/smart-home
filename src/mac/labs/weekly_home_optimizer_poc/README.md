# Weekly Home Optimizer POC

Package: `P0018`

This Mac-only lab module builds a deterministic one-week plan for heat, PPM and RH-policy ventilation tradeoffs.

Run from the repository root:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 500 --house-temp 22
python3 -m src.mac.labs.weekly_home_optimizer_poc --week 2 --ppm 700 --house-temp 22 --format json
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

The server is trusted-local read-only POC tooling. It runs the local planner and does not write to devices.
