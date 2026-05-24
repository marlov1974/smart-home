# P0015 Function Design

## Shelly Runtime: `src/shelly/weather/weather.js`

### `log`

- Status: new
- Purpose: prefix concise weather log lines.
- Inputs: message.
- Outputs: none.
- Side effects: writes to Shelly debug log.
- Test coverage: source/lint-style contract tests.

### `clip`, `round1`, `toNumber`, `toInt`

- Status: new
- Purpose: compact numeric normalization for weather fields.
- Inputs: raw values and bounds.
- Outputs: bounded numeric values.
- Side effects: none.
- Test coverage: mirrored Mac parser tests for expected rounding/clipping.

### `todayString`, `buildDailyUrl`, `buildHourlyUrl`

- Status: new
- Purpose: construct Open-Meteo URLs with house coordinates and required fields.
- Inputs: current date or constants.
- Outputs: URL strings.
- Side effects: none.
- Test coverage: source tests and Mac contract URL tests.

### `parseDailyWeather`

- Status: new
- Purpose: parse daily Open-Meteo JSON and extract solar proxy, mean temp and mean humidity.
- Inputs: daily JSON response body.
- Outputs: object with `solar_kwh_today`, `temp_avg_today`, `humidity_avg_today`.
- Side effects: log parse failures.
- Test coverage: Mac weather contract parser fixture tests and source field tests.

### `parseHourlyWeather`

- Status: new
- Purpose: parse hourly Open-Meteo JSON and extract near-current temperature.
- Inputs: hourly JSON response body.
- Outputs: object with `temp_now`.
- Side effects: log parse failures.
- Test coverage: Mac weather contract parser fixture tests and source field tests.

### `httpGet`

- Status: new
- Purpose: perform one bounded Shelly `HTTP.GET`.
- Inputs: URL, callback.
- Outputs: callback with body or null.
- Side effects: external HTTP call from Shelly.
- Test coverage: live verification.

### `kvsSet`

- Status: new
- Purpose: write one KVS value.
- Inputs: key, value object, callback.
- Outputs: callback with success boolean.
- Side effects: writes `g2.weather.act` only.
- Test coverage: source tests and live KVS verification.

### `selfStop`

- Status: new
- Purpose: stop `weather_v0_9_0` after one-shot completion.
- Inputs: none.
- Outputs: none.
- Side effects: calls `Script.Stop` for own script id.
- Test coverage: live script status after deploy.

### `runWeather`

- Status: new
- Purpose: orchestrate URL build, daily fetch, hourly fetch, KVS write and self-stop.
- Inputs: none.
- Outputs: none.
- Side effects: HTTP GET, KVS write, logs, self-stop.
- Test coverage: live deploy/log/KVS verification.

## Mac Tool: `src.mac.tools.weather_contract.core`

### `build_daily_url`, `build_hourly_url`

- Status: new
- Purpose: construct the same Open-Meteo URL shape used by the Shelly runtime.
- Inputs: date and coordinates.
- Outputs: URL string.
- Side effects: none.
- Test coverage: unit tests.

### `fetch_json`

- Status: new
- Purpose: fetch and decode JSON with response length evidence.
- Inputs: URL, timeout, opener.
- Outputs: decoded JSON and byte length.
- Side effects: external HTTP in live command.
- Test coverage: fake opener tests.

### `parse_daily`, `parse_hourly`

- Status: new
- Purpose: validate required Open-Meteo fields and normalize G2 weather output.
- Inputs: decoded JSON.
- Outputs: parsed weather dict.
- Side effects: raises on missing schema.
- Test coverage: fixture and error tests.

### `check_openmeteo`

- Status: new
- Purpose: run the Mac pre-live API/schema check and return evidence.
- Inputs: optional date, timeout, opener.
- Outputs: evidence dict.
- Side effects: external HTTP in live command.
- Test coverage: fake opener tests.

### `main`

- Status: new
- Purpose: CLI for `check-openmeteo`.
- Inputs: argv.
- Outputs: process exit code and JSON evidence.
- Side effects: stdout/stderr and external HTTP in live mode.
- Test coverage: lower-level unit tests.

## Mac Live Tool: `src.mac.tools.shelly_live.core`

### `deploy_weather`

- Status: new
- Purpose: upload/start/log/KVS-verify `weather_v0_9_0` on dampers only.
- Inputs: base URL, built script path, expected log text, timeouts, upload chunk size.
- Outputs: weather deploy evidence.
- Side effects: allowed script create/update/start/stop, read `g2.weather.act`.
- Test coverage: fake RPC/log/KVS sequence test.

### `verify_weather_kvs`

- Status: new
- Purpose: validate `g2.weather.act` shape and ranges.
- Inputs: KVS value.
- Outputs: summary dict.
- Side effects: none.
- Test coverage: valid and invalid KVS tests.

### `read_weather_kvs`, `wait_for_weather_kvs`

- Status: new
- Purpose: bounded read/poll of `g2.weather.act`.
- Inputs: base URL, timeouts, opener.
- Outputs: raw value and summary.
- Side effects: read-only KVS RPC.
- Test coverage: fake RPC tests.
