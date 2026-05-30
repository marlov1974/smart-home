# P0032 review

## Classification

PASS

## Repository truth

P0030 spotprice history exists at `~/.smart-home/data/spotprice_history.sqlite3`. Its `spot_prices` table already has primary key `(area, utc_hour_start)`, so SE1 can be stored beside SE3 without a disruptive schema change.

P0031 weather history exists at `~/.smart-home/data/weather_history.sqlite3`. Its schema can represent proxy groups by registering active locations with distinct `area_proxy` values and computing weighted hourly rows per group.

## Source checks

Read-only source checks on 2026-05-30:

- `https://www.elprisetjustnu.se/api/v1/prices/2022/05-30_SE1.json` returned 24 hourly rows.
- `https://www.elprisetjustnu.se/api/v1/prices/2026/05-29_SE1.json` returned 96 quarter-hour rows.

Therefore P0030's source/parser model supports SE1 for the requested period and newer quarter-hour data.

## Safety

P0032 requires only read-only HTTP and local SQLite writes. No Shelly, Home Assistant, KVS, Script, relay, dimmer, cover, switch, light, MCP or device access is required.

## Review conclusion

PASS. Implement P0032 as extensions to existing P0030/P0031 Mac data services.
