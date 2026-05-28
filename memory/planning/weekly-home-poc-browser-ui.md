# Weekly Home POC Browser UI

Last changed: P0023

This file records the durable local browser contract for the Mac weekly home POC.

## Purpose

The browser UI exposes the P0018 weekly heat, PPM and RH-policy planner from a local Mac HTTP server for manual inspection from a browser or phone on the same LAN.

It is trusted-local POC tooling only. It is not a live controller and must not be exposed to the internet.

## Server command

Default local-only command:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 127.0.0.1 --port 8081
```

Phone/LAN manual test command:

```bash
python3 -m src.mac.labs.weekly_home_optimizer_poc.server --host 0.0.0.0 --port 8081
```

Phone URL pattern:

```text
http://<mac-lan-ip>:8081/
```

The default port is `8081` so it does not collide with the P0017 spot forecast service default port `8080`.

## Endpoints

```text
GET /
GET /?week=2&ppm=500&houseTemp=22&people=6
GET /api/weekly-home-poc?week=2&ppm=500&houseTemp=22&people=6
GET /health
```

`GET /` renders the form.

`GET /?week=...` renders the HTML result page.

`GET /api/weekly-home-poc?...` returns JSON:

```text
input
summary
hours
```

`hours` contains 168 hourly P0018 row objects for valid input.

`GET /health` returns compact JSON status.

## Input contract

Required query parameters:

```text
week
ppm
houseTemp
people
```

The browser UI does not add a reference year or indoor RH input.

`people` defaults to `3` when omitted and is valid in the POC range `0..20`.

The result summary includes:

```text
people
occupancy_gain_ppm_h
weather_source
weather_provider
weather_profile_strategy
weather_profile_year
weather_fallback_reason, when fallback occurred
heat_optimizer
heat_modes_kw
heat_soc_capacity_kWh
heat_soc_step_kWh
start_soc_pct
end_soc_min_pct
min_heat_soc_pct
end_heat_soc_pct
heat_optimizer_warnings
heat_cost_model
cop_model
optimized_heat_el_kWh
flat_heat_el_kWh
optimized_heat_el_cost
flat_heat_el_cost
optimized_vs_flat_cost_pct
optimized_saving_pct
avg_cop_optimized
avg_cop_flat
heat_cost_comparison_warnings
```

The result page displays the COP-emulated optimized-vs-flat comparison in summary cards and a plain operator sentence. The wording must keep the comparison labeled as emulated/POC rather than measured savings.

## Runtime boundary

The server only runs local POC calculations. It must not perform Shelly, FTX, VP or Home Assistant writes.
