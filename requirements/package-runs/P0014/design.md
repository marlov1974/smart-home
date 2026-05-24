# P0014 Implementation Design

## Package Interpretation

P0014 adds a narrow Mac-side device-management tool for the dampers lab Shelly. The tool must plan, apply, verify, and rerun idempotently for exactly this baseline:

- device display name `ftx_dampers`
- switch channel name `dampers`
- restore output state after reboot enabled
- virtual number component `House Temp`

The tool must not identify the target by URL alone. It accepts a runtime `--base-url`, reads live identity, and verifies physical Shelly id `8813bfd99f54` before any live write.

## Target Device Confirmation

Repository facts:

- logical role: `ftx-dampers`
- stable LAN address: `192.168.77.30`
- physical Shelly id suffix: `8813bfd99f54`
- current operator NAT endpoint from memory: `http://192.168.86.240:8030/`

Live confirmation uses `Shelly.GetDeviceInfo`. The returned `id` must end with `8813bfd99f54` or equal it case-insensitively after normalizing separators/case. `Shelly.GetStatus`, `Sys.GetConfig`, `Switch.GetConfig?id=0`, and `Switch.GetStatus?id=0` are captured for state evidence.

## Runtime Access Endpoint Selection

The CLI requires `--base-url`. The implementation does not persist this endpoint as identity. Evidence may record the endpoint used for this run, alongside the stable LAN address and physical id.

## Shelly API/RPC Discovery

The implementation uses these RPC methods only:

- Read:
  - `Shelly.GetDeviceInfo`
  - `Shelly.GetStatus`
  - `Sys.GetConfig`
  - `Shelly.GetComponents` with `include=["config","status"]`
  - `Switch.GetConfig` with `id=0`
  - `Switch.GetStatus` with `id=0`
  - `Number.GetConfig` / `Number.GetStatus` for discovered `House Temp`
- Write:
  - `Sys.SetConfig` with `{"device":{"name":"ftx_dampers"}}`
  - `Switch.SetConfig` with `{"id":0,"config":{"name":"dampers"}}`
  - `Switch.SetConfig` with `{"id":0,"config":{"initial_state":"restore_last"}}`
  - `Virtual.Add` with type `number` and `House Temp` config
  - `Number.SetConfig` for an existing `House Temp` component whose config differs
  - `Number.Set` only immediately after creating a new `House Temp` component to set neutral value `21`

The write allowlist rejects any method outside that set. No `Switch.Set`, `Switch.Toggle`, relay, cover, or output-control RPC is used.

## Plan/Apply/Verify Model

The CLI supports:

- `plan`: read current state, validate target identity, print planned actions as JSON.
- `apply`: read current state, validate target identity, build a plan, apply allowlisted actions, read state again, verify target baseline, and print JSON evidence.
- `verify`: read current state and verify the baseline without writing.

The planner compares current config to target values. It emits zero actions when the baseline already matches.

## Restore-Output Read/Write/Readback Model

Shelly switch configuration exposes `initial_state`. For P0014, restore output state after reboot maps to:

```json
{"initial_state":"restore_last"}
```

The tool only reads and sets switch configuration. It does not toggle the output and does not reboot the device.

## House Temp Component Contract

The component is a virtual number:

- name: `House Temp`
- min: `10`
- max: `30`
- default value: `21`
- persisted: `true`
- UI unit: `C`
- UI step: `0.1`
- initial value after creation: `21`

Existing `House Temp` is accepted when it is a `number:<id>` component. If duplicate matching names exist, the tool stops before writing because it cannot unambiguously choose the component.

If the live device does not support virtual number components, the tool stops before creating it and reports the discovered API failure.

## Idempotency Model

After successful apply, a second `plan` or `apply` should report no actions. The tests cover this with fake live state and the live evidence must record a second idempotent run.

## Rollback/Cleanup Model

The tool records before-state summaries in evidence. If a wrong setting is applied, rollback can be performed by applying the previous `Sys`/`Switch`/`Number` values inside P0014 scope. The implementation does not automatically delete number components unless a later explicit cleanup package or unambiguous P0014 duplicate cleanup is required.

## Intended Files

Create:

- `src/mac/tools/shelly_device/`
- `tests/mac/tools/shelly_device/`
- `docs/functions/mac/shelly-device-management-tool.md`

Update:

- `docs/functions/00-index.md`
- `requirements/package-runs/P0014/attempts.md` after verification

No existing Shelly runtime source or deploy artifacts are changed.

## Test Strategy

Run:

```bash
python3 -m unittest discover tests/mac/tools
git diff --check
```

Live verification, if reachable:

```bash
python3 -m src.mac.tools.shelly_device plan --base-url http://192.168.86.240:8030
python3 -m src.mac.tools.shelly_device apply --base-url http://192.168.86.240:8030
python3 -m src.mac.tools.shelly_device apply --base-url http://192.168.86.240:8030
python3 -m src.mac.tools.shelly_device verify --base-url http://192.168.86.240:8030
```

## Risks and Uncertainties

- The live dampers firmware may not support virtual number components. If so, stop after evidence; do not substitute another component type.
- `initial_state="restore_last"` must be accepted by the target switch profile. If not, stop with evidence rather than toggling outputs or reboot-testing.
- The runtime endpoint may be unreachable from the current Mac environment; that blocks live apply but not unit testing.
