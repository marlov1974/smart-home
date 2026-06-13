# P0064 Review

## Classification

WARN

## Evidence

- Home Assistant API is reachable on `http://127.0.0.1:8123`.
- HA version is `2026.6.3`.
- FTX dashboard is YAML-mode:
  - `url_path: ftx-dashboard`
  - `filename: dashboards/ftx.yaml`
- Live file path is `/mnt/data/supervisor/homeassistant/dashboards/ftx.yaml`.
- Current `Total effekt` gauge config has `max: 5000`.

## Consistency Result

The operator says FTX max power is `450 W`. Updating the gauge max to `450` is consistent with the desired visualization and does not change runtime control.

The package is `WARN` because it writes live Home Assistant dashboard YAML through the HAOS VM guest agent. The write is narrow and readback-verifiable.
