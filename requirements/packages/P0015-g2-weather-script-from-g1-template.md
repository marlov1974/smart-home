# Package P0015: G2 weather script from G1 template

## Status
verified

## Package order
P0015

## Primary area
G2 / Shelly runtime / Mac tooling / weather runtime

## Decision summary

P0015 creates the first G2 weather runtime script using the G1 weather script as the implementation template.

The target script is:

```text
weather_v0_9_0
```

The script will run on the dampers Shelly as a G2 development runtime before G2 production activation.

Dampers is an allowed G2 development device because it has a low central control role before production. Later, dampers may also be part of production precisely because it does little and is suitable for controlled staged testing.

P0015 creates a production-shaped but not production-active G2 weather KVS contract:

```text
g2.weather.act
```

This KVS may be written on dampers. P0015 must not write the G1/VVX production weather KVS on the current G1 runtime host.

## Solution model

G2 weather will be a Shelly one-shot script that:

1. builds Open-Meteo URLs for the house coordinates
2. fetches daily weather data
3. fetches near-current hourly temperature
4. parses a compact weather result
5. writes `g2.weather.act` on the local Shelly device
6. logs concise evidence
7. self-stops

Mac tooling must first test the Open-Meteo API/schema before Shelly live deploy. This is the first concrete use of the future production idea that Codex/Mac should test external APIs before pushing runtime errors onto Shelly devices.

Mac remains the deployer/verifier. After deployment, the Shelly weather script must be autonomous: it must not need Mac or Home Assistant to perform its own weather fetch when started.

## Current behavior

G1 weather lives in `marlov1974/shelly` and writes weather data for the current G1 FTX runtime.

G1 weather:

- uses Open-Meteo
- runs as a one-shot worker
- writes `ftx.weather.act`
- writes solar proxy and temperature data
- self-stops

There is no G2 weather runtime script yet in `marlov1974/smart-home`.

There is no G2 brain yet. When a G2 brain exists, it will initially be test/runtime-development, not production. It may later read `g2.weather.act`, but P0015 does not implement or activate that brain behavior.

## G1 template source

Codex must inspect the G1 source of truth before design/implementation:

```text
marlov1974/shelly/memory/ftx-digitalt/09-weather-model.md
marlov1974/shelly/rt/recipes/weather.json
marlov1974/shelly/rt/weather/base.js
marlov1974/shelly/rt/weather/url.js
marlov1974/shelly/rt/weather/http.js
marlov1974/shelly/rt/weather/parse.js
marlov1974/shelly/rt/weather/fetch.js
marlov1974/shelly/rt/weather/output.js
marlov1974/shelly/rt/weather/main.js
marlov1974/shelly/rt/brain/io-weather.js
```

Codex must document in `requirements/package-runs/P0015/design.md` which G1 behavior is copied, adapted or intentionally not copied.

## Target G2 source and artifacts

Expected source location:

```text
src/shelly/weather/
```

Expected manifest:

```text
src/shelly/weather/manifest.json
```

Expected built script:

```text
build/shelly/weather/weather_v0_9_0.js
```

The existing Shelly build tool should generate the built script and optional repo deploy chunks/recipe.

Mac direct deploy must read the complete built script from `build/shelly/weather/weather_v0_9_0.js` and split it into temporary in-memory RPC upload chunks. It must not use `dep/s/ch/**` as the Mac direct-deploy source.

## Weather coordinates

Use the same house coordinates as G1 unless Codex finds a durable G2 memory value that supersedes them:

```text
LAT = 59.6214405
LON = 17.7336153
```

## Open-Meteo API model

Use Open-Meteo forecast API:

```text
https://api.open-meteo.com/v1/forecast
```

Daily data must include:

```text
shortwave_radiation_sum
temperature_2m_mean
relative_humidity_2m_mean
```

Hourly data must include:

```text
temperature_2m
```

P0015 should keep the G1 two-request model unless Codex documents a package-scoped reason to simplify or change it:

```text
daily request:
  daily=shortwave_radiation_sum,temperature_2m_mean,relative_humidity_2m_mean
  start_date=<today>
  end_date=<today>
  timezone=auto

hourly request:
  hourly=temperature_2m
  forecast_hours=1
  timezone=auto
```

## G2 weather KVS contract

P0015 must write this local G2 KVS key on the target development device:

```text
g2.weather.act
```

Expected value shape:

```json
{
  "solar_kwh_today": 0,
  "temp_now": 0,
  "temp_avg_today": 0,
  "humidity_avg_today": 0
}
```

Field meanings:

```text
solar_kwh_today      project-specific solar-gain proxy for today
temp_now             near-current outdoor temperature in Celsius
temp_avg_today       daily mean outdoor temperature in Celsius
humidity_avg_today   daily mean relative humidity in percent
```

Suggested clipping/rounding:

```text
solar_kwh_today      integer, 0..999
temp_now             one decimal, -99.9..99.9
temp_avg_today       one decimal, -99.9..99.9
humidity_avg_today   integer or one decimal, 0..100
```

P0015 must not write:

```text
ftx.weather.act
```

P0015 must not write any weather KVS on:

```text
ftx-vvx / 192.168.77.40 / current G1 runtime host
```

## Solar model

Use the G1 solar proxy model unless Codex documents a package-scoped reason to change it:

```text
solar_kwh_today = round(shortwave_radiation_sum_MJ * 2.0)
```

This remains a control heuristic / house solar-gain proxy, not a physical kWh measurement.

## Memory and runtime-health strategy

P0015 must apply the P0012/P0013 Shelly HTTP/JSON lessons:

- keep upstream payloads small
- log response lengths
- avoid large diagnostic strings
- avoid retaining response bodies longer than needed
- write compact KVS values only
- verify logs for `out_of_memory`, stuck states and missing final KVS output

G1 uses `JSON.parse`. P0015 may use `JSON.parse` only if Mac API test and live evidence show the Open-Meteo payloads are small enough on the target device.

If response payloads are unexpectedly large or live logs show memory pressure, Codex must stop or redesign inside package scope before making the runtime current truth.

## Target live device

Primary live target:

```text
infrastructure role: ftx-dampers
physical Shelly id: 8813bfd99f54
stable LAN address: 192.168.77.30
operator NAT URL: http://192.168.86.240:8030/
```

Dampers is allowed for G2 development runtime tests before production activation.

Codex must still verify live identity/status before writes and must not rely on runtime endpoint alone.

## Allowed live actions

On dampers only, P0015 may:

- read device status/config
- read script list/status
- create/update/start/stop only `weather_v0_9_0`
- upload `weather_v0_9_0` using bounded in-memory RPC upload chunks
- read or stream debug log with timeout
- read only documented G2 weather KVS keys
- allow `weather_v0_9_0` to perform HTTP GET to Open-Meteo
- allow `weather_v0_9_0` to write only `g2.weather.act`

## Forbidden live actions

P0015 must not:

- deploy or write anything to `ftx-vvx` / `192.168.77.40`
- write `ftx.weather.act`
- change device settings/config
- call switch/relay/output/cover/actuator operations
- affect damper physical state
- change Home Assistant
- change G1 repository
- implement or deploy a G2 brain
- implement G2 production activation
- schedule weather as production runtime
- migrate G1 runtime ownership

## Non-goals

- No G2 brain implementation.
- No G2 driver implementation.
- No FTX production integration.
- No Home Assistant integration.
- No production scheduling.
- No dampers actuator control.
- No external Python dependencies.
- No rollback/version switching implementation.

## Invariants

- Python standard library only for Mac tooling.
- Shelly runtime must be autonomous after deployment.
- Mac direct deploy reads the complete built script, not `dep/s/ch/**`.
- Live actions must remain non-actuating.
- G1/VVX production KVS must not be touched.
- Package-run evidence is required.
- Knowhow promotion must be considered in final output.
- Pre-production G2 commit/push policy applies after successful verification.

## Knowledge updates

Update if needed:

- `docs/functions/mac/shelly-live-deploy-tool.md`
- `docs/functions/mac/shelly-build-tool.md`
- `docs/functions/mac/weather-contract-tool.md` if a new Mac API contract tool is created
- `docs/functions/shelly/weather.md` if a durable Shelly weather function catalog is created
- `memory/knowhow/shelly.md` if new Shelly HTTP/runtime lessons are learned
- `memory/device-management/mac-layer.md` if Mac API pre-live testing needs a durable rule update

## Files to inspect

G2:

- `AGENTS.md`
- `memory/bootstrap-manifest.json`
- `memory/04-codex-workflow.md`
- `memory/05-package-lifecycle.md`
- `memory/device-management/source-build-deploy-layers.md`
- `memory/device-management/mac-layer.md`
- `memory/infrastructure/devices.md`
- `memory/knowhow/shelly.md`
- `src/mac/tools/shelly_build/**`
- `src/mac/tools/shelly_live/**`
- `tests/mac/tools/**`
- `src/shelly/spotprice/**` as recent Shelly HTTP/runtime reference

G1 template:

- `marlov1974/shelly/memory/ftx-digitalt/09-weather-model.md`
- `marlov1974/shelly/rt/recipes/weather.json`
- `marlov1974/shelly/rt/weather/**`
- `marlov1974/shelly/rt/brain/io-weather.js`

## Files allowed to change

- `src/shelly/weather/**`
- `build/shelly/weather/**`
- `dep/s/**` only for generated weather artifacts if the build tool generates them
- `src/mac/tools/**` for weather API contract test and live deploy support
- `tests/mac/tools/**`
- `docs/functions/**`
- `memory/knowhow/**`
- `memory/device-management/**` only if durable Mac/pre-live deploy rules need refinement
- `requirements/package-runs/P0015/**`
- `requirements/packages/P0015-g2-weather-script-from-g1-template.md`

## Forbidden changes

- no G1 repository changes
- no G1 runtime host changes
- no `ftx-vvx` live writes
- no Home Assistant changes
- no actuator/output control code
- no G2 brain/driver implementation
- no production activation
- no external Python package dependencies
- no broad refactor outside weather/Mac deploy tooling needed for P0015
- do not rewrite previous package-run evidence

## Codex phase requirements

Codex must create these before implementation:

```text
requirements/package-runs/P0015/review.md
requirements/package-runs/P0015/design.md
requirements/package-runs/P0015/functions.md
```

Use the P0007 phase-gate model.

The design must include sections:

```text
G1 weather template analysis
G2 weather KVS contract
Open-Meteo API/schema pre-live test
Memory and runtime-health strategy
Dampers live target and identity verification
Mac direct-deploy source model
Live verification plan
No-production-activation boundary
```

## Live test/debug policy

Live testing allowed: yes, dampers only.

Live write actions allowed: yes, but only for:

- creating/updating/starting/stopping `weather_v0_9_0`
- uploading code to `weather_v0_9_0`
- `weather_v0_9_0` writing `g2.weather.act`

Shelly log capture required: yes.

KVS read verification required: yes.

Mac Open-Meteo API/schema pre-live test required: yes.

Max implementation/debug attempts: 3.

Codex must stop immediately if:

- it cannot verify dampers physical Shelly id `8813bfd99f54`
- the Open-Meteo schema does not include required fields
- a required live command exceeds the allowed action list
- the adapted weather script contains actuator/output/relay/switch/cover/device-config behavior
- live evidence shows memory pressure that cannot be fixed within package scope

## Test cases

### TC1: G1 template is identified
Given the G1 weather files
When Codex writes `design.md`
Then it documents G1 source files, recipe order, KVS contract and intentional G2 adaptations.

### TC2: Mac Open-Meteo API contract test
Given current Open-Meteo endpoint behavior
When Mac API pre-live test runs
Then daily/hourly schemas contain expected fields and response lengths are recorded:

```text
daily.shortwave_radiation_sum[0]
daily.temperature_2m_mean[0]
daily.relative_humidity_2m_mean[0]
hourly.temperature_2m[0]
```

### TC3: Build weather_v0_9_0
Given `src/shelly/weather/manifest.json`
When the Shelly build tool runs
Then `build/shelly/weather/weather_v0_9_0.js` is generated.

### TC4: Weather parser unit tests
Given fixture daily/hourly Open-Meteo JSON
When parser/tooling tests run
Then output contains `solar_kwh_today`, `temp_now`, `temp_avg_today` and `humidity_avg_today` with expected clipping/rounding.

### TC5: G2 weather KVS contract
Given `weather_v0_9_0` succeeds
When it writes KVS
Then `g2.weather.act` contains parseable compact weather data including `humidity_avg_today`.

### TC6: Live dampers deploy/log/KVS
Given `weather_v0_9_0` is built
When the tool deploys and starts it on dampers
Then log evidence shows Open-Meteo fetch, parse, `g2.weather.act` write and self-stop.

### TC7: No forbidden operations
Given the P0015 live boundary
When reviewing tool code, package-run evidence and log evidence
Then there are no device setting changes and no actuator/output/relay/cover/switch/component/network/MQTT/Bluetooth/cloud operations.

### TC8: G1 production KVS untouched
Given P0015 runs on dampers
When reviewing code and evidence
Then no writes to `ftx.weather.act` or `ftx-vvx` occur.

### TC9: Runtime health
Given live weather test completes
When reviewing bounded logs
Then no `out_of_memory`, repeated stuck state or missing KVS output is observed.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/weather/manifest.json --build-root build/shelly/weather --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/weather --dep-root dep/s --role weather_v0_9_0
git diff --check
```

Codex must also run a Mac Open-Meteo API/schema pre-live command defined by the package implementation, for example:

```bash
python3 -m src.mac.tools.weather_contract check-openmeteo
```

For live dampers test, Codex must document the exact command it ran, target endpoint, physical Shelly id verification, upload chunk size/count, log timeout, KVS key read, KVS values or safe summary, final script status and whether memory pressure occurred.

## Runtime health checks

During live test, check and record:

- target endpoint used
- physical Shelly id verification
- daily URL shape
- hourly URL shape
- daily response length
- hourly response length
- parsed `solar_kwh_today`
- parsed `temp_now`
- parsed `temp_avg_today`
- parsed `humidity_avg_today`
- upload chunk size and count
- script list/status after deploy
- start/stop result
- bounded log excerpt
- KVS read result for `g2.weather.act`
- memory-related log lines if present
- absence of forbidden RPC calls in package/tool/log evidence

## Deployment plan

No production deployment.

Controlled pre-production live test on dampers only.

Final acceptable live state after successful P0015:

```text
weather_v0_9_0 installed and stopped on dampers
g2.weather.act present on dampers with latest parsed weather values
no damper actuator/output state changed by P0015
```

## Rollback plan

If live verification fails after allowed attempts, follow failed-package cleanup:

- preserve package-run evidence
- update package status to stopped/failed-live if appropriate
- revert unverified current-state implementation changes unless evidence-only commit is intended
- leave or remove only `weather_v0_9_0` according to design/evidence
- do not touch unrelated scripts or KVS

If an incorrect KVS key was written, Codex may only remove it if the package design explicitly allowed that cleanup and the key is unambiguously owned by P0015.

## Expected Codex output

- PASS/WARN/STOP review
- design path
- functions path
- G1 weather template analysis summary
- G2 weather KVS contract
- Open-Meteo API pre-live test result
- files changed
- tests run
- live command and target endpoint
- physical Shelly id verification
- upload chunk size and count
- log evidence path
- KVS evidence summary
- verification result
- final live state
- knowhow promotion created/updated/skipped
- commit SHA after push, if successful
- uncertainty
- diff summary

## Completion notes

P0015 completed live verification on `2026-05-24`.

Verified endpoint/identity:

```text
runtime endpoint used: http://192.168.86.240:8030
stable LAN address: 192.168.77.30
physical Shelly id: 8813bfd99f54
live device id: shellypro1pm-8813bfd99f54
```

Mac Open-Meteo pre-live check passed:

```text
daily_response_bytes: 443
hourly_response_bytes: 308
solar_kwh_today: 52
temp_now: 22.6
temp_avg_today: 18.6
humidity_avg_today: 62.0
```

Build/validate passed:

```text
built weather_v0_9_0: 1 chunks
valid weather_v0_9_0
```

Live deploy and verification passed:

```text
script: weather_v0_9_0
script id: 2
upload_chunk_bytes: 1500
upload_chunk_count: 4
final script state: stopped
KVS key: g2.weather.act
```

Readback:

```json
{
  "solar_kwh_today": 52,
  "temp_now": 22.6,
  "temp_avg_today": 18.6,
  "humidity_avg_today": 62
}
```

Evidence:

```text
requirements/package-runs/P0015/review.md
requirements/package-runs/P0015/design.md
requirements/package-runs/P0015/functions.md
requirements/package-runs/P0015/attempts.md
```
