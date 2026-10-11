# Reproduce P0086

From the G2 repository root, Python 3.14.7 (stdlib only, no dependencies to install):

```sh
python3 -m unittest discover -s tools/ftc6/p86/tests -v
python3 tools/ftc6/p86/reader.py --help
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation read --address 0x400 --length 1
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --fixture tools/ftc6/p86/fixtures/session.json
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation read --address 0x400 --length 1 --fixture tools/ftc6/p86/fixtures/read.json
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation log --fixture tools/ftc6/p86/fixtures/log.json
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation energy --fixture tools/ftc6/p86/fixtures/energy.json
```

Expected PASS for fixtures; DRY_RUN without a fixture. All are synthetic, not real captures. Negative examples must return nonzero:

```sh
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --fixture tools/ftc6/p86/fixtures/timeout.json
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --operation read --address 0x80000 --length 1
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-normal-static
python3 tools/ftc6/p86/reader.py --profile ftc6-20.01-diag-static --execute
```

For evidence retention add `--output /new/private/path.json`; the file must not already exist. No connection opens, network calls, request retries or real sleeps occur. Fixture elapsed times simulate deadlines; cancellation is explicit fixture data. Hardware execution is blocked before output.

## Private analysis reproduction

Use the pinned P83 repaired decoder, Ghidra12.1.4 PUBLIC and Java21.0.12.1+1. No reinstall. Exact hashes are in verification.json. Full original image, projects and exports remain private. Root workspace contains P0082/run_headless.sh, P0082/private/ftc6.bin and P0085/private/projects/final.gpr/final.rep.

Copy the finalized P85 project independently to P0086/private/projects/fresh-a.gpr/.rep and fresh-b.gpr/.rep (do not overwrite existing projects). `run_analysis.py` uses fixed root/target files and depth2; paths below assume this repository is P0080/implementation-smart-home under that workspace. It writes local Ghidra preferences, so sandbox permission may be required.

```sh
python3 tools/ftc6/p86/run_analysis.py ../.. fresh-a
python3 tools/ftc6/p86/run_analysis.py ../.. fresh-b
python3 tools/ftc6/p86/run_analysis.py ../.. fresh-a --proof
python3 tools/ftc6/p86/verify_local.py ../../P0082/private/ftc6.bin ../../P0086/private/fresh-a ../../P0086/private/fresh-b ../../P0086/private/fresh-a-proof.log /tmp/p86-evidence-repeat.json
```

The recorded first run used the same P83Seed/P83Trace arguments directly through run_headless.sh; the wrapper executes identical options. Two independently seeded copies produced222 identical files and all73 requested function roots matched. The proof emulated8 logical addresses at the one reviewed load. Exact operand checks reject changed/unsupported instruction evidence; tests separately exercise wrong-image rejection. The hash mock in one unit test isolates operand checking and is not the real input validation.

Run `git diff --check` and, after staging, `git diff --cached --check`. Rebuild REPOSITORY_FILES.md from `git ls-files`, including staged new files. Native/ARM tests are not applicable: no firmware source, headers, allowlists or build artifacts changed.

Sources: local official Renesas M16C/60 software manual §2.3 printedpp24–25 and M16C/65 R01UH0135EJ0210 table1.10/clock chapter; P0083 provenance, P0084 settings/transport trace, P0085 protocol/access evidence. The hardware manual pin/clock claims remain conditional on exact MCU/package identification.
