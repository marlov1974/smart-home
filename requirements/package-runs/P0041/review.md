# P0041 consistency review

Status: PASS

P0041 is consistent with repository state after synchronization with `origin/main`.

The active package defines a new seven-day index forecast dataset track and explicitly keeps M2A/M2C/M2D signal-normal infrastructure while demoting M1/M1B/M3A/M3B/M3C/M3D/M4 to legacy diagnostic or fallback status for this track. Existing P0037/P0038/P0039/P0040 diagnostics already provide local joined rows, Swedish special-day fields, SE1 and SE3-SE1 split targets, P0038 wind/solar proxy locations, and weather proxy transforms that P0041 can reuse without touching Shelly, Home Assistant, KVS, API, or optimizer paths.

Assumptions:

- Local dataset tables may be written to the existing local feature SQLite database under `~/.smart-home/data/spotprice_model_features.sqlite3`; SQLite databases are not committed.
- P0041 creates training target datasets and feature contracts only. It does not train AI-1/AI-2 and does not promote any model.
- M2 normal weather surfaces are smooth/cyclic historical signal normals for feature construction, not forecast-time target-derived price models.
- Incomplete local seven-day windows are skipped for AI-1, matching the package preference.

Scope boundaries:

- No Shelly/device/Home Assistant/KVS calls.
- No M5/M6/M7/API/optimizer/control path.
- No AI model training.
- No continuation of the old M1+M3+M4 chain as the primary seven-day architecture.
