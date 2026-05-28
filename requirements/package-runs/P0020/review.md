# Package P0020 Review Evidence

## Package

`P0020`

## Consistency result

PASS

## Files checked

- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `requirements/packages/P0020-mac-weekly-home-poc-browser-ui.md`
- `requirements/packages/P0018-mac-weekly-heat-ppm-rh-poc.md`
- `memory/device-management/mac-layer.md`
- `memory/physical/ftx/airflow.md`
- `memory/planning/weekly-heat-ppm-rh-poc.md`
- `src/mac/labs/weekly_home_optimizer_poc/**`
- `tests/mac/weekly_home_optimizer_poc/**`
- `docs/functions/mac/weekly-home-optimizer-poc.md`
- `git status --short --branch`

## Checks

### Package vs memory

Consistent. Mac layer memory allows Mac services, POC experiments and diagnostics using Python standard library. P0020 is read-only local lab tooling and does not change runtime responsibilities.

### Package vs linked requirements

Linked requirements are TBD in the package, but the package contains sufficient browser/API requirements.

### Package vs previous packages

Consistent with P0018. P0018 exposes `build_weekly_plan()` and `rows_for_plan()`, which are sufficient for server HTML and JSON output without duplicating optimizer logic.

### Package vs implementation/deploy structure

Consistent. The existing P0018 lab package is the right location for `server.py` and `html.py`. No deploy artifact is required.

### Package vs G1/G2 boundary

Consistent. G1 is not touched and no current G1 runtime behavior is changed.

### Package vs invariants

Consistent. The server can bind to `127.0.0.1` by default, use port `8081`, avoid external dependencies/CDNs, and remain side-effect-free beyond local POC calculation.

### Package vs testability and rollback

Testable using standard-library HTTP server in a background test thread bound to `127.0.0.1` and an ephemeral port. Rollback is a future package or simply not running the server.

### Chat-only assumptions

No chat-only assumptions are required.

## Decision

Continue.

## Notes for human/ChatGPT review

The implementation will add a deterministic `--once-smoke` command so verification does not require leaving a blocking server process running.
