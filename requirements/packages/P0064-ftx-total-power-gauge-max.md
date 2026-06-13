# P0064 FTX total power gauge max

## Goal

Set the Home Assistant FTX dashboard `Total effekt` gauge maximum to `450 W` so a live value around `175 W` renders at about 40% instead of about 10%.

## Background

The live Home Assistant FTX dashboard is YAML-mode:

```text
url_path: ftx-dashboard
filename: dashboards/ftx.yaml
HAOS path: /mnt/data/supervisor/homeassistant/dashboards/ftx.yaml
```

The current gauge uses:

```yaml
max: 5000
```

This is inconsistent with the operator-provided physical maximum for the FTX unit:

```text
450 W
```

## Scope

Allowed repository changes:

- `src/ha/dashboards/ftx.yaml`
- `dep/ha/dashboards/ftx.yaml`
- `tests/mac/ha/**`
- package-run evidence under `requirements/package-runs/P0064/**`

Allowed live action:

- replace `/mnt/data/supervisor/homeassistant/dashboards/ftx.yaml` in the local HAOS VM with the package `dep/ha/dashboards/ftx.yaml`
- read back Lovelace config through Home Assistant API

Forbidden:

- no Shelly writes
- no G1 changes
- no Home Assistant entity/integration changes
- no changes to other dashboards
- no HA restart unless readback proves it is required

## Required Verification

- Test that `src/ha/dashboards/ftx.yaml` and `dep/ha/dashboards/ftx.yaml` match.
- Test that the `Total effekt` gauge has `max: 450`.
- Live readback through HA WebSocket must show the `Total effekt` card with `max: 450`.
- Run `git diff --check`.

## Commit/Push Authorization

If verification passes and the diff is inside package scope, this package authorizes commit and push.
