# P0056D What We Learned

- Open-Meteo archive rate limits can persist beyond 20 minutes and affect even tiny requests.
- P0056D fetches must be resumable at location granularity; the runner now commits after each location and skips complete cached locations.
- SE1 and SE2 Open-Meteo P0056D location data was fetched completely before the rate limit blocked FI.
- A future rerun should start after a longer Open-Meteo cooldown and should reuse the already committed SE1/SE2 rows.

