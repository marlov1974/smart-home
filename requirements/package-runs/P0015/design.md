# P0015 Implementation Design

## Package Interpretation

P0015 creates the first G2 weather Shelly runtime script, `weather_v0_9_0`, adapted from the G1 weather template. It will be deployed only to dampers as a pre-production G2 development runtime.

The runtime is one-shot:

1. build daily and hourly Open-Meteo URLs
2. fetch daily weather
3. fetch near-current hourly temperature
4. parse compact JSON payloads
5. write `g2.weather.act`
6. log concise evidence
7. stop itself

Mac remains deployer/verifier. The installed Shelly script must be autonomous when started.

## G1 Weather Template Analysis

G1 files inspected from `marlov1974/shelly`, with critical files cross-checked against `origin/main` commit `0c3a445`:

- `memory/ftx-digitalt/09-weather-model.md`
- `rt/recipes/weather.json`
- `rt/weather/base.js`
- `rt/weather/url.js`
- `rt/weather/http.js`
- `rt/weather/parse.js`
- `rt/weather/fetch.js`
- `rt/weather/output.js`
- `rt/weather/main.js`
- `rt/brain/io-weather.js`

Copied/adapted:

- house coordinates
- Open-Meteo forecast API
- two-request daily/hourly model
- solar proxy factor `2.0`
- daily mean temperature
- near-current hourly temperature
- one-shot fetch/write/self-stop flow
- fallback-to-zero on HTTP/parse failure

Changed for G2:

- script name becomes `weather_v0_9_0`
- KVS key becomes `g2.weather.act`
- output includes `humidity_avg_today`
- runtime is standalone G2 source instead of G1 chunk recipe/common wrappers
- logs include response lengths and compact completion markers

Intentionally not copied:

- G1 `ftx.weather.act`
- G1 brain reader behavior
- G1 production cadence/scheduling
- any G1 runtime host deployment

## G2 Weather KVS Contract

Key:

```text
g2.weather.act
```

Value object:

```json
{
  "solar_kwh_today": 52,
  "temp_now": 21.9,
  "temp_avg_today": 18.4,
  "humidity_avg_today": 62
}
```

Rounding/clipping:

- `solar_kwh_today`: integer `0..999`
- `temp_now`: one decimal `-99.9..99.9`
- `temp_avg_today`: one decimal `-99.9..99.9`
- `humidity_avg_today`: one decimal `0..100`

The source and tools must not contain `ftx.weather.act`.

## Open-Meteo API/Schema Pre-Live Test

Add a Mac standard-library tool:

```text
src/mac/tools/weather_contract/
```

CLI:

```bash
python3 -m src.mac.tools.weather_contract check-openmeteo
```

The tool fetches:

- daily `shortwave_radiation_sum,temperature_2m_mean,relative_humidity_2m_mean` for today
- hourly `temperature_2m` with `forecast_hours=1`

It validates required arrays and emits JSON evidence with response lengths and parsed output. Tests use fake responses and fixtures; the live command validates current external API behavior before Shelly deploy.

## Memory and Runtime-Health Strategy

The Shelly script uses `JSON.parse` because the Mac pre-live check and direct curl checks show the P0015 payloads are compact. The script logs daily/hourly response lengths, avoids storing diagnostic copies, writes one compact KVS object and self-stops.

Live logs must be checked for:

- `out_of_memory`
- missing `KVS OK`
- missing `DONE`
- repeated stuck states

## Dampers Live Target and Identity Verification

Target:

```text
runtime endpoint: http://192.168.86.240:8030/
stable LAN: 192.168.77.30
physical id: 8813bfd99f54
```

Before live writes, the live tool will read `Shelly.GetDeviceInfo` and require the live id to match `8813bfd99f54`.

## Mac Direct-Deploy Source Model

Build output:

```text
build/shelly/weather/weather_v0_9_0.js
```

Mac direct deploy reads that complete built script and splits it into temporary in-memory RPC chunks. It does not read `dep/s/ch/**`.

## Live Verification Plan

Commands:

```bash
python3 -m src.mac.tools.weather_contract check-openmeteo
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/weather/manifest.json --build-root build/shelly/weather --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/weather --dep-root dep/s --role weather_v0_9_0
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_live deploy-weather --base-url http://192.168.86.240:8030 --script build/shelly/weather/weather_v0_9_0.js --expect "weather_v0_9_0 DONE"
git diff --check
```

The live command must report:

- target id verification
- upload chunk bytes/count
- before/after script status
- log excerpt
- parsed `g2.weather.act`
- no memory pressure indicators

## No-Production-Activation Boundary

P0015 installs and tests a stopped script plus local KVS on dampers only. It does not schedule weather, deploy a G2 brain, migrate G1/VVX, touch Home Assistant, or activate production control.

## Intended Changes

Create/update:

- `src/shelly/weather/manifest.json`
- `src/shelly/weather/weather.js`
- `build/shelly/weather/weather_v0_9_0.js`
- generated `dep/s/ch/weather_v0_9_0/**`
- generated `dep/s/rec/weather_v0_9_0.json`
- `src/mac/tools/weather_contract/**`
- `tests/mac/tools/weather_contract/**`
- P0015 support in `src/mac/tools/shelly_live/core.py`
- P0015 tests in `tests/mac/tools/shelly_live/test_core.py`
- function docs for weather contract/live/weather runtime if useful
- `requirements/package-runs/P0015/**`
- P0015 completion notes

No G1 files will be changed.

## Risks and Uncertainties

- Shelly firmware may parse JSON differently or hit heap pressure despite compact payloads; live logs are the gate.
- Open-Meteo may transiently fail; if the Mac pre-live check fails because schema is absent, stop.
- `relative_humidity_2m_mean` is available in current API checks; if live endpoint changes, stop before deploy.
