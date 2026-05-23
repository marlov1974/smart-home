# Package P0010 Findings

## Finding 1: `unittest discover tests/mac/tools` initially found zero tests

Status: fixed inside P0010.

The repository had test files under nested directories without package marker files, so the required package-level command:

```bash
python3 -m unittest discover tests/mac/tools
```

initially reported zero tests. P0010 added `__init__.py` markers under the Mac test tree so the command discovers both Shelly build and live deploy tests.

## Finding 2: one-shot script logs need listener-first sequencing

Status: fixed inside P0010.

For an inert script that prints once, starting the script before opening `/debug/log` can miss the expected log line. The live tool now starts bounded log capture before issuing `Script.Start`.

## Finding 3: live test script should be stopped after verification

Status: fixed inside P0010.

The first successful live run left `hello_v1_0_0` installed and still reported as running. P0010 now stops only `hello_v1_0_0` after observing the expected log line, leaving it installed but stopped.
