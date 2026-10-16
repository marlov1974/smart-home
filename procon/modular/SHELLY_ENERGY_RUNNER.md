# Four-quarter Shelly energy runner

The current production executor is 1.5.1. Its validation-only path completes
after identity, model, feedback and plan parsing even when newly booted firmware
has not yet produced a qualified power pair. Production execution still holds
on that stale feedback. Validation never seeds C077 or calls the EFFECT command
path.

`tools/run_shelly_energy.py` installs and supervises Script 7 without weakening
the existing read-only preflight or native restoration checks. Before runtime
validation or execution it writes `vp.energy.plan`, reads the key back and
requires an exact match. The previous key value, including an absent key, is
restored during cleanup when the runner's plan is still current. A newer value
written by L4 during the run is preserved instead of being overwritten.

The wire value is deliberately small and deterministic:

```text
v=1|rev=17|start=1800000000|q0=1500|q1=2000|q2=2500|q3=4000
```

`start` must be a Unix timestamp on a wall-clock 15-minute boundary. Each
quarter contains Wh and must be in `1500..6000`, corresponding to a pair demand
of `6..24 kW`. The command-line defaults are `1500 2000 2500 4000`; omitted
start uses the current quarter and omitted revision uses the current Unix
second.

Examples:

```sh
python3 tools/run_shelly_energy.py --validate-runtime \
  --quarter-wh 1500 2000 2500 4000

python3 tools/run_shelly_energy.py --execute \
  --quarter-wh 1500 2000 2500 4000 \
  --evidence-name shelly-energy-four-quarter
```

The execution deadline is four 900-second quarters plus a 360-second cleanup
allowance. Evidence records the complete identity range `I72..I86` and the
effect-model diagnostics `I308..I319` plus seed sequence `I346` for both
devices. The original native mode is still compared after restoration, and
Script 7 is stopped and disabled on every cleanup path.

Run the focused offline checks with:

```sh
python3 tests/test_run_shelly_energy.py
```
