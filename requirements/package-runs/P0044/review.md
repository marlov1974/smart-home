# P0044 package consistency review

Status: PASS

P0044 is consistent with the current repository state.

Evidence checked before editing:

- Repository was synchronized with `origin/main` by fast-forward pull before package files were read.
- `requirements/packages/P0044-train-ai1-day-to-local-week-shape-scale-model.md` exists and is the active package.
- P0042 evidence documents corrected fixed-CET dataset generation and reduced skipped fixed-CET days.
- P0043 evidence documents PASS status and the required AI-2 selected groups: `system_proxy_se1=F4_full`, `area_diff_proxy_se3=F2_time_calendar_weather_actual`.
- Local feature DB contains corrected P0042 AI-1 table `ai1_day_to_local_week_training_targets_v2` with both required target series and rows from 2022-06-01 through 2026-05-21.

Safety review:

- P0044 is Mac-only model diagnostics/training evidence.
- It must read local SQLite data only and write package-run evidence/code/tests/docs.
- No Shelly, Home Assistant, KVS, device, API, optimizer, M5, M6, M7, combined 168h forecast or AI-2 retraining is authorized.
- The implementation must fail if the P0042 v2 AI-1 table is missing rather than falling back to pre-correction data.

Assumptions:

- `scikit-learn` is available locally from prior packages.
- P0044 may write small JSON model configuration evidence to the repository but will not commit binary model artifacts.
