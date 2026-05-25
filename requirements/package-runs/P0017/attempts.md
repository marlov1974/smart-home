# P0017 Attempts and Verification

## Attempt 1

Implemented the Mac spot forecast service, model helpers, HTTP handler, CLI, unit tests and function catalog entry.

Initial unit test run found two test-harness issues:

- In-process socket binding with `HTTPServer(("127.0.0.1", 0), ...)` is blocked by the default sandbox.
- The standard-library import allowlist test did not allow local `src` package imports.

Fix:

- Reworked API unit tests to call the generated handler directly without opening a listening socket.
- Updated the import allowlist to permit local package imports while still rejecting non-standard external imports.

## Verification

Commands run:

```bash
python3 -m unittest discover tests/mac/spot_forecast
python3 src/mac/services/spot_forecast/server.py --once --week 2
python3 src/mac/services/spot_forecast/server.py --once --week 25
python3 src/mac/services/spot_forecast/server.py --host 127.0.0.1 --port 8765
python3 -m unittest discover tests/mac
git diff --check
```

Results:

- `python3 -m unittest discover tests/mac/spot_forecast`: PASS, 16 tests.
- `python3 src/mac/services/spot_forecast/server.py --once --week 2`: PASS, returned 21-number compact JSON array.
- `python3 src/mac/services/spot_forecast/server.py --once --week 25`: expected non-zero exit code 3 with `{"error":"week not found"}`.
- Local HTTP service check on `127.0.0.1:8765`: PASS with week 2 HTTP 200, invalid week HTTP 400, week 25 HTTP 404.
- `python3 -m unittest discover tests/mac`: PASS, 74 tests.
- `git diff --check`: PASS.

## Local Service Observations

HTTP responses observed during local service check:

```text
/spot/period-index?week=2   200 [1.08,0.83,0.47,0.7,0.75,0.77,1.32,1.46,0.84,1.89,2.12,1.19,2.05,1.81,0.53,0.48,0.53,0.52,0.47,0.49,0.7]
/spot/period-index?week=abc 400 {"error":"invalid week"}
/spot/period-index?week=25  404 {"error":"week not found"}
```

## Live Actions

No live Shelly actions were performed. P0017 live testing is not allowed and not required.

## Knowhow Promotion

Skipped. P0017 did not include live debugging, runtime anomalies, new Shelly/API discoveries, deploy/rollback lessons or repeated workflow problems. The sandboxed local socket restriction was package-specific test evidence and did not require a durable knowhow rule.
