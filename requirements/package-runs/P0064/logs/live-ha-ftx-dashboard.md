# P0064 Live HA FTX Dashboard

Target:

```text
Home Assistant API: http://127.0.0.1:8123
HA version: 2026.6.3
Dashboard: ftx-dashboard
YAML file: /mnt/data/supervisor/homeassistant/dashboards/ftx.yaml
```

Precheck:

```text
Total effekt gauge max: 5000
```

Live write:

```text
Wrote dep/ha/dashboards/ftx.yaml to /mnt/data/supervisor/homeassistant/dashboards/ftx.yaml via QEMU guest agent.
bytes_written: 1472
readback_matches_dep: true
```

HA WebSocket readback:

```json
{"entity":"sensor.ftx_total_effekt_2","max":450,"min":0,"name":"Total effekt","severity":{"green":0,"red":400,"yellow":300},"type":"gauge"}
```

Rendered ratio check:

```text
175 / 450 = 0.389
```

No HA restart was required.
