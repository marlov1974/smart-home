# P0032 weather location weights

Captured from local SQLite DB:

```text
/Users/marcus.lovenstad/.smart-home/data/weather_history.sqlite3
```

Query:

```sql
select area_proxy, name, latitude, longitude, weight
from weather_locations
where area_proxy in (
  'se1_core_weather',
  'nordic_connected_weather',
  'south_connected_weather',
  'se3_load_weather'
)
order by area_proxy, weight desc, name;
```

Result:

```text
nordic_connected_weather|Helsinki|60.1699|24.9384|0.18
nordic_connected_weather|Oslo|59.9139|10.7522|0.18
nordic_connected_weather|Trondheim|63.4305|10.3951|0.18
nordic_connected_weather|Tampere|61.4978|23.761|0.16
nordic_connected_weather|Turku|60.4518|22.2666|0.16
nordic_connected_weather|Bergen|60.3913|5.3221|0.14
se1_core_weather|Kiruna|67.8558|20.2253|0.11
se1_core_weather|Gallivare|67.1339|20.6528|0.1
se1_core_weather|Lulea|65.5848|22.1547|0.1
se1_core_weather|Skelleftea|64.7507|20.9528|0.09
se1_core_weather|Umea|63.8258|20.263|0.09
se1_core_weather|Ostersund|63.1792|14.6357|0.08
se1_core_weather|Oulu|65.0121|25.4651|0.08
se1_core_weather|Rovaniemi|66.5039|25.7294|0.08
se1_core_weather|Sundsvall|62.3908|17.3069|0.08
se1_core_weather|Tromso|69.6492|18.9553|0.07
se1_core_weather|Bodo|67.2804|14.4049|0.06
se1_core_weather|Narvik|68.4385|17.4273|0.06
se3_load_weather|Stockholm|59.3293|18.0686|0.16
se3_load_weather|Goteborg|57.7089|11.9746|0.1
se3_load_weather|Orebro|59.2753|15.2134|0.1
se3_load_weather|Vasteras|59.6099|16.5448|0.1
se3_load_weather|Linkoping|58.4108|15.6214|0.09
se3_load_weather|Jonkoping|57.7826|14.1618|0.08
se3_load_weather|Norrkoping|58.5877|16.1924|0.08
se3_load_weather|Karlstad|59.4022|13.5115|0.07
se3_load_weather|Borlange|60.4858|15.4371|0.06
se3_load_weather|Gavle|60.6749|17.1413|0.06
se3_load_weather|Kalmar|56.6634|16.3568|0.05
se3_load_weather|Vaxjo|56.879|14.8059|0.05
south_connected_weather|Stockholm|59.3293|18.0686|0.06
south_connected_weather|Goteborg|57.7089|11.9746|0.05
south_connected_weather|Malmo|55.605|13.0038|0.05
south_connected_weather|Copenhagen|55.6761|12.5683|0.04
```

Assessment: weights match the P0032 implementation contract in `src/mac/services/weather_history/storage.py`. Group totals are practical proxy weights, not normalized to 1.0 for every group in storage; P0033 uses existing weighted proxy outputs and the P0033 Level 2 climate weights documented in `climate-weight-selection.md`.
