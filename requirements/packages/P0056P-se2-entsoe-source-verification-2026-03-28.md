# Package P0056P: SE2 ENTSO-E source verification for 2026-03-28 anomaly

## Status

planned

## Package order

P0056P

## Primary area

G2 / Mac / Energy-market AI LABB / data-source verification

## Label

```text
LABB
SOURCE-AUDIT
```

This package is LABB-only. It is not G2-KANDIDAT and must not create deployable runtime behavior.

## Linked requirements

Epic:
- E____

Features:
- F____

User stories:
- US____

## Decision summary

P0056M found a severe SE2 DayAhead forecast miss on `2026-03-28`:

```text
delivery day: 2026-03-28
mean actual: about 5487.6 MW
mean forecast: about 1800.4 MW
hourly MAE: about 3708.6 MW
neighboring days: about 1800..2200 MW
```

P0056N classified `2026-03-28` as a probable target/source anomaly because the spike is already visible in local native source rows, while native source coverage is incomplete:

```text
expected native 15-minute rows: 96
observed native 15-minute rows: 94
partial hourly rows: 2
```

Before using this day for model selection, error-slice conclusions, regime/deviation modeling or decomposed normal+deviation forecast work, the project must verify whether the SE2 `2026-03-28` spike exists in fresh/original ENTSO-E Actual Total Load source data.

## Solution model

P0056P is a source-verification package.

It must compare three layers for SE2 around the suspicious delivery day:

```text
fresh/original ENTSO-E Actual Total Load
→ local native ingestion table
→ local hourly aggregation table
```

The package must answer:

```text
Does the 7279 MW / extreme-load spike exist in fresh/original ENTSO-E?
Is the whole local delivery day genuinely extremely high?
Are native 15-minute rows missing, duplicated or malformed?
Is the ENTSO-E request contract correct?
Is local hourly aggregation correct?
```

The package must produce evidence sufficient for a follow-up decision:

```text
A. local import/cache/aggregation bug
B. ENTSO-E source-observed anomaly
C. independently plausible/confirmed real load regime
D. unresolved; exclude from model selection until verified elsewhere
```

## Current behavior

The current realistic DayAhead consumption forecast truth is:

```text
P0056K realistic DayAhead protocol
+
P0056O DST-canonical delivery-day generation
```

P0056K uses:

```text
forecast_origin = D-1 12:00 Europe/Stockholm
delivery_day = D local delivery day
```

P0056O fixed the separate DST bug and established canonical true local delivery-day rows:

```text
normal day = 24 rows
spring-forward day = 23 rows
fall-back day = 25 rows
```

P0056O did not retrain models and did not change the P0056N classification that `2026-03-28` remains a probable target/source anomaly.

## Problem

The SE2 `2026-03-28` target value is too extreme to use blindly.

If it is a local ingestion/cache/aggregation bug, including it in model evaluation or model selection will corrupt conclusions.

If it is present in fresh ENTSO-E source data but not independently verified, it should be treated as a source-observed anomaly and excluded or specially flagged until a separate independent-source package confirms it.

If it is real, it is an important high-load/regime event and should inform the future decomposed normal+deviation model.

## Target behavior

After P0056P, the repository must contain a clear decision on `2026-03-28`:

```text
verified_local_bug
source_observed_anomaly
independently_plausible_real_regime
unresolved_exclude_from_selection
```

The package must preserve compact evidence showing:

```text
fresh ENTSO-E native rows
local native rows
local hourly rows
row counts
missing/duplicate timestamps
extreme values
hourly aggregation comparison
request metadata
sanitized source metadata
decision
```

## Non-goals

- No new consumption model.
- No model retraining.
- No model selection.
- No decomposed normal+deviation model implementation.
- No spot-price feature work.
- No flow/exchange/A61/capacity feature work.
- No production runtime.
- No Home Assistant changes.
- No Shelly/device/KVS changes.
- No G2-KANDIDAT promotion.
- No use of uploaded cross-border physical-flow CSV unless a later package explicitly asks for flow/capacity work.
- No large raw source dumps committed.

## Invariants

- This is LABB-only source verification.
- Fresh ENTSO-E calls must be token-safe.
- ENTSO-E token values must never be written to evidence, logs or committed files.
- Only Actual Total Load for SE2 may be fetched unless the design explicitly justifies small neighboring-area sanity checks.
- Do not use A09, A11, A61, flow, exchange, capacity, utilization, production or price features.
- Do not change historical package evidence from P0056K/P0056M/P0056N/P0056O.
- Do not rewrite old results to hide bad rows.
- If evidence is uncertain, prefer flag/exclude over forcing the day into model selection.

## Data scope

Primary area:

```text
SE2
```

Primary local delivery day:

```text
2026-03-28 Europe/Stockholm
```

Required comparison window:

```text
2026-03-27 .. 2026-03-30 Europe/Stockholm
```

Optional broader context window if useful and compact:

```text
2026-03-25 .. 2026-03-31 Europe/Stockholm
```

Required source contract:

```text
ENTSO-E Transparency Platform
Actual Total Load
documentType A65 / processType A16 if matching existing P0054P2 ingestion contract
outBiddingZone_Domain = SE2 bidding-zone EIC
unit normalized to MW
native resolution preserved before hourly aggregation
```

Codex must verify the exact EIC and request parameters from existing P0054P2/P0056A source code or package evidence before making fresh requests.

## Knowledge updates

Create or update:

```text
requirements/package-runs/P0056P/CHANGELOG.md
requirements/package-runs/P0056P/review.md
requirements/package-runs/P0056P/design.md
requirements/package-runs/P0056P/functions.md
requirements/package-runs/P0056P/source-contract.md
requirements/package-runs/P0056P/fresh-entsoe-fetch.md
requirements/package-runs/P0056P/local-native-comparison.md
requirements/package-runs/P0056P/hourly-aggregation-comparison.md
requirements/package-runs/P0056P/decision.md
requirements/package-runs/P0056P/what-we-learned.md
requirements/package-runs/P0056P/next-package-recommendation.md
```

Optional compact evidence files:

```text
requirements/package-runs/P0056P/se2-2026-03-28-native-comparison.csv
requirements/package-runs/P0056P/se2-2026-03-28-hourly-comparison.csv
requirements/package-runs/P0056P/metrics-summary.json
```

Do not commit large raw XML/API payloads. Store compact normalized evidence only.

## Implementation updates

Allowed implementation is limited to Mac-side source verification tooling and tests.

Expected implementation shape:

```text
src/mac/services/spotprice_model_diagnostics/p0056p.py
tests/mac/test_p0056p_se2_entsoe_source_verification.py
```

The implementation may reuse existing ENTSO-E ingestion helpers from P0054P2/P0056A if safe and package-scoped.

If reusable helpers are changed, Codex must document the function-level change in `requirements/package-runs/P0056P/functions.md` and update durable function docs only if the behavior matters across future packages.

## Files to inspect

```text
memory/energy-market-ai-lab.md
memory/spotprice-forecast-period-policy.md
memory/chat-handoffs/2026-06-09-energy-market-ai-lab-handoff-short.md

docs/functions/mac/spotprice-model-diagnostics.md

requirements/package-runs/P0056K/CHANGELOG.md
requirements/package-runs/P0056K/dayahead-protocol.md
requirements/package-runs/P0056M/CHANGELOG.md
requirements/package-runs/P0056M/hour-level-summary.md
requirements/package-runs/P0056N/classification.md
requirements/package-runs/P0056N/dst-local-day-audit.md
requirements/package-runs/P0056N/forecast-row-alignment-audit.md
requirements/package-runs/P0056N/decision.md
requirements/package-runs/P0056O/CHANGELOG.md
requirements/package-runs/P0056O/decision.md

src/mac/services/spotprice_model_diagnostics/**
tests/mac/**
local SQLite schema/table definitions for:
  area_consumption_native_v1
  area_consumption_hourly_v1
  entsoe_consumption_area_hourly_v1
```

If exact table names differ, Codex must document the actual discovered table names in design and evidence.

## Files allowed to change

```text
requirements/packages/P0056P-se2-entsoe-source-verification-2026-03-28.md
requirements/package-runs/P0056P/**
src/mac/services/spotprice_model_diagnostics/p0056p.py
tests/mac/test_p0056p_se2_entsoe_source_verification.py
docs/functions/mac/spotprice-model-diagnostics.md
```

Only if strictly necessary:

```text
src/mac/services/spotprice_model_diagnostics/<shared_entsoe_helper>.py
tests/mac/<shared_entsoe_helper_test>.py
```

## Forbidden changes

```text
No Shelly changes.
No Home Assistant changes.
No device/runtime writes.
No production deployment.
No G2-KANDIDAT promotion.
No model retraining.
No model binaries.
No model selection changes.
No decomposed forecast implementation.
No spot-price feature additions.
No flow/exchange/A61/capacity/utilization features.
No production forecast API.
No Nord Pool integration.
No workplace integration.
No old physical_balance target revival.
No changes to P0056K/P0056M/P0056N/P0056O historical evidence.
No result rewriting to hide bad rows.
No token values in logs/evidence.
No large raw API dumps.
No uploaded cross-border physical-flow CSV processing.
```

## Pre-implementation consistency review

Before editing, Codex must classify the package:

```text
PASS
WARN
STOP
```

PASS requires:

```text
- Existing P0056N anomaly evidence can be found.
- Existing P0054P2/P0056A ENTSO-E Actual Total Load ingestion contract can be found.
- SE2 EIC/request parameters can be verified.
- Required local tables can be identified or absence can be documented safely.
- Fresh ENTSO-E token-safe access is available or a fallback original-source read path is available.
```

WARN is acceptable if:

```text
- Fresh ENTSO-E fetch cannot be performed, but original locally cached raw/source rows are available and can be compared.
- Independent external confirmation is not available, but source-observed anomaly decision can still be made.
```

STOP if:

```text
- SE2 EIC/request contract cannot be verified.
- No source path exists to compare against local native/hourly rows.
- Token-safe fetch would expose secrets.
- Implementation would require broad ingestion rewrite.
- The package would need model retraining or forbidden feature work.
```

Store review in:

```text
requirements/package-runs/P0056P/review.md
```

## Implementation design policy

Codex must write:

```text
requirements/package-runs/P0056P/design.md
```

The design must include:

```text
- P0056N baseline anomaly summary
- ENTSO-E Actual Total Load request contract
- SE2 EIC and timezone handling
- source window and local delivery-day boundaries
- fresh/original source fetch/read plan
- local native table read plan
- local hourly table read plan
- aggregation comparison method
- token/secret safety plan
- compact evidence plan
- decision classification logic
```

## Function design policy

Codex must write:

```text
requirements/package-runs/P0056P/functions.md
```

Expected new functions may include:

```text
run_p0056p_source_verification(...)
build_p0056p_entsoe_request(...)
load_fresh_entsoe_actual_load_rows(...)
load_local_native_area_rows(...)
load_local_hourly_area_rows(...)
aggregate_native_to_hourly_for_audit(...)
compare_native_rows(...)
compare_hourly_rows(...)
classify_2026_03_28_anomaly(...)
write_p0056p_evidence(...)
```

Exact names may differ, but function purpose, inputs, outputs, side effects and tests must be documented before implementation.

## Live/API policy

External API calls allowed:

```text
yes, ENTSO-E Actual Total Load only
```

Live device testing allowed:

```text
no
```

Live write actions allowed:

```text
no
```

Database writes allowed:

```text
yes, package-run evidence only
```

Local research DB writes allowed:

```text
no, unless design justifies a package-scoped temporary audit table and it is not treated as canonical source truth
```

Secret handling:

```text
- read token only from existing approved local token path or ENTSOE_SECURITY_TOKEN
- never print token
- never write token to evidence
- record only sanitized token-source metadata
```

## Test cases

### TC1: ENTSO-E request contract is Actual Total Load only

Given P0056P builds an ENTSO-E request
When request parameters are inspected
Then it uses the existing Actual Total Load contract for SE2 and does not request A09/A11/A61, flow, exchange, capacity, utilization, production or price data.

### TC2: Token safety

Given token-based ENTSO-E fetch is available
When P0056P writes evidence
Then no token value or bearer/security token field appears in any evidence file.

### TC3: Fresh/native row count comparison

Given fresh/original ENTSO-E native rows and local native rows for SE2 around `2026-03-28`
When P0056P compares them
Then it reports row counts, missing timestamps, duplicate timestamps, native resolution, min/max/mean MW and extreme values.

### TC4: Hourly aggregation comparison

Given fresh/original native rows and local hourly rows
When P0056P aggregates native rows to hourly mean MW
Then each comparable hour is checked against local hourly values with tolerances documented in design.

### TC5: Spike existence classification

Given the suspicious SE2 `2026-03-28` values
When P0056P classifies the anomaly
Then it emits exactly one primary classification:

```text
verified_local_bug
source_observed_anomaly
independently_plausible_real_regime
unresolved_exclude_from_selection
```

### TC6: Partial native coverage is reported

Given `2026-03-28` has missing or partial native rows
When P0056P writes evidence
Then it reports expected vs observed native row count, partial hourly rows and their timestamps.

### TC7: No model/runtime side effects

Given the package runs
When reviewing changed files and evidence
Then no model training, model binaries, runtime changes, device calls, Home Assistant changes, Shelly/KVS writes or production artifacts exist.

## Verification commands

Codex must define final commands in `design.md`, but must run equivalents of:

```bash
python3 -m unittest discover tests/mac
python3 -m src.mac.services.spotprice_model_diagnostics.p0056p \
  --area SE2 \
  --start-local-date 2026-03-27 \
  --end-local-date 2026-03-30 \
  --write-evidence requirements/package-runs/P0056P
git diff --check
```

If fresh ENTSO-E API fetch cannot run in the environment, Codex must run the strongest available original/local-source comparison command and classify the result as WARN or STOP according to this package.

## Evidence requirements

`fresh-entsoe-fetch.md` must include:

```text
- sanitized request contract
- area
- EIC
- source window
- source system
- response row count
- native resolution
- no-token-leak confirmation
```

`local-native-comparison.md` must include:

```text
- local native table name
- local row count
- expected native row count
- missing timestamps
- duplicate timestamps
- min/max/mean MW
- whether 7279 MW or equivalent spike exists locally
```

`hourly-aggregation-comparison.md` must include:

```text
- local hourly table name
- fresh/original aggregated hourly rows
- local hourly rows
- max absolute difference
- hours differing beyond tolerance
- partial hourly rows
```

`decision.md` must include an explicit JSON decision object similar to:

```json
{
  "area": "SE2",
  "delivery_date_local": "2026-03-28",
  "classification": "<one of required classifications>",
  "fresh_entsoe_has_spike": true,
  "local_native_has_spike": true,
  "local_hourly_has_spike": true,
  "native_rows_expected": 96,
  "native_rows_observed": 94,
  "hourly_aggregation_ok": false,
  "model_selection_action": "exclude_until_independently_verified",
  "recommended_next_package": "..."
}
```

Fields may be adjusted to match evidence, but the classification and model-selection action must be explicit.

## Decision logic

Use this decision table:

```text
If fresh/original ENTSO-E lacks the spike
and local native/hourly has the spike:
  classification = verified_local_bug
  action = fix ingestion/cache/aggregation before modeling

If fresh/original ENTSO-E has the spike
and local native/hourly matches it:
  classification = source_observed_anomaly
  action = flag/exclude from model selection until independently verified

If fresh/original ENTSO-E has the spike
and independent source or later package confirms plausible real load:
  classification = independently_plausible_real_regime
  action = include only with explicit regime/deviation handling

If source access or evidence is insufficient:
  classification = unresolved_exclude_from_selection
  action = exclude from model selection and create follow-up source package
```

## Runtime health checks

Not applicable. No live devices or runtime systems are touched.

## Deployment plan

No deployment.

Commit only package requirements, package-run evidence, source-audit helper code/tests if implemented, and function-catalog update if needed.

## Rollback plan

Rollback is a new forward-moving package. Do not rewrite P0056P evidence if later verification changes the decision; create a follow-up package that supersedes the classification.

## Expected Codex output

Codex must report:

```text
PASS/WARN/STOP review
commit SHA
files changed
tests/commands run
ENTSO-E request contract used
SE2 EIC used
fresh/original source availability
native row count comparison
hourly aggregation comparison
2026-03-28 classification
model-selection action
whether 7279 MW spike exists in fresh/original ENTSO-E
whether 15-minute rows are missing/duplicated
whether hourly aggregation is correct
confirmation no token leaked
confirmation no model/runtime/device/production changes
recommended next package
```

## Completion notes

To be filled after implementation.
