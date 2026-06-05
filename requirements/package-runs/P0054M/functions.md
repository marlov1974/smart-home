# P0054M Function Design

## New Functions

`run_p0054m_analysis(...)`

- Purpose: orchestrate price feature generation, consumption dataset construction, paired model training, evaluation and evidence writing.
- Inputs: local feature DB, weather DB and evidence directory.
- Outputs: result object with status, row counts and evidence paths.
- Side effects: writes package-run evidence and a local SQLite P0054M train-side price forecast table.

`build_blocked_oof_price_rows(...)`

- Purpose: create train-side safe advanced SE3 price rows for 2025-03..2025-05 using P0054L2-compatible models trained only before 2025-03.
- Inputs: reconstructed SE3 price rows.
- Outputs: forecast rows shaped like downstream price feature rows.
- Side effects: none.

`load_p0054l2_holdout_price_rows(...)`

- Purpose: read P0054L2 Ensemble holdout forecast rows and normalize them for P0054K-style consumption row building.
- Inputs: feature DB path.
- Outputs: normalized price forecast rows plus source contract.
- Side effects: none.

`persist_p0054m_price_rows(...)`

- Purpose: persist the train-side P0054M blocked out-of-fold advanced price table.
- Inputs: feature DB path and forecast rows.
- Outputs: row count.
- Side effects: writes local SQLite table.

`build_p0054m_modeling_rows(...)`

- Purpose: build SE3 consumption modeling rows from P0054K-compatible helpers using P0054M price rows.
- Inputs: SE3 consumption rows, weather proxy rows and price rows.
- Outputs: direct and weekly modeling rows.
- Side effects: none.

`p0054m_feature_contract(...)`

- Purpose: define no-price and with-P0054L2-advanced-price feature sets.
- Inputs: none.
- Outputs: feature contract dictionary.
- Side effects: none.

`validate_p0054m_matrix_safety(...)`

- Purpose: verify paired rows, cutoff ordering, forbidden feature names and train/holdout price source separation.
- Inputs: modeling rows and feature contract.
- Outputs: leakage review dictionary.
- Side effects: none.

`write_p0054m_evidence(...)`

- Purpose: write Markdown/JSON/CSV evidence under `requirements/package-runs/P0054M/`.
- Inputs: summary and scored rows.
- Outputs: evidence path map.
- Side effects: writes package-run evidence.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Function Catalog

Update `docs/functions/mac/spotprice-model-diagnostics.md` after implementation.
