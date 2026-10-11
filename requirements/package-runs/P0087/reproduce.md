# Reproduction

From G2 root, stdlib Python3.14.7; no dependency download or device needed:

```sh
python3 -m unittest discover -s tools/ftc6/p87/tests -v
python3 -m compileall -q tools/ftc6/p87
python3 tools/ftc6/p87/scenarios.py /tmp/p87-scenarios.json
python3 tools/ftc6/p87/replay.py ../../P0080/effect-learning/down-up-20261009T204755Z/events.jsonl /tmp/p87-history.json
python3 tools/ftc6/p87/replay.py ../../P0080/effect-learning/capture-native6kw-20261010T153111Z/events.jsonl /tmp/p87-short-history.json
```

Replay inputs are private existing files; absent inputs cause an error, never a live fallback. Compare generated outputs byte-for-byte with checked-in sanitized JSON. No model CLI can actuate anything.60s replay-age policy is documented separately from unknown native sensor expiry.

For extraction, independently copy finalized `P0086/private/projects/fresh-a.gpr/.rep` to new P0087/private/projects/fresh-a and fresh-b project names, without overwriting existing copies. Use pinned P83 repaired decoder and original local image; wrapper paths assume G2 is P0080/implementation-smart-home under the workspace. Ghidra may require sandbox permission for local preferences.

```sh
python3 tools/ftc6/p87/run_analysis.py ../.. fresh-a
python3 tools/ftc6/p87/run_analysis.py ../.. fresh-b
python3 tools/ftc6/p87/verify_local.py ../../P0082/private/ftc6.bin ../../P0087/private/fresh-a ../../P0087/private/fresh-b /tmp/p87-extraction.json
```

Expected90 correct roots,273 matching files, actual table/operand checks. The initial runs used the same P83Seed/P83Trace command sequence; final wrapper merely removes an unused P86 proof option. Do not copy the exploratory work project or promote unsupported roots. Full exports stay private; extraction-verification.json contains only hashes and small relevant operand/table evidence.

Run `git diff --check`, `git diff --cached --check`, and ensure only P87 plus catalog/knowhow/index changes are staged. Generate REPOSITORY_FILES.md using the repository's generate script and staged path set. Native firmware build/live tests are NOT RUN: no production source or deployment changed.
