# P0026 attempts

## Attempt 1

- Status: completed
- Change summary: created the read-only Mac KVS.Get NAT helper, package-scoped tests, durable function docs and package evidence.
- Tests run:
  - `python3 -m unittest discover tests/mac/tools/local_kvs_read` failed first because the mocked `HTTPError` without an `fp` triggered a Python 3.9 tempfile-backed attribute edge case while reading an absent body.
  - Fixed HTTPError body handling to read only when `exc.fp` exists.
  - `python3 -m unittest discover tests/mac/tools/local_kvs_read` passed after fix.
  - `python3 -m unittest discover tests/mac/tools` passed after fix.
  - `python3 -m src.mac.tools.local_kvs_read get --octet 0 --key hp.price.status` returned validation exit code `2` without network access.
  - `git diff --check` passed.
- Live verification: skipped because no explicit octet/key was supplied for a read-only live KVS.Get.
- Result: implementation verified by unit tests and whitespace check.

## Follow-up live verification

- Status: completed
- Scope: read-only `KVS.Get` only.
- Command requested:

```bash
python3 -m src.mac.tools.local_kvs_read get --octet 30 --key hp.price.status --timeout 5
```

- Derived URL:

```text
http://192.168.86.240:8030/rpc/KVS.Get?key=hp.price.status
```

- First sandboxed run result:
  - Exit code: `1`
  - `result_status`: `network_error`
  - `audit_error`: `[Errno 1] Operation not permitted: '/Users/marcus.lovenstad/.smart-home'`
  - Interpretation: sandbox prevented default audit-path creation and local network access was not verified from the sandboxed run.
- Escalated read-only live run result:
  - Exit code: `0`
  - HTTP status: `200`
  - `result_status`: `success`
  - Result value: `"ok"`
  - Audit path: `/Users/marcus.lovenstad/.smart-home/local_kvs_read_audit.jsonl`
- Forbidden actions: no `KVS.Set`, no `Script.*`, no `Switch.*`, no `Light.*`, no `Cover.*`, no relay/dimmer/actuator calls, no generic HTTP proxy and no MCP server.
