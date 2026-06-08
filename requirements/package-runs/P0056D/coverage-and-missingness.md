# P0056D Coverage And Missingness

## Status

`STOP`

## Coverage

| area | expected locations | loaded locations | loaded rows | status |
| --- | ---: | ---: | ---: | --- |
| SE1 | 7 | 7 | 245448 | complete |
| SE2 | 9 | 9 | 315576 | complete |
| FI | 17 | 0 | 0 | blocked by Open-Meteo 429 |

## Missingness

- `snow_depth` remains unavailable from the existing Open-Meteo helper and would be labelled optional missing.
- FI P0056D proxy/features were not built because required FI representative locations could not be fetched.

