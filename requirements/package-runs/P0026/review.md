# P0026 consistency review

## Result

WARN

P0026 is implementable and inside the documented Mac tooling scope. The only material ambiguity is the `80xx` wording combined with required octet validation for `1..254`. Existing repository examples and device registry entries use two-digit octets, but the package requires the full valid host-octet range. The implementation will therefore interpret the NAT port as:

```text
external port = 8000 + octet
```

This preserves all documented examples:

```text
30 -> 8030
40 -> 8040
```

and also keeps octets `100..254` valid without constructing impossible five-digit ports.

## Checks

- `memory/infrastructure/router-nat.md` documents operator host `192.168.86.240` and NAT convention `external port = 80xx`, with `192.168.77.40 -> http://192.168.86.240:8040/`.
- `memory/infrastructure/devices.md` lists the same NAT pattern for known devices.
- `memory/infrastructure/network.md` says user-facing troubleshooting should normally use NAT URLs.
- `memory/device-management/mac-layer.md` allows Mac diagnostics/live-device probes and requires endpoint separation from durable device identity.
- P0026 is read-only and does not require live writes.
- Proposed files stay inside `src/mac/tools/local_kvs_read/**`, `tests/mac/tools/local_kvs_read/**`, `docs/functions/mac/local-kvs-read-poc.md`, `docs/functions/00-index.md`, and `requirements/package-runs/P0026/**`.

## Decision

Continue implementation with the documented port interpretation and without optional live verification unless an explicit octet/key is supplied.
