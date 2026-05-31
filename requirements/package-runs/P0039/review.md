# P0039 Review

Status: WARN

## Consistency Result

P0039 is consistent with the current G2 Mac-side spotprice diagnostics direction and can be implemented without device, Shelly, Home Assistant, KVS, API, M5/M6/M7, or production activation changes.

The package is broad because it asks for taxonomy documentation, M1B implementation, sequential M3A/M3B recomputation, optional downstream M3C/M3D use, strict full-year holdout evidence, and local feature DB outputs. The safe package interpretation is:

- implement strict train-only M1B diagnostics and local feature DB tables for P0039 outputs
- recompute M3A and M3B on the M1B sequential residual contract
- document M3C/M3D/M4 target contracts for future packages
- do not rename existing M3A/M3B/P0038 tables
- do not change production model promotion or server/API behavior

## Repository Truth Checked

- `README.md`, `memory/bootstrap-manifest.json`, and manifest bootstrap files were read.
- `requirements/packages/P0039-holiday-clean-m1b-and-sequential-residual-taxonomy.md` defines the active package.
- `src/mac/services/spotprice_model_diagnostics/p0037.py` already provides strict 2025 holdout splitting, M1/M2/M3A/M3B diagnostics, and component evidence helpers.
- `src/mac/services/spotprice_model_diagnostics/p0038.py` already provides M3C/M3D solar/wind diagnostics and writes existing M3ABCD tables.
- `docs/functions/mac/spotprice-ml-normal-model.md` documents P0036 M4 and needs the new taxonomy status.

## Assumptions

- M1B uses exclusion, not weights: only `normal_weekday`, `normal_saturday`, and `normal_sunday` training rows are included.
- Midsummer Day is excluded because the Swedish calendar classifies it as `major_social_holiday`, not `normal_saturday`.
- P0039 strict evidence uses train rows through `2023-12-31`; validation and 2025 holdout are never used to fit M1B/M3A/M3B.
- P0039 may write diagnostic tables to the local feature database, but generated SQLite databases and prediction dumps are not committed.

## Safety

No live device access is allowed or needed. P0039 must not call Shelly, Home Assistant, KVS, MCP, or actuator/device APIs.
