# P0015 Consistency Review

## Classification

PASS

## Result

P0015 is consistent with repository truth and can be implemented inside the stated package scope.

## Evidence

- G2 repository was synchronized with `origin/main` before reading package files.
- `requirements/packages/P0015-g2-weather-script-from-g1-template.md` exists after sync and is the active package.
- Existing G2 Shelly build tooling supports a weather manifest with one role and generated build/deploy artifacts.
- Existing G2 live tooling already supports bounded script create/update/start/stop/log/KVS verification for named test scripts and can be extended for the P0015 script/key boundary.
- `memory/device-management/mac-layer.md` supports Mac pre-live checks and runtime endpoint separation.
- `memory/infrastructure/devices.md` identifies dampers as:
  - role `ftx-dampers`
  - stable LAN `192.168.77.30`
  - operator NAT endpoint `http://192.168.86.240:8030/`
  - physical Shelly id `8813bfd99f54`
- P0014 left dampers as the controlled G2 lab device and did not make it production FTX control.

## G1 Template Check

G1 weather source was inspected read-only from `marlov1974/shelly`. The local G1 checkout is on branch `codex/setup-dev-machine`, so the critical weather template files were cross-checked against `origin/main` without checkout.

G1 `origin/main` template commit:

```text
0c3a445
```

Relevant G1 behavior:

- recipe order: wrapper, weather base/url/http/parse/fetch/output/main, wrapper end
- one-shot script
- Open-Meteo daily and hourly requests
- coordinates `59.6214405`, `17.7336153`
- solar proxy `round(shortwave_radiation_sum_MJ * 2.0)`
- JSON parsing of small Open-Meteo payloads
- KVS output `ftx.weather.act`
- self-stop after write

P0015 adapts this to G2 by changing script name, KVS key and adding daily humidity.

## Open-Meteo Schema Check

Read-only pre-design API checks on `2026-05-24` returned the required fields:

```text
daily.shortwave_radiation_sum[0] = 26.11
daily.temperature_2m_mean[0] = 18.4
daily.relative_humidity_2m_mean[0] = 62
hourly.temperature_2m[0] = 21.9
```

Payloads were compact enough for Shelly JSON parsing in this package shape:

```text
daily response: about 400 bytes
hourly response: about 280 bytes
```

## Safety / Scope

Allowed implementation scope:

- `src/shelly/weather/**`
- `build/shelly/weather/**`
- generated `dep/s/**` weather artifacts
- `src/mac/tools/**`
- `tests/mac/tools/**`
- `docs/functions/**`
- `memory/knowhow/**` if a durable lesson is discovered
- `requirements/package-runs/P0015/**`
- package completion notes

Forbidden areas remain out of scope:

- no G1 repository changes
- no G1/VVX runtime writes
- no `ftx.weather.act` writes
- no Home Assistant changes
- no actuator/output operations
- no production activation

## Notes

The package is live-device adjacent, but the live write boundary is specific and non-actuating. The quick package command authorizes commit/push after verified success under the current pre-production policy.
