# P0064 Attempts

## Attempt 1

Status: passed.

Implementation:

- imported the live FTX dashboard YAML into `src/ha/dashboards/ftx.yaml`
- created matching deploy artifact `dep/ha/dashboards/ftx.yaml`
- changed `Total effekt` gauge from `max: 5000` to `max: 450`
- adjusted severity thresholds to `green: 0`, `yellow: 300`, `red: 400`
- added `tests/mac/ha/test_ftx_dashboard.py`

Live write:

- wrote `dep/ha/dashboards/ftx.yaml` to `/mnt/data/supervisor/homeassistant/dashboards/ftx.yaml`
- guest-agent readback matched deploy artifact byte-for-byte

Live verification:

- HA WebSocket `lovelace/config` for `ftx-dashboard` returned `Total effekt` gauge `max: 450`
- 175 W ratio against max is `0.389`
