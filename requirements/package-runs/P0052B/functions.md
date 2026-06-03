# P0052B function design

## New functions

`run_p0052b_ingestion(feature_db=..., evidence_dir=..., windows=None)`

- Purpose: orchestrate token safety, schema migration, ENTSO-E backfill, validation, diagnostics and evidence writing.
- Inputs: feature DB path, evidence directory and optional UTC windows.
- Outputs: package result dataclass/status dictionary.
- Side effects: writes local SQLite rows and package evidence.
- Test coverage: live verification plus unit tests for subfunctions.

`capacity_concept_review()`

- Purpose: return documented A61 A02/A03/A04 concept metadata and conservative suitability status.
- Inputs: none.
- Outputs: dictionary/rows with meaning, directional status, utilization suitability and source notes.
- Side effects: none.
- Test coverage: contract type mapping test.

`ensure_p0052b_schema(conn)`

- Purpose: add P0052B metadata columns and required wide columns without dropping existing data.
- Inputs: SQLite connection.
- Outputs: schema-change summary.
- Side effects: `ALTER TABLE` statements.
- Test coverage: in-memory schema migration test.

`metadata_for_config(config, request_meta, response_meta=None)`

- Purpose: derive document/process/business/contract/curve/resolution/concept metadata for source rows.
- Inputs: document config, sanitized request metadata and optional parsed response metadata.
- Outputs: metadata dictionary.
- Side effects: none.
- Test coverage: metadata enrichment test.

`fetch_entsoe_rows_for_windows(token, windows, configs)`

- Purpose: fetch configured ENTSO-E documents over safe chunks and return rows plus sanitized response summaries.
- Inputs: token, window list and document configs.
- Outputs: raw rows and source-contract summaries.
- Side effects: HTTPS read only.
- Test coverage: parser/unit coverage plus live verification.

`chunk_windows(start, end, max_days)`

- Purpose: split historical ranges into API-safe chunks.
- Inputs: UTC start/end and day limit.
- Outputs: list of UTC start/end tuples.
- Side effects: none.
- Test coverage: chunk boundary test.

`persist_entsoe_rows_p0052b(conn, raw_rows, hourly_rows)`

- Purpose: idempotently insert metadata-enriched raw and hourly rows.
- Inputs: SQLite connection and row lists.
- Outputs: insert/upsert summary.
- Side effects: SQLite upserts.
- Test coverage: idempotent insert test.

`update_wide_entsoe_features_p0052b(conn, hourly_rows, concept_review)`

- Purpose: insert missing wide timestamp rows and update scheduled exchange, physical flow and capacity columns.
- Inputs: SQLite connection, hourly rows and concept review.
- Outputs: updated/inserted row summary.
- Side effects: SQLite insert/update.
- Test coverage: wide row creation and one-row-per-timestamp tests.

`normalize_timestamp_sql(expr)`

- Purpose: produce SQLite expression that makes `Z` and `+00:00` timestamp strings joinable.
- Inputs: SQL expression string.
- Outputs: SQL expression string.
- Side effects: none.
- Test coverage: normalized join test.

`run_join_fix_analysis(conn)`

- Purpose: explain P0052A zero-row join and compute fixed overlap counts.
- Inputs: SQLite connection.
- Outputs: diagnosis dictionary.
- Side effects: none.
- Test coverage: synthetic `Z`/`+00:00` join test.

`run_p0052b_diagnostics(conn, concept_review)`

- Purpose: compute SE3 price / SE3-SE1 correlations for scheduled exchange and physical flow, and utilization/margin only if allowed.
- Inputs: SQLite connection and concept review.
- Outputs: diagnostics dictionary.
- Side effects: none.
- Test coverage: diagnostic shape test.

`validate_p0052b(conn, raw_rows, hourly_rows, source_contracts, secret_safety)`

- Purpose: validate token safety, duplicates, finite values, capacity non-negativity, coverage, joins and forbidden document types.
- Inputs: SQLite connection, rows, source summaries and secret safety.
- Outputs: validation dictionary.
- Side effects: none.
- Test coverage: validation helper tests.

`write_p0052b_evidence(evidence_dir, summary)`

- Purpose: write required Markdown/JSON evidence without secrets.
- Inputs: evidence directory and summary.
- Outputs: file path mapping.
- Side effects: writes package-run evidence.
- Test coverage: token scan after live verification.

## Changed functions

None in P0052A/P0052 planned initially. If a P0052A helper needs to be generalized, P0052B should wrap it locally instead of changing P0052A unless a bug fix is unavoidable.

## Removed functions

None.
