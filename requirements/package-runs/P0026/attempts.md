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
