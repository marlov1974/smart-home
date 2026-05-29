# Spot Fixture Data

Last changed: P0024

This folder contains local spot-price fixtures used by Mac-side G2 planning tools.

## 2025 hourly Europe/Stockholm fixture

```text
data/spot/spot_2025_hourly_europe_stockholm.csv
data/spot/spot_2025_conversion_report.json
```

The hourly CSV is the source of truth for P0024 actual-price patching in the weekly home optimizer POC.

Canonical key:

```text
utc_hour_start
```

Do not join by `local_wall_hour`; the autumn DST transition repeats the local `02:00` hour. The fixture keeps `utc_hour_start`, `utc_offset` and `fold` so repeated local hours remain distinct.

Expected report properties:

```text
timezone = Europe/Stockholm
hourly_rows = 8760
all_hourly_quarter_count_is_4 = true
spring 2025-03-30 local day = 23 hours
fall 2025-10-26 local day = 25 hours
```
