# Open-Meteo Archive Rate Limit Resume

Open-Meteo archive can return persistent `HTTP 429 Too Many Requests` for both large multi-year requests and tiny date-range probes.

For package work that fetches many representative weather locations:

- Fetch one representative location and one small period chunk at a time after a rate-limit incident. Quarter-sized chunks were effective for P0056D.
- Commit or persist each completed chunk before starting the next chunk.
- Make reruns skip chunks whose expected row count is already complete.
- Add explicit backoff and spacing between non-cached requests.
- Never delete already fetched weather rows because a later chunk fails.
- Do not run dependent model training or retesting until required weather coverage is complete, unless the output is explicitly labeled partial sensitivity.
- Treat rate-limit interruptions as WARN with exact resume command and checkpoint evidence when Open-Meteo remains generally reachable. Reserve STOP for cases where repeated retries show the source cannot be accessed at all or required data cannot be loaded.

This was observed during P0056D on 2026-06-07 when SE1/SE2 location rows completed but FI was blocked by persistent Open-Meteo archive 429. On 2026-06-08 P0056D resumed successfully using 528 quarter-sized location-period chunks and chunk-level checkpoint evidence.
