# P0032 function design

## Spotprice history changes

`ensure_system_proxy_view(conn)`

- Creates `spotprice_system_proxy_hourly`.

`ingest_daily_for_areas(conn, areas, db_path, today, fetcher)`

- Runs P0030 daily ingest for all configured areas, default `SE3,SE1`.

`validate_system_proxy(conn, start_date, end_date, db_path)`

- Validates SE1 continuity, SE3/SE1 alignment, diff stats and ratio null policy.

## Weather history changes

`register_default_locations(conn)`

- Registers P0031 SE3 locations and P0032 proxy-group locations.

`all_area_proxies(conn)`

- Returns all active `area_proxy` groups.

`compute_all_area_proxy_hourly(conn, start_date, end_date, ingest_run_id)`

- Recomputes weighted hourly rows for every active proxy group.

`compute_weather_gradients(conn, start_date, end_date, ingest_run_id)`

- Materializes P0032 gradient rows.

`validate_proxy_groups(conn, start_date, end_date, db_path)`

- Validates proxy group rows and gradient rows.

`backfill(..., area_proxies=None)`

- Fetches active locations for selected groups and computes groups/gradients.

`ingest_daily(...)`

- Keeps all active proxy groups current through latest safe day.
