# P0052A attempts

## Attempt 1

Live ENTSO-E ingestion reached XML parsing and failed on an observed capacity resolution of `P1M`.

Result:

```text
ValueError: Unsupported ENTSO-E resolution: P1M
```

Fix:

```text
- Added period-bound based `P1M` handling.
- Filtered expanded source observations back to the requested UTC range.
- Added unit coverage for monthly resolution.
```

## Attempt 2

Live ENTSO-E ingestion completed.

Result:

```text
status = WARN
raw_rows = 20334
hourly_rows = 7795
wide_rows_updated = 599
```

No token value was printed or written to evidence.
