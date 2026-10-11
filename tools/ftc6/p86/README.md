# P0086 offline FTC6 qualification tools

Python standard library only; tested with Python 3.14.7. No pip dependencies or serial/network backend. The profile is explicitly static 20.01, not a connection profile for installed 21.00. `--execute` is deliberately rejected. No arbitrary command injection.

```sh
python3 tools/ftc6/p86/reader.py --help
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation read --address 0x400 --length 1
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation log --fixture tools/ftc6/p86/fixtures/log.json
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation energy --fixture tools/ftc6/p86/fixtures/energy.json
python3 -m unittest discover -s tools/ftc6/p86/tests -v
```

Default is dry-run. `--fixture` replays synthetic responses with elapsed times; no waiting or device access occurs. All bundled fixtures are fabricated test data, never physical observations. `--output` creates a new file exclusively; existing evidence cannot be overwritten. A failed response preserves the supplied raw fixture and returns nonzero. Request and total deadlines are finite; there are zero retries. Cancellation is modeled by `{"cancelled":true}`. Close silence is never reported as verified restoration.

A read uses one bounded block and includes open/close in the plan. The 0400 example demonstrates encoding only; no expected 21.00 value is known. Flash and aliases are blocked. The normal 8N2 profile rejects diagnostic packets; `normal52()` documents address mapping but does not generate unqualified normal traffic. Log reading drains the firmware ring and omits the original CN105 checksum. Do not treat replay success as live compatibility.

`energy.py` exposes pure A3/BCD decoding and candidate API600 envelope construction for 520–531, excluding 532/340. Production allowlists remain unchanged. Captures require ordered timezone-bearing timestamps, matching raw frames, format and selectors. Pair atomicity and physical units remain unverified. `settings.py` is an observer and offline diff helper, not a settings sender: apply is blocked.

Pinned local Ghidra reproduction and emulator requirements: [P0086/reproduce.md](../../../requirements/package-runs/P0086/reproduce.md). Complete findings: [P0086/findings.md](../../../requirements/package-runs/P0086/findings.md).
