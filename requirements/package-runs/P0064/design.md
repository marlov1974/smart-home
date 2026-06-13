# P0064 Implementation Design

## Package Interpretation

Fix the FTX Home Assistant dashboard scale for the `Total effekt` gauge. The card should show 175 W as roughly `175 / 450 = 39%`.

## Implementation Structure

- Add G2-owned source YAML under `src/ha/dashboards/ftx.yaml`.
- Add matching deploy YAML under `dep/ha/dashboards/ftx.yaml`.
- Change only the `Total effekt` gauge maximum and matching severity thresholds.
- Add a small standard-library unit test that verifies the deploy artifact matches source and that the gauge block has the expected max.

## Intended Changes

`Total effekt` gauge:

```yaml
min: 0
max: 450
severity:
  green: 0
  yellow: 300
  red: 400
```

## Live Plan

Use QEMU guest agent to replace only:

```text
/mnt/data/supervisor/homeassistant/dashboards/ftx.yaml
```

Then verify via HA WebSocket `lovelace/config` for `url_path: ftx-dashboard`.

## Risks

- HA YAML dashboards may cache content. If WebSocket readback does not update after file write, a later package or explicit operator approval may reload/restart HA. P0064 does not plan a restart unless needed.
- G2 had no prior `src/ha`/`dep/ha` dashboard source; this package creates the initial source/deploy copy from the live dashboard.
