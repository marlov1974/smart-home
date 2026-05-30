# P0032 changelog

## Added

- Added SE1 spotprice history to the existing P0030 SQLite DB.
- Added `spotprice_system_proxy_hourly` view.
- Added system-proxy validation CLI.
- Added P0032 weather proxy group locations.
- Added weather proxy group views and materialized gradient table.
- Added proxy-group validation CLI.
- Added tests for spot system proxy and weather proxy groups.

## Changed

- Changed spotprice daily LaunchAgent command to `--areas SE3,SE1`.
- Changed weather daily ingest to cover all active weather proxy groups and recompute gradients.
- Updated docs for spotprice and weather history datasets.
