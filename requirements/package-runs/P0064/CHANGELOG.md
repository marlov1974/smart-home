# P0064 Changelog

## Status

verified-live

## Behavior

The Home Assistant FTX dashboard now scales the `Total effekt` gauge against `450 W`.

For a value of `175 W`, the gauge ratio is now approximately:

```text
175 / 450 = 0.389
```

Changed:

- `src/ha/dashboards/ftx.yaml`
- `dep/ha/dashboards/ftx.yaml`
- `tests/mac/ha/test_ftx_dashboard.py`
- P0064 package definition and evidence

## Verification

```text
python3 -m unittest tests.mac.ha.test_ftx_dashboard
python3 -m unittest discover tests/mac
git diff --check
```

Live readback:

```json
{"entity":"sensor.ftx_total_effekt_2","max":450,"min":0,"name":"Total effekt","severity":{"green":0,"red":400,"yellow":300},"type":"gauge"}
```

## Live Actions

Performed:

- replaced `/mnt/data/supervisor/homeassistant/dashboards/ftx.yaml` in the local HAOS VM with `dep/ha/dashboards/ftx.yaml`
- read back Lovelace config through Home Assistant WebSocket API

Not performed:

- no Shelly writes
- no Home Assistant restart
- no other dashboard edits

## Final Live State

```text
FTX dashboard Total effekt gauge max = 450
```

## Uncertainty

Mobile clients may need a dashboard refresh/reopen to pick up the YAML change if they have cached the old card config.

## Knowhow Promotion

Skipped. The package did not add a new reusable operational lesson beyond existing package evidence.
