# Station / Proxy Selection

| area | source_kind | source_id | source_name | weight | fallback | coverage_start | coverage_end | reason |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| SE1 | area_proxy | se1_core_weather | se1_core_weather | 1.000 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Northern Sweden load-weighted weather proxy. |
| SE2 | area_proxy | se1_core_weather | se1_core_weather | 0.650 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Cold northern Swedish component. |
| SE2 | area_proxy | se3_load_weather | se3_load_weather | 0.350 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern transition component for SE2 load geography. |
| SE3 | area_proxy | se3_load_weather | se3_load_weather | 1.000 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Existing SE3 broad load weather proxy. |
| SE4 | area_proxy | se4_load_weather | se4_load_weather | 1.000 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Existing SE4 load weather proxy. |
| NO1 | location | nordic_connected_oslo | Oslo | 0.800 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Oslo/East Norway load centre. |
| NO1 | location | nordic_connected_bergen | Bergen | 0.200 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Western Norwegian weather influence. |
| NO2 | location | nordic_connected_bergen | Bergen | 0.550 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | South-west Norway load and coast component. |
| NO2 | location | nordic_connected_oslo | Oslo | 0.250 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | South Norway inland/east component. |
| NO2 | location | south_connected_goteborg | Goteborg | 0.200 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Nearby southern Nordic fallback component. |
| NO3 | location | nordic_connected_trondheim | Trondheim | 0.800 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Central Norway load centre. |
| NO3 | location | nordic_connected_bergen | Bergen | 0.200 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Coastal Norway moderation. |
| NO4 | location | se1_core_tromso | Tromso | 0.350 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Northern Norway coastal component. |
| NO4 | location | se1_core_bodo | Bodo | 0.250 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Nordland coastal component. |
| NO4 | location | se1_core_narvik | Narvik | 0.250 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Northern inland/coastal transition. |
| NO4 | location | nordic_connected_trondheim | Trondheim | 0.150 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern NO4 transition component. |
| NO5 | location | nordic_connected_bergen | Bergen | 0.750 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | West Norway load centre. |
| NO5 | location | nordic_connected_oslo | Oslo | 0.250 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Inland/east transition component. |
| DK1 | location | south_connected_copenhagen | Copenhagen | 0.450 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Available Denmark station, fallback for Jutland. |
| DK1 | location | south_connected_malmo | Malmo | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Nearby southern Scandinavia fallback. |
| DK1 | location | south_connected_goteborg | Goteborg | 0.250 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Western Scandinavia fallback. |
| DK2 | location | south_connected_copenhagen | Copenhagen | 0.800 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Zealand/Copenhagen load centre. |
| DK2 | location | south_connected_malmo | Malmo | 0.200 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Oresund regional component. |
| FI | location | nordic_connected_helsinki | Helsinki | 0.350 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Finland load centre. |
| FI | location | nordic_connected_tampere | Tampere | 0.250 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Inland Finland load centre. |
| FI | location | nordic_connected_turku | Turku | 0.200 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | South-west Finland component. |
| FI | location | se1_core_oulu | Oulu | 0.100 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Northern Finland component. |
| FI | location | se1_core_rovaniemi | Rovaniemi | 0.100 | False | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Lapland component. |
| EE | location | nordic_connected_helsinki | Helsinki | 0.450 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Nearest configured Baltic-adjacent station. |
| EE | location | south_connected_stockholm | Stockholm | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Baltic Sea regional fallback. |
| EE | location | nordic_connected_turku | Turku | 0.250 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | South Finland fallback. |
| LV | location | nordic_connected_helsinki | Helsinki | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Baltic north fallback. |
| LV | location | south_connected_stockholm | Stockholm | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Baltic Sea regional fallback. |
| LV | location | south_connected_copenhagen | Copenhagen | 0.200 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Baltic fallback. |
| LV | location | south_connected_malmo | Malmo | 0.200 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Baltic fallback. |
| LT | location | south_connected_copenhagen | Copenhagen | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Baltic fallback. |
| LT | location | south_connected_malmo | Malmo | 0.250 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Baltic fallback. |
| LT | location | south_connected_stockholm | Stockholm | 0.250 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Baltic Sea regional fallback. |
| LT | location | nordic_connected_helsinki | Helsinki | 0.200 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Northern Baltic fallback. |
| DE_LU | location | south_connected_copenhagen | Copenhagen | 0.450 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Closest configured continental-adjacent station. |
| DE_LU | location | south_connected_malmo | Malmo | 0.350 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Baltic/North Germany fallback. |
| DE_LU | location | south_connected_goteborg | Goteborg | 0.200 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Western Scandinavian fallback. |
| PL | location | south_connected_malmo | Malmo | 0.400 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Baltic fallback. |
| PL | location | se3_load_kalmar | Kalmar | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | South-east Sweden/Baltic fallback. |
| PL | location | south_connected_copenhagen | Copenhagen | 0.200 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Western Baltic fallback. |
| PL | location | south_connected_stockholm | Stockholm | 0.100 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Baltic regional fallback. |
| NL | location | south_connected_copenhagen | Copenhagen | 0.450 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Closest configured North Sea-adjacent fallback. |
| NL | location | south_connected_malmo | Malmo | 0.300 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Southern Scandinavia fallback. |
| NL | location | south_connected_goteborg | Goteborg | 0.250 | True | 2022-05-29T22:00Z | 2026-05-31T21:00Z | Western Scandinavia fallback. |
