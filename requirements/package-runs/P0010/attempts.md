# Package P0010 Attempts

## Package

`P0010`

## Attempt 1

Change summary:
- Added `src/mac/tools/shelly_live` Mac-side live deploy/log tooling.
- Added a hard `hello_v1_0_0` script-name boundary for create, upload, start, stop and delete operations.
- Renamed the fixture build role to `hello_v1_0_0`.
- Added unit tests for RPC request construction, script-name rejection, deploy orchestration, log capture and stdlib-only imports.
- Rebuilt generated fixture artifacts for `hello_v1_0_0`.

Tests run:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello_v1_0_0
```

Live command:

```bash
python3 -m src.mac.tools.shelly_live deploy-hello --base-url http://192.168.86.240:8030/ --script build/shelly/fixture/hello_v1_0_0.js --expect hello --log-timeout 20
```

Result:
- Local tests passed.
- Build and validate passed.
- First sandboxed live command failed with `Operation not permitted`, then passed after explicit network escalation.
- Live log contained `hello world`.
- Follow-up live run showed `before_scripts` with `hello_v1_0_0` still running, so the tool was updated to stop only `hello_v1_0_0` after successful log verification.

## Attempt 2

Change summary:
- Started bounded log capture before `Script.Start` to avoid missing one-shot print output.
- Stopped only `hello_v1_0_0` after successful log verification.
- Printed before/after script list evidence from the CLI.

Tests run:

```bash
python3 -m unittest discover tests/mac/tools
python3 -m src.mac.tools.shelly_live deploy-hello --base-url http://192.168.86.240:8030/ --script build/shelly/fixture/hello_v1_0_0.js --expect hello --log-timeout 20
```

Result:
- Passed.
- Final live status showed `hello_v1_0_0` installed and not running.
- Full live evidence is stored in `requirements/package-runs/P0010/logs/live-dampers-hello.md`.

## Live Runtime

Run on dampers only:

```text
target=http://192.168.86.240:8030
script=hello_v1_0_0
```

No cleanup was requested. The inert `hello_v1_0_0` script was left installed and stopped.
