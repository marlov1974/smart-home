# P0054W what we learned

1. eSett Open Data has public SE3 MGA masterdata and `EXP18/LoadProfile`.
2. `EXP18/LoadProfile` supports per-MGA querying and currently returns 15-minute rows in the preflight sample.
3. Source values are negative for load profile quantities; P0054W preserves that source sign.
4. Full SE3 fetch progress is checkpointed in `esett_mga_consumption_ingestion_checkpoint_v1`.

## 2026-06-06 correction

5. Time resolution and settlement/measurement class must be treated separately: a monthly-settled class may still arrive as 15m/60m rows.
6. P0054W `EXP18/LoadProfile` matches SE3/MBA `EXP15.profiled`, not `EXP15.metered` or `EXP15.total`.
7. Public eSett Open Data exposes `EXP15.metered` at SE3/MBA level, but no public per-MGA `metered/non_profiled` source was found in this package pass.
8. Full SE3 per-MGA bottom-up modeling must wait for that source or explicitly model a SE3 residual.
