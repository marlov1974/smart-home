# P0016 Implementation Design

## Package Interpretation

P0016 creates a narrow proof that a measurement-owning Shelly device can publish compact telemetry to a planner/development Shelly without a central poller. The source device is `ftx-supply-uni`; the receiver is dampers. Runtime contracts must not use a `g2` namespace.

## G1 Poll/Master Inspiration Analysis

Copied/adapted from G1:

- Supply component IDs and value extraction from `rt/poll/feature-supply.js`.
- Numeric clipping/rounding style from `rt/poll/numbers.js` and common helpers.
- The idea of complete telemetry snapshots from `rt/poll/output.js`, reduced to only supply UNI fields.
- The 15 second cadence and busy-skip guard from `rt/master/base.js` and `rt/master/main.js`.
- The refresher concept is inspired by G1 master scheduling, but implemented only as a one-shot restart script.

Intentionally not copied:

- No central multi-device `poll`.
- No fan, extract, process, heat, cool, VVX or dampers polling.
- No `ftx.tel.*` contracts.
- No score dispatcher, reboot worker, production worker ids or G1 runtime host assumptions.
- No actuator/output reads beyond local status component parsing, and no actuator writes.

## Implementation Structure

New Shelly source:

- `src/shelly/supply_uni/manifest.json`
- `src/shelly/supply_uni/supply_uni_pub.js`
- `src/shelly/supply_uni/supply_uni_refresh.js`

Generated artifacts:

- `build/shelly/supply_uni/supply_uni_pub.js`
- `build/shelly/supply_uni/supply_uni_refresh.js`
- `dep/s/ch/supply_uni_pub/**`
- `dep/s/ch/supply_uni_refresh/**`
- `dep/s/rec/supply_uni_pub.json`
- `dep/s/rec/supply_uni_refresh.json`

Mac live-tool support:

- Extend `src/mac/tools/shelly_live/core.py` only enough to deploy/verify P0016 scripts and `tele.supply_uni`.
- Add tests in `tests/mac/tools/shelly_live/test_core.py`.

Documentation:

- Package evidence under `requirements/package-runs/P0016/**`.
- Cross-package function docs for Shelly supply UNI runtime and changed Mac live-tool behavior.

## Supply UNI Live Status/Component Discovery

Before live writes, read:

- supply UNI `Shelly.GetDeviceInfo`
- supply UNI `Shelly.GetStatus`
- dampers `Shelly.GetDeviceInfo`
- current script lists

The runtime parser expects these local status keys:

- `voltmeter:100`
- `input:2`
- `temperature:100`
- `temperature:101`
- `temperature:102`

Accepted numeric field aliases match the G1 helper style:

- Pressure: `xvoltage`, `value`, `pa`, `pressure`
- RPM: `xfreq`, `value`, `rpm`, `frequency`
- Temperature: `tC`, `tc`, `value`, `temp`

If live status lacks these values, stop before deploying scripts.

## Telemetry KVS Contract

Remote key on dampers:

```text
tele.supply_uni
```

Value shape:

```json
{"t":1234567890,"supply_pa":0,"outdoor":0,"post_vvx":0,"to_outdoor":0,"supply_rpm":0}
```

No source name, schema version, sequence, units, labels or nested status objects are included.

## Delta-Trigger Policy

`supply_uni_pub` keeps `lastSent` in RAM.

It publishes a full snapshot when:

- no previous successful snapshot exists
- `supply_pa` changes by at least 10 Pa
- `outdoor` changes by at least 1.0 C
- `post_vvx` changes by at least 1.0 C
- `to_outdoor` changes by at least 1.0 C
- `supply_rpm` changes by at least 100 RPM

If remote write fails, `lastSent` is not updated.

## Publisher Runtime Model

`supply_uni_pub`:

- logs `BOT`
- starts an immediate tick and a repeating 15 second timer
- skips overlapping ticks with a short `BUSY` log
- reads local `Shelly.GetStatus`
- parses and normalizes the five supply UNI values
- writes the full snapshot to dampers using remote JSON-RPC `KVS.Set`
- updates `lastSent` only after success
- logs compact parse/publish status

The script is long-lived. If P0016 succeeds it will be left running, because that is the proof state expected by the package.

## Refresher Runtime Model

`supply_uni_refresh`:

- finds `supply_uni_pub` by script name
- stops it if running
- waits briefly
- starts it
- logs `DONE`
- self-stops

P0016 does not implement Shelly-side hourly scheduling. It leaves `supply_uni_refresh` installed and stopped; hourly triggering is future production scheduling work.

## Remote KVS Write Model

The publisher sends JSON-RPC over HTTP to dampers:

```text
POST http://192.168.77.30/rpc
{"id":1,"method":"KVS.Set","params":{"key":"tele.supply_uni","value":<snapshot>}}
```

This is a remote KVS write only. It does not call switch, relay, cover, output, component or device-config methods.

## Live Verification Plan

1. Read supply UNI identity/status from `http://192.168.86.240:8020/`.
2. Read dampers identity/status from `http://192.168.86.240:8030/` and require physical id `8813bfd99f54`.
3. Verify supply status shape contains the required local component values.
4. Build and validate both scripts.
5. Deploy `supply_uni_pub` and `supply_uni_refresh` to supply UNI only.
6. Start `supply_uni_pub`, capture logs until publish success, and read back `tele.supply_uni` from dampers.
7. Start `supply_uni_refresh`, capture logs showing stop/start/self-stop, then confirm `supply_uni_pub` running and `supply_uni_refresh` stopped.
8. Record final script states and KVS readback.

## No-Central-Poll Boundary

No Mac or Shelly code will poll multiple FTX devices for P0016. Supply UNI reads only local status and publishes one compact snapshot to dampers.

## No-G2-Runtime-Name Boundary

Runtime scripts and KVS keys are:

- `supply_uni_pub`
- `supply_uni_refresh`
- `tele.supply_uni`

No new P0016 runtime name or contract uses `g2`.

## Test Strategy

Run:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/supply_uni/manifest.json --build-root build/shelly/supply_uni --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/supply_uni --dep-root dep/s --role supply_uni_pub
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/supply_uni --dep-root dep/s --role supply_uni_refresh
git diff --check
```

Live verification uses the P0016 command added to the Mac live tool and stores concise output under `requirements/package-runs/P0016/logs/`.

## Risks and Uncertainties

- Supply UNI physical id is not documented yet.
- Live `Shelly.GetStatus` may expose different field names than G1 expected; stop if values cannot be identified safely.
- Remote HTTP from supply UNI to dampers may fail because of Shelly HTTP/RPC behavior or network restrictions.
- Refresher cannot provide hourly scheduling by itself; this is documented as future scheduling work.
