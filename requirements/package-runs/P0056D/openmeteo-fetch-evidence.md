# P0056D Open-Meteo Fetch Evidence

## Status

`STOP`

Open-Meteo archive access is currently rate-limited with `HTTP 429 Too Many Requests`.

## Completed P0056D Fetches

| area | locations | rows |
| --- | ---: | ---: |
| SE1 | 7 | 245448 |
| SE2 | 9 | 315576 |
| FI | 0 | 0 |

Each completed location has 35064 hourly rows for `2022-06-01..2026-05-31`.

## Blocking Error

The first FI location, `FI_HELSINKI_ESPOO_VANTAA_RING_HELSINKI`, failed with persistent `HTTP Error 429: Too Many Requests` after backoff waits of 60, 180, 420 and 900 seconds.

A tiny independent Open-Meteo archive request for Helsinki covering only `2022-06-01..2022-06-02` also returned `HTTP/1.1 429 Too Many Requests`, so the block is not caused only by large payload size.

## Resumability

The P0056D runner now keeps location-level rows across reruns and skips locations whose row count already matches the expected 35064 hours. A later rerun should skip SE1/SE2 and resume at FI when Open-Meteo allows archive requests again.

