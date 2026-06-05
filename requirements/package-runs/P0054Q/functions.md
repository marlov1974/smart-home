# P0054Q Function Design

## New Functions

`run_p0054q_analysis(...)`

- Purpose: orchestrate corrected-target loading, feature construction, model training/evaluation and evidence writing.
- Inputs: feature DB path, weather DB path, evidence directory.
- Outputs: `P0054QResult`.
- Side effects: writes package-run evidence only.
- Tests: package command.

`load_entsoe_se3_target_rows(...)`

- Purpose: load P0054P2 SE3 actual-load rows and normalize to P0054K-compatible in-memory target fields.
- Inputs: feature DB path.
- Outputs: list of target rows.
- Side effects: none.
- Tests: unit test with in-memory SQLite.

`validate_entsoe_target_contract(...)`

- Purpose: prove the corrected target source is ENTSO-E actual total load and not old physical balance.
- Inputs: target rows.
- Outputs: source contract summary.
- Side effects: none.
- Tests: unit test.

`p0054q_feature_contract(...)`

- Purpose: expose no-price and with-advanced-price feature groups reused from P0054N.
- Inputs: none.
- Outputs: feature contract.
- Side effects: none.
- Tests: leakage/unit review.

`validate_p0054q_leakage(...)`

- Purpose: verify target/source/feature matrix safety for corrected target.
- Inputs: modeling rows, feature contract, target contract and fairness.
- Outputs: leakage review.
- Side effects: none.
- Tests: unit test rejects old target references.

`target_sanity_metrics(...)`

- Purpose: report corrected SE3 target mean/median and daily energy against P0054P2 scale.
- Inputs: target/source rows and DayAhead selected rows.
- Outputs: sanity metrics.
- Side effects: none.
- Tests: helper unit test.

`add_percent_metrics(...)`

- Purpose: add MAE percent of mean/median actual to full_36h and DayAhead metric summaries.
- Inputs: summary dictionaries.
- Outputs: updated summary dictionaries.
- Side effects: mutates local summary objects only.
- Tests: unit test.

`model_comparison(...)`

- Purpose: pick best corrected-target full_36h, DayAhead and daily-energy models.
- Inputs: full_36h summary, DayAhead summary, daily energy summary.
- Outputs: comparison summary.
- Side effects: none.
- Tests: package evidence.

`write_p0054q_evidence(...)`

- Purpose: write required Markdown/JSON/CSV evidence.
- Inputs: summary and compact metric rows.
- Outputs: evidence path map.
- Side effects: package-run file writes.
- Tests: package command.

## Changed Functions

None planned.

## Removed Functions

None planned.

## Durable Docs

Update `docs/functions/mac/spotprice-model-diagnostics.md` for P0054Q.
