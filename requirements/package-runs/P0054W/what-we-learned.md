# P0054W what we learned

1. eSett Open Data has public SE3 MGA masterdata and `EXP18/LoadProfile`.
2. `EXP18/LoadProfile` supports per-MGA querying and currently returns 15-minute rows in the preflight sample.
3. Source values are negative for load profile quantities; P0054W preserves that source sign.
4. Full SE3 fetch progress is checkpointed in `esett_mga_consumption_ingestion_checkpoint_v1`.
