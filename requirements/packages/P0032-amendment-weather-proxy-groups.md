# P0032 amendment: Weather proxy groups for SE1 system-proxy and SE3 area-diff modeling

## Status

planned amendment to P0032

## Applies to

```text
requirements/packages/P0032-se1-system-proxy-history.md
requirements/packages/P0031-weather-history-dataset-service.md
```

This amendment is part of P0032 scope and must be read by Codex together with the main P0032 package file before P0032 review/design/implementation.

## User clarification

P0032 must do more than fetch SE1 spotprice and create the SE3-SE1 series.

It must also extend weather-history coverage so future temperature-normalization and V2 model packages can learn weather effects for:

```text
1. SE1 system_proxy_price
2. SE3-SE1 area_diff_proxy
```

SE1 is heavily affected by northern/nordic production and balance. Southern Sweden/SE4 should not dominate SE1 weather, but southern Norway, southern Finland and southern Sweden may still affect SE1/system-proxy as low-weight connected load/weather signals.

P0032 must therefore add weather proxy groups and gradient features, not just raw extra cities.

## Added P0032 outcomes

P0032 must now deliver:

```text
1. SE1 spotprice history backfilled and kept current
2. SE3-SE1 area_diff_proxy and SE3/SE1 area_ratio_proxy available
3. additional Nordic/Open-Meteo weather locations added to weather_history storage
4. weather proxy groups computed/stored or exposed for future model packages
5. weather gradients computed/stored or exposed for future model packages
```

This remains data-foundation work only. No ML training is allowed in P0032.

## Required weather proxy groups

Codex must design and implement the following durable proxy groups or equivalent names documented in design:

```text
se1_core_weather
nordic_connected_weather
south_connected_weather
se3_load_weather
```

### se1_core_weather

Purpose:

```text
Primary weather signal for SE1 system_proxy_price.
```

Expected high-weight locations:

```text
Kiruna
Gällivare
Luleå
Skellefteå
Umeå
Östersund
Sundsvall
Rovaniemi
Oulu
Tromsø
Narvik
Bodø
```

### nordic_connected_weather

Purpose:

```text
Connected Nordic weather/load signal that may affect SE1/system-proxy with lower weight than core north.
```

Expected medium/low-weight locations:

```text
Trondheim
Oslo
Bergen
Helsinki
Tampere
Turku
```

### south_connected_weather

Purpose:

```text
Low-weight southern connected load/weather signal. It may affect broad system-proxy but should not dominate SE1.
```

Expected low-weight locations:

```text
Stockholm
Göteborg
Malmö
Copenhagen
```

### se3_load_weather

Purpose:

```text
Primary load/weather signal for SE3 demand and SE3-SE1 area_diff_proxy.
```

Expected locations:

```text
Stockholm
Örebro
Västerås
Linköping
Norrköping
Göteborg
Jönköping
Karlstad
Borlänge
Gävle
Kalmar
Växjö
```

Codex may adjust exact coordinates and weights during design, but must preserve the intent:

```text
- SE1/system-proxy weather is dominated by northern/nordic core locations.
- southern connected locations have small weights only.
- SE3 load weather is a separate proxy group.
```

## Required weather variables

For each added location, fetch/store the same P0031 required hourly variables:

```text
temperature_2m
apparent_temperature
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
```

P0032 must reuse P0031 weather_history code/schema where possible. It must not create a separate incompatible weather database unless P0031 schema cannot be safely extended.

Expected DB:

```text
~/.smart-home/data/weather_history.sqlite3
```

## Required proxy and gradient outputs

P0032 must create queryable group-level hourly series for future model packages.

Expected outputs, as tables, views, or deterministic export/query functions:

```text
weather_proxy_se1_core_hourly
weather_proxy_nordic_connected_hourly
weather_proxy_south_connected_hourly
weather_proxy_se3_load_hourly
```

At minimum, each proxy group must expose weighted hourly values for:

```text
temperature_2m
apparent_temperature
heating_degree_hours
cooling_degree_hours
wind_speed_10m
wind_speed_100m
wind_gusts_10m
cloud_cover
shortwave_radiation
precipitation
snowfall
relative_humidity_2m
pressure_msl
source_coverage_count
source_coverage_weight
```

P0032 must also expose gradient features, at least:

```text
temp_gradient_se3_load_minus_se1_core
apparent_temp_gradient_se3_load_minus_se1_core
heating_degree_gradient_se3_load_minus_se1_core
wind_100m_gradient_nordic_connected_minus_se3_load
south_temp_gradient_minus_se1_core
```

Codex may choose additional useful gradients, but must document them.

## Weighting policy

P0032 must define initial deterministic weights. These are not final ML weights; they are feature-construction weights.

Expected policy:

```text
se1_core_weather: highest aggregate weight for SE1/system-proxy
nordic_connected_weather: lower aggregate weight
south_connected_weather: low aggregate weight only
se3_load_weather: separate, optimized for SE3 load/area-diff features
```

Codex must document:

```text
- location list
- coordinates
- group assignment
- per-group weights
- rationale
```

Future ML packages may learn actual influence from the proxy/gradient features.

## Backfill and daily ingest requirements

P0032 must backfill new weather locations and proxy group rows for the same period as P0031/P0030:

```text
start: 2022-05-30
end: latest safely available weather data at build time
```

It must also update daily weather ingest so added locations and proxy groups remain current.

Preferred approach:

```text
extend the existing P0031 weather_history daily ingest job to include all active weather locations and recompute all proxy groups/gradients
```

If P0031 launchd job must change, Codex must:

```text
- back up or document existing plist state
- update only user-level LaunchAgent
- verify launchd status
- document rollback commands
```

No separate weather launchd job should be created unless Codex documents why extending P0031 is unsafe.

## Validation requirements

P0032 must validate and report:

```text
- added location row counts
- added location gap counts
- added location null counts per required variable
- proxy group row counts
- proxy group gap counts
- source coverage count/weight per proxy group
- gradient row counts
- gradient null counts
- first/last timestamp for added locations/proxies/gradients
- DB size impact
- daily ingest verification after extension
```

Completeness rule:

```text
proxy group complete=true only if required group locations have complete weather rows or design explicitly allows partial group coverage with coverage metadata and WARN evidence.
```

No synthetic gap filling is allowed.

## Design additions

`requirements/package-runs/P0032/design.md` must include:

```text
- exact weather locations and coordinates
- group names and weights
- P0031 weather DB/schema extension plan
- proxy group table/view/query model
- gradient table/view/query model
- backfill command for added weather locations
- daily ingest extension plan
- launchd update plan if needed
- validation/completeness rules for proxies and gradients
- how future P0033 temperature-normalization ML should consume these features
```

## Function additions

`requirements/package-runs/P0032/functions.md` must document functions or equivalent responsibilities for:

```text
register_weather_proxy_locations(...)
backfill_weather_proxy_locations(...)
compute_weather_proxy_groups(...)
compute_weather_gradients(...)
validate_weather_proxy_groups(...)
extend_weather_daily_ingest(...)
```

## Additional test cases

Add or update tests for:

```text
TC12: proxy group locations are registered with expected groups and weights
TC13: proxy group computation produces weighted hourly rows
TC14: gradient computation produces expected differences between proxy groups
TC15: southern connected weather has lower aggregate weight than se1_core_weather for SE1/system-proxy
TC16: weather daily ingest includes added active locations and updates proxy groups
TC17: proxy/gradient validation reports missing data without synthetic filling
```

## Verification additions

Expected command equivalents:

```bash
python3 -m src.mac.services.weather_history backfill --db ~/.smart-home/data/weather_history.sqlite3 --locations proxy-groups
python3 -m src.mac.services.weather_history compute-proxy-groups --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history validate-proxy-groups --db ~/.smart-home/data/weather_history.sqlite3
python3 -m src.mac.services.weather_history ingest-daily --db ~/.smart-home/data/weather_history.sqlite3
launchctl print gui/$(id -u)/se.mlovholm.smart-home.weather-history-daily
```

If actual command names differ, document equivalents in design/attempts.

## Safety constraints unchanged

This amendment does not permit:

```text
- ML training
- temperature-normalized price modeling
- optimizer/control changes
- Shelly deploy
- Shelly RPC/KVS writes
- Home Assistant integration
- actuator/device access
- synthetic gap filling
- external Python dependencies without STOP/approval
- root/system launch daemon
- public network service exposure
```

## Expected Codex output added

Codex final output must include:

```text
- added weather locations and coordinates
- proxy group names and weights
- weather DB path
- backfill result for added locations
- proxy group/gradient validation result
- daily weather ingest extension result
- launchd status if changed
- DB size impact
- confirmation that no ML/weather-normalized price model was built in P0032
```
