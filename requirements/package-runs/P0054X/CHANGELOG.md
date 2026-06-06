# P0054X changelog

- Reviewed P0054W input against P0054X cluster-taxonomy requirements.
- Confirmed P0054W `EXP18/LoadProfile` covers only the profiled/load-profile component.
- Confirmed public eSett `EXP15` exposes measured/profiled/total at SE3/MBA level but not per MGA.
- Stopped before cluster generation because monthly-read/measured per-MGA series are missing.
- No models, DB taxonomy tables, credentials, devices or runtime changes were performed.

## 2026-06-06 clarification correction

- Added `partial-coverage-warning.md`.
- P0054X remains stopped for full SE3 taxonomy because P0054W currently covers only the `EXP18/LoadProfile` / `EXP15.profiled` component.
- A taxonomy may proceed only if explicitly labeled partial load-profile taxonomy, or if a later package adds the missing per-MGA `metered/non_profiled` source or residual group.
