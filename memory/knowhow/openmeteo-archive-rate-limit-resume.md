# Open-Meteo Archive Rate Limit Resume

Open-Meteo archive can return persistent `HTTP 429 Too Many Requests` for both large multi-year requests and tiny date-range probes.

For package work that fetches many representative weather locations:

- Commit or persist each completed location before starting the next location.
- Make reruns skip locations whose expected row count is already complete.
- Add explicit backoff and spacing between non-cached requests.
- Treat incomplete required weather locations as STOP for packages that require all selected representative series before model training.

This was observed during P0056D on 2026-06-07 when SE1/SE2 location rows completed but FI was blocked by persistent Open-Meteo archive 429.

