# P0015 Attempts and Verification Evidence

## Attempt 1

Result: PASS

## Mac Open-Meteo Pre-Live Check

Command:

```bash
python3 -m src.mac.tools.weather_contract check-openmeteo
```

Result:

```text
date: 2026-05-24
daily_response_bytes: 443
hourly_response_bytes: 308
daily.shortwave_radiation_sum[0]: present
daily.temperature_2m_mean[0]: present
daily.relative_humidity_2m_mean[0]: present
hourly.temperature_2m[0]: present
solar_kwh_today: 52
temp_now: 22.6
temp_avg_today: 18.6
humidity_avg_today: 62.0
```

## Build

Commands:

```bash
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/weather/manifest.json --build-root build/shelly/weather --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/weather --dep-root dep/s --role weather_v0_9_0
```

Result:

```text
built weather_v0_9_0: 1 chunks
valid weather_v0_9_0
built script bytes: 5442
repo chunk bytes: 5442
```

## Live Dampers Deploy

Command:

```bash
python3 -m src.mac.tools.shelly_live deploy-weather --base-url http://192.168.86.240:8030 --script build/shelly/weather/weather_v0_9_0.js --expect 'weather_v0_9_0 DONE' --log-timeout 30 --kvs-timeout 30
```

Target verification:

```text
runtime endpoint: http://192.168.86.240:8030
stable LAN: 192.168.77.30
expected physical id: 8813bfd99f54
live device id: shellypro1pm-8813bfd99f54
```

Deploy result:

```text
script: weather_v0_9_0
script id: 2
upload_chunk_bytes: 1500
upload_chunk_count: 4
before scripts: spotprice_v0_9_0 stopped
after scripts: spotprice_v0_9_0 stopped, weather_v0_9_0 stopped
```

KVS readback:

```json
{
  "solar_kwh_today": 52,
  "temp_now": 22.6,
  "temp_avg_today": 18.6,
  "humidity_avg_today": 62
}
```

Log evidence summary:

```text
weather_v0_9_0 BOT
weather_v0_9_0 DATE 2026-05-24
weather_v0_9_0 DAILY GET
weather_v0_9_0 DAILY OK len=443
weather_v0_9_0 HOURLY GET
weather_v0_9_0 HOURLY OK len=307
weather_v0_9_0 KVS SET solar=52 temp=22.6 avg=18.6 hum=62
weather_v0_9_0 KVS OK
weather_v0_9_0 DONE
```

Runtime health:

```text
No out_of_memory marker observed.
No missing KVS output.
Script final state: stopped.
No actuator/output RPC was used by the Mac tool or weather script.
No write to ftx.weather.act.
No ftx-vvx endpoint was used.
```

Note: unrelated `Shelly.GetComponents ... via SHC` log lines appeared during log streaming. They were not emitted by the P0015 Mac tool or weather script and did not correspond to P0015 writes.

Knowhow promotion:

```text
Skipped. P0015 confirmed the already-planned Mac pre-live API check pattern and documented it in the function catalog, but did not discover a new reusable Shelly runtime anomaly or workaround.
```

## Verification Commands

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.weather_contract check-openmeteo
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/weather/manifest.json --build-root build/shelly/weather --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/weather --dep-root dep/s --role weather_v0_9_0
python3 -m src.mac.tools.shelly_live deploy-weather --base-url http://192.168.86.240:8030 --script build/shelly/weather/weather_v0_9_0.js --expect 'weather_v0_9_0 DONE' --log-timeout 30 --kvs-timeout 30
git diff --check
```
