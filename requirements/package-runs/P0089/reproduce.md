# P0089 reproduce

From repository root, Python standard library only:

```sh
python3 tools/ftc6/p89/report.py requirements/package-runs/P0089
python3 -m unittest discover -s tools/ftc6/p89 -p test_p89.py
python3 -m unittest discover -s tools/ftc6/p86/tests -p test_p86.py
python3 -m unittest discover -s tools/ftc6/p88 -p test_p88.py
```

Private evidence:

```sh
python3 tools/ftc6/p89/extract_evidence.py ../../P0082/private/ftc6.bin ../../P0089/private /tmp/p89-evidence.json
P89_IMAGE=../../P0082/private/ftc6.bin P89_PRIVATE=../../P0089/private python3 -m unittest discover -s tools/ftc6/p89 -p test_p89.py
```

Private Ghidra work/repeat projects are isolated copies of P88 bits-fixed/bits-fixed-repeat. With P83Seed depth1 and P83Trace export roots from evidence.json/assembly_sha256 into matching directoriescontrols,controls-more,read-helpers and repeat. Logs must showTARGETED_EXPORT_COMPLETE; compare assembly byte-for-byte. Use P0082/run_headless.sh and scriptPath tools/ftc6/p83 from the outer workspace. Root addresses and tables are reference-image-specific; wrong image/missing evidence fail explicitly. Full vendor listings remain private.

The pure state fixtures inject explicit internal events. They do not emulate a working peer, open a transport, or prove timing on hardware. Frame construction is fixture serialization, not a live operation planner. P89 does not update P86/P87/P88 reports or production source.
