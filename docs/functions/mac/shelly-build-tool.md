# Mac Shelly Build Tool Function Catalog

## Scope

Mac-side G2 Shelly source/build/deploy artifact generation introduced by P0008.

## Functions

### load_manifest()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_build/core.py`

Purpose:
- Read and validate a JSON Shelly build manifest.

Inputs:
- Manifest path.

Outputs:
- Manifest object containing script definitions.

Side effects:
- Reads one JSON file.

Contract notes:
- Manifest root must be an object with a non-empty `scripts` list.
- Each script must have a non-empty `role` and non-empty `sources` list.

Used by:
- P0008 Shelly build tool.

Tests:
- `tests/mac/tools/shelly_build/test_core.py`

Introduced:
- P0008

Last changed:
- P0008

### build_script()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_build/core.py`

Purpose:
- Build one complete runnable Shelly script by concatenating explicit source files.

Inputs:
- Manifest path and script definition.

Outputs:
- Role name and built script text.

Side effects:
- Reads source files.

Contract notes:
- Source paths are relative to the manifest directory.
- Absolute paths and paths escaping the manifest directory are rejected.

Used by:
- `build_from_manifest()`

Tests:
- `tests/mac/tools/shelly_build/test_core.py`

Introduced:
- P0008

Last changed:
- P0008

### chunk_text()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_build/core.py`

Purpose:
- Split built script text into deterministic chunks under a byte limit.

Inputs:
- Script text and max chunk byte size.

Outputs:
- Ordered chunk text list.

Side effects:
- None.

Contract notes:
- Splits on line boundaries.
- Raises when one source line exceeds the byte limit.

Used by:
- `build_from_manifest()`

Tests:
- `tests/mac/tools/shelly_build/test_core.py`

Introduced:
- P0008

Last changed:
- P0008

### validate_role()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_build/core.py`

Purpose:
- Validate recipe/chunk presence, chunk sizes and exact reconstruction of a built script.

Inputs:
- Build root, deploy root, role name and max chunk byte size.

Outputs:
- No return value on success; raises `BuildError` on failure.

Side effects:
- Reads built script, recipe and chunk files.

Contract notes:
- Recipe format is compact JSON `{"v":1,"n":<chunk_count>}`.
- Chunks must be named `01.js`, `02.js`, etc.

Used by:
- P0008 verification command and `build_from_manifest()`.

Tests:
- `tests/mac/tools/shelly_build/test_core.py`

Introduced:
- P0008

Last changed:
- P0008

### build_from_manifest()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_build/core.py`

Purpose:
- Build every script listed in a manifest and write build/deploy artifacts.

Inputs:
- Manifest path, build root, deploy root and max chunk byte size.

Outputs:
- List of generated `BuildResult` records.

Side effects:
- Writes built scripts, chunk files and recipe files.

Contract notes:
- Validates generated artifacts before returning.
- Replaces the generated chunk directory for each role.

Used by:
- CLI `build` command.

Tests:
- `tests/mac/tools/shelly_build/test_core.py`

Introduced:
- P0008

Last changed:
- P0008

### main()

Status: active

Owner/runtime:
- Mac

Source:
- `src/mac/tools/shelly_build/core.py`

Purpose:
- Provide command-line build and validate operations.

Inputs:
- CLI arguments.

Outputs:
- Process exit status.

Side effects:
- `build` writes build/deploy artifacts.
- `validate` reads build/deploy artifacts.
- Prints concise status.

Contract notes:
- Returns `1` and prints `error: ...` for `BuildError`.

Used by:
- `python3 -m src.mac.tools.shelly_build`

Tests:
- Verification commands in P0008.

Introduced:
- P0008

Last changed:
- P0008
