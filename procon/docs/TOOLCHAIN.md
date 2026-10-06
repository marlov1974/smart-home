# P0069 development environment

Persistent checkout: `/Users/marcus/Documents/Codex/smart-home-procon` (worktree of existing Smart Home repo). Tooling lives in ignored procon/.local; source and tests are versioned. Homebrew, ARM GCC, CMake/Ninja and .NET were absent at inventory; used official portable ARM tarball plus existing Make, avoiding a systemwide package-manager installation. No updater execution.

- Apple Silicon arm64 macOS; Python3.14.7.
- ARM GNU Toolchain14.3.Rel1: GCC14.3.1 20250623; binutils2.44.0.20250616.
- Native tests: Apple clang21.0.0 (clang-2100.1.1.101), ASan/UBSan.
- Python exact versions: tools/requirements.txt (Capstone5.0.9, pyelftools0.33, Unicorn2.1.4, dnfile0.18.0, dncil1.0.2, pefile2024.8.26).

Install/rebuild from repository root:

```sh
sh procon/tools/setup.sh
make -C procon verify
procon/.local/venv/bin/python procon/tools/analyze_updater.py
```

Setup uses Python venv/pip and an official Arm archive. [Arm installation guide](https://learn.arm.com/install-guides/gcc/arm-gnu/) and pinned download URL are recorded in setup.sh. Archive SHA25630f4d08b219190a37cded6aa796f4549504902c53cfc3c7e044a8490b6eba1f7 matched Arm's .sha256asc file. Tools were initially downloaded/extracted under/tmp, then moved into .local; Python wheels installed into the final venv with `python -m pip install --no-index --find-links=/tmp/procon-wheels -r procon/tools/requirements.txt`. Setup.sh reproduces that environment using public downloads.

Unicorn JIT raised macOS illegal-instruction under the Codex sandbox. The identical test passed outside the sandbox. Grant JIT execution permission when required; do not count a sandbox crash as a passing test or hide failures. Tests have no serial/network device access.

GNU Make accepts TOOLCHAIN=/path/to/toolchain and PYTHON=/path/to/python overrides for other supported compiler hosts. Original vector comparison used ST CMSIS-L4 commitca0bfa2b8b68dc2994b27fba0a10dfd28d086ee1, optional command `python tools/analyze_original.py /path/to/Source/Templates/gcc` from procon. Generated BIN deterministic across a forced full rebuild. No Ghidra/OpenOCD needed for this bounded milestone.

P0070: M1 r2 now hardware-confirmed; next experimental build adds CN10524008E1 on PA9/10AF7 and read-only compressor telemetry. See `../releases/P0070-compressor-r1/README.md` and `CN105.md`. Same conservative flash/RAM/vector limits and96KiB FF envelope. Physical CN105 result pending. No setting writes or physical flash by Codex.
