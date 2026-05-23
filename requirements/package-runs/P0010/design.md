# Package P0010 Implementation Design

## Package Interpretation

P0010 adds Mac-side Python standard-library tooling for a bounded live deploy/start/log verification loop against the dampers Shelly device. The only script name the tool may create, update, start, stop or delete is `hello_v1_0_0`.

The fixture source remains inert and only prints `hello ...`. The build manifest will produce a built script named `hello_v1_0_0` so the live upload uses the same semantic versioned script name required by the package.

## Implementation Structure

Create a new tool package:

```text
src/mac/tools/shelly_live/
  __init__.py
  __main__.py
  core.py
```

The tool will use Shelly Gen2 JSON-RPC over HTTP POST to `/rpc` for script lifecycle calls and bounded HTTP GET to `/debug/log` for log capture.

CLI shape:

```text
python3 -m src.mac.tools.shelly_live deploy-hello \
  --base-url http://192.168.86.240:8030/ \
  --script build/shelly/fixture/hello_v1_0_0.js \
  --expect hello \
  --log-timeout 20
```

Optional cleanup:

```text
--cleanup
```

After successful log verification, the tool stops only `hello_v1_0_0` and leaves it installed as harmless test evidence. If `--cleanup` is supplied, the tool then deletes only `hello_v1_0_0`.

## Intended Changes

- Change `src/shelly/fixture/manifest.json` role from `hello` to `hello_v1_0_0`.
- Rebuild generated fixture artifacts under:
  - `build/shelly/fixture/hello_v1_0_0.js`
  - `dep/s/ch/hello_v1_0_0/**`
  - `dep/s/rec/hello_v1_0_0.json`
- Remove stale generated `hello` artifacts if the role rename makes them obsolete.
- Add `src/mac/tools/shelly_live/**`.
- Add `tests/mac/tools/shelly_live/test_core.py`.
- Update build tests for the new fixture role.
- Add `docs/functions/mac/shelly-live-deploy-tool.md`.
- Update `docs/functions/mac/shelly-build-tool.md` only where tests or fixture role references need current-state alignment.
- Store live evidence under `requirements/package-runs/P0010/attempts.md` and `requirements/package-runs/P0010/logs/`.
- Fill P0010 completion notes after verification.

## Safety Model

The live tool will hard-code the allowed script name:

```text
hello_v1_0_0
```

The implementation will reject any other script name before issuing write/start/stop/delete RPCs.

The tool will not contain RPC methods for switch, relay, cover, component, Wi-Fi, network, MQTT, Bluetooth, cloud, KVS, config or actuator changes.

## Refactoring Decisions

No changes to the existing Shelly build tool architecture are needed beyond fixture role/test alignment. The live deploy tool is separate because it owns live HTTP/RPC behavior and safety checks, while `shelly_build` owns deterministic source/build/deploy artifact generation.

## Test Strategy

Local verification:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello_v1_0_0
git diff --check
```

Live verification:

```bash
python3 -m src.mac.tools.shelly_live deploy-hello --base-url http://192.168.86.240:8030/ --script build/shelly/fixture/hello_v1_0_0.js --expect hello --log-timeout 20
```

Record the exact command, endpoint, script status before/after, deploy/start responses and bounded log excerpt under `requirements/package-runs/P0010/`.

## Risks And Uncertainties

- The dampers device may be unavailable from the current network. If so, stop after local verification and record the failed live attempt.
- Shelly debug log streaming behavior may differ by firmware. The tool will use a bounded timeout and treat missing expected text as a clear failure.
- Existing `hello` generated artifacts may need removal after the fixture role rename to avoid stale deploy artifacts.
