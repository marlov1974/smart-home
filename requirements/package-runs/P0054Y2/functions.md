# P0054Y2 function design

Status: `PASS`

## New functions

`run_p0054y2_decomposition(...)`

Purpose: orchestrate DB schema creation, cluster assignment, hourly aggregation, residual construction, table writes and evidence generation.

Inputs: feature DB path and evidence directory.

Outputs: result object with status, row counts and evidence paths.

Side effects: writes P0054Y2 SQLite tables and package evidence.

Test coverage: integration run plus focused unit tests of helper functions.

`create_schema(conn)`

Purpose: create P0054Y2 output tables.

Inputs: SQLite connection.

Outputs: none.

Side effects: creates tables if missing.

`classify_mga_cluster(mga, feature)`

Purpose: assign a loaded MGA to one profiled/load-profile cluster using deterministic heuristics.

Inputs: masterdata/name/owner and load-shape feature summary.

Outputs: cluster metadata.

Side effects: none.

`aggregate_profiled_clusters(conn, assignments)`

Purpose: aggregate native 15m/60m P0054W energy rows to hourly positive MW-equivalent cluster rows.

Inputs: SQLite connection and cluster assignments.

Outputs: rows for `se3_profiled_mga_cluster_hourly_v1`.

Side effects: none.

`compute_residual_rows(cluster_rows, entsoe_rows)`

Purpose: compute residual rows and decomposition rows from profiled cluster sums and ENTSO-E SE3 total.

Inputs: cluster rows and ENTSO-E hourly rows.

Outputs: residual rows and decomposition rows.

Side effects: none.

`quality_summary(residual_rows)`

Purpose: compute required validation metrics and negative residual examples.

Inputs: residual rows.

Outputs: serializable summary dict.

Side effects: none.

`write_evidence(evidence_dir, summary)`

Purpose: write required P0054Y2 evidence and compact CSV/JSON outputs.

Inputs: evidence path and summary.

Outputs: mapping of evidence names to paths.

Side effects: writes package-run files.
