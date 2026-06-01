# P0045 package consistency review

Status: PASS

P0045 is consistent with current repository truth and can proceed.

Evidence checked before editing:

- Repository was synchronized with `origin/main` before reading package files.
- P0045 package file exists at `requirements/packages/P0045-combine-ai1-ai2-168h-shape-forecast.md`.
- P0042 evidence is PASS and identifies corrected fixed-CET v2 datasets.
- P0043 evidence is PASS and identifies AI-2 selected groups:
  - `system_proxy_se1 = F4_full`
  - `area_diff_proxy_se3 = F2_time_calendar_weather_actual`
- P0044 evidence is WARN and identifies the target usage policy required by P0045:
  - use all SE1 AI-1 targets
  - use area_diff `day_level_shape` cautiously
  - use deterministic fallbacks for weak area_diff scale targets
- Local feature DB contains:
  - `ai1_day_to_local_week_training_targets_v2`
  - `ai2_hour_to_day_training_targets_v2`

Important implementation assumption:

P0043 and P0044 committed model configuration/evidence but no binary model artifacts. P0045 will therefore regenerate AI-1/AI-2 predictions deterministically from the stored selected feature groups and the corrected P0042 train rows. This is documented as artifact regeneration for evaluation, not new model development or hyperparameter search.

Safety review:

- P0045 is Mac-only historical evaluation.
- It may read the local feature SQLite DB and write package evidence/code/tests/docs.
- It must not create an API, train new model variants, call devices, call Shelly, call Home Assistant, write KVS or touch optimizer/control paths.
