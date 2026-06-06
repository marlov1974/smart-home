# P0054Z weather source inventory

```json
{
  "broad_proxy": {
    "area_proxy": "se3_load_weather",
    "max_ts": "2026-05-31T21:00Z",
    "min_ts": "2022-05-29T22:00Z",
    "rows": 35112
  },
  "has_required_source": true,
  "missing_required_station_ids": [],
  "required_station_ids": [
    "se3_load_borlange",
    "se3_load_gavle",
    "se3_load_goteborg",
    "se3_load_jonkoping",
    "se3_load_kalmar",
    "se3_load_karlstad",
    "se3_load_linkoping",
    "se3_load_norrkoping",
    "se3_load_orebro",
    "se3_load_stockholm",
    "se3_load_vasteras",
    "se3_load_vaxjo"
  ],
  "weather_area_hourly": [
    {
      "area_proxy": "SE3",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "nordic_connected_weather",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "p0038_central_wind_proxy",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "p0038_north_solar_proxy",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "p0038_north_wind_proxy",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "p0038_se3_load_solar_proxy",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "p0038_south_solar_proxy",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "p0038_south_wind_proxy",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "se1_core_weather",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "se3_load_weather",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "se4_load_weather",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    },
    {
      "area_proxy": "south_connected_weather",
      "max_ts": "2026-05-31T21:00Z",
      "min_ts": "2022-05-29T22:00Z",
      "rows": 35112
    }
  ],
  "weather_locations": [
    {
      "active": 1,
      "area_proxy": "SE3",
      "latitude": 57.7089,
      "location_id": "goteborg",
      "longitude": 11.9746,
      "name": "Goteborg / western SE3",
      "weight": 0.25
    },
    {
      "active": 1,
      "area_proxy": "SE3",
      "latitude": 58.4108,
      "location_id": "linkoping",
      "longitude": 15.6214,
      "name": "Linkoping / southern SE3",
      "weight": 0.2
    },
    {
      "active": 1,
      "area_proxy": "SE3",
      "latitude": 59.2753,
      "location_id": "orebro",
      "longitude": 15.2134,
      "name": "Orebro / inland SE3",
      "weight": 0.2
    },
    {
      "active": 1,
      "area_proxy": "SE3",
      "latitude": 59.3293,
      "location_id": "stockholm",
      "longitude": 18.0686,
      "name": "Stockholm / Malardalen",
      "weight": 0.35
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 60.4858,
      "location_id": "se3_load_borlange",
      "longitude": 15.4371,
      "name": "Borlange",
      "weight": 0.06
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 60.6749,
      "location_id": "se3_load_gavle",
      "longitude": 17.1413,
      "name": "Gavle",
      "weight": 0.06
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 57.7089,
      "location_id": "se3_load_goteborg",
      "longitude": 11.9746,
      "name": "Goteborg",
      "weight": 0.1
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 57.7826,
      "location_id": "se3_load_jonkoping",
      "longitude": 14.1618,
      "name": "Jonkoping",
      "weight": 0.08
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 56.6634,
      "location_id": "se3_load_kalmar",
      "longitude": 16.3568,
      "name": "Kalmar",
      "weight": 0.05
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 59.4022,
      "location_id": "se3_load_karlstad",
      "longitude": 13.5115,
      "name": "Karlstad",
      "weight": 0.07
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 58.4108,
      "location_id": "se3_load_linkoping",
      "longitude": 15.6214,
      "name": "Linkoping",
      "weight": 0.09
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 58.5877,
      "location_id": "se3_load_norrkoping",
      "longitude": 16.1924,
      "name": "Norrkoping",
      "weight": 0.08
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 59.2753,
      "location_id": "se3_load_orebro",
      "longitude": 15.2134,
      "name": "Orebro",
      "weight": 0.1
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 59.3293,
      "location_id": "se3_load_stockholm",
      "longitude": 18.0686,
      "name": "Stockholm",
      "weight": 0.16
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 59.6099,
      "location_id": "se3_load_vasteras",
      "longitude": 16.5448,
      "name": "Vasteras",
      "weight": 0.1
    },
    {
      "active": 1,
      "area_proxy": "se3_load_weather",
      "latitude": 56.879,
      "location_id": "se3_load_vaxjo",
      "longitude": 14.8059,
      "name": "Vaxjo",
      "weight": 0.05
    }
  ]
}
```
