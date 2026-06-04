# P0053A implementation design

Package interpretation:

P0053A backfills ENTSO-E A09 scheduled commercial exchange and A11 physical flow for internal Swedish borders. It extends the existing P0052 transfer tables with historical observed exchange/flow signals, derives directional net and pressure features, joins them with P0051 physical balance and P0048/P0049 price/spread data, and writes package evidence. It intentionally excludes A61 capacity from requests and from derived features.

Implementation structure:

- Add `src/mac/services/spotprice_model_diagnostics/p0053a.py`.
- Reuse P0052A constants and XML parsing helpers where safe.
- Reuse P0052B schema extensions, idempotent persistence helpers and clipped parsing.
- Add P0053A-specific A09/A11 config filtering, monthly missing-chunk planning, net/pressure feature derivation, analysis table creation, validation, diagnostics and evidence writing.
- Add `tests/mac/services/spotprice_model_diagnostics/test_p0053a.py` for scope guards and derived feature behavior.

Intended changes:

- Ensure existing long transfer tables contain P0052B metadata columns.
- Ensure wide transfer table has A09/A11 directional columns from P0052A plus P0053A net/pressure columns.
- Fetch missing A09/A11 internal-border monthly chunks for the requested range.
- Persist raw/hourly rows idempotently into:
  - `transfer_capacity_flow_raw_v1`
  - `transfer_capacity_flow_hourly_v1`
- Rebuild/update A09/A11 wide values and P0053A derived columns for the target range in:
  - `transfer_capacity_flow_se1_se4_hourly_v1`
- Create or replace:
  - `physical_balance_flow_exchange_analysis_v1`
- Write required evidence under:
  - `requirements/package-runs/P0053A/`

Deliberate non-changes:

- Do not delete or reclassify existing A61 rows from earlier packages.
- Do not create or populate utilization/margin columns.
- Do not alter production forecasting, API, device, Home Assistant, KVS or Shelly artifacts.
- Do not introduce continental price features or SE1-to-SE3 anchoring.

Test strategy:

- Unit tests cover A09/A11-only configs, no A61 request generation, token-safe source contracts, timestamp normalization, net directional formula, pressure formulas, analysis table creation on `Z`/`+00:00` mixed timestamps and explicit absence of utilization/margin-derived P0053A columns.
- Package verification runs P0053A unit tests, relevant existing P0052A/P0052B/P0052C tests and `git diff --check`.
- Live verification checks token safety, coverage, duplicate keys, finite values, row counts, joined analysis rows and forbidden-scope scans.

Risks and uncertainties:

- ENTSO-E may omit historical chunks or rate-limit requests. The implementation records failed safe metadata only and uses the package WARN threshold if full history is incomplete.
- Existing local DB already contains P0052B A09/A11 rows from `2024-09-01` onward; P0053A must not infer completeness outside measured coverage.
- Existing wide table has older capacity/utilization columns from P0052/P0052B; P0053A evidence must distinguish pre-existing columns from features this package creates or populates.
