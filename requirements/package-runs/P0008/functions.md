# Package P0008 Function Design

## Package

`P0008`

## Scope

Mac-side Shelly build/deploy generation tooling in `src/mac/tools/shelly_build/`.

## New functions

### load_manifest()

Purpose: Read and validate a JSON Shelly build manifest.

Inputs: Manifest path.

Outputs: Manifest object containing script definitions.

Side effects: Reads one JSON file.

Reason: P0008 requires the tool to read a script build manifest.

Tests: Fixture build and invalid/missing source tests.

### build_script()

Purpose: Build one complete script by concatenating explicit source files in manifest order.

Inputs: Manifest path and script definition.

Outputs: Built script text and role name.

Side effects: Reads source files.

Reason: P0008 requires explicit helper and role source inclusion.

Tests: Fixture build script content and reconstruction tests.

### chunk_text()

Purpose: Split built script text into deterministic numeric chunks under a byte limit.

Inputs: Script text and max chunk byte size.

Outputs: Ordered chunk text list.

Side effects: None.

Reason: P0008 requires generated numeric deploy chunks with size validation.

Tests: Chunk generation and oversize validation tests.

### write_built_script()

Purpose: Write a complete built Shelly script to `build/shelly/<group>/<role>.js`.

Inputs: Build root, role name and script text.

Outputs: Built script path.

Side effects: Creates parent directories and writes a file.

Reason: P0008 requires complete built scripts under `build/shelly/`.

Tests: Fixture build test.

### write_chunks()

Purpose: Write ordered chunks to `dep/s/ch/<role>/NN.js`.

Inputs: Deploy root, role name and chunk texts.

Outputs: Chunk file paths.

Side effects: Creates or replaces the role chunk directory.

Reason: P0008 requires deployable numeric chunks.

Tests: Chunk generation and reconstruction tests.

### write_recipe()

Purpose: Write compact recipe JSON for a role.

Inputs: Deploy root, role name and chunk count.

Outputs: Recipe path.

Side effects: Creates parent directory and writes JSON.

Reason: P0008 requires recipe format `{"v":1,"n":<count>}`.

Tests: Chunk generation test.

### validate_role()

Purpose: Validate that recipe/chunks reconstruct the built script exactly and obey size limits.

Inputs: Build root, deploy root, role name and max chunk byte size.

Outputs: Validation result or exception.

Side effects: Reads built script, recipe and chunk files.

Reason: P0008 requires reconstruction and chunk size validation.

Tests: Reconstruction, missing chunk and oversize validation tests.

### build_from_manifest()

Purpose: Build every script listed in a manifest and return generated paths.

Inputs: Manifest path, build root, deploy root and max chunk byte size.

Outputs: List of build results.

Side effects: Reads source files and writes build/deploy artifacts.

Reason: Provides the package-level build operation.

Tests: Fixture end-to-end build test.

### main()

Purpose: Provide command-line access for build and validate operations.

Inputs: CLI arguments.

Outputs: Process exit status.

Side effects: Writes build/deploy artifacts for build; reads files for validate; prints concise status.

Reason: P0008 requires runnable Mac tooling and verification commands.

Tests: Covered indirectly by command verification.

### Private support helpers

Purpose: Keep file I/O, byte counting, numeric naming, safe source-path validation and manifest script-entry validation localized.

Functions:

- `_read_text()`
- `_write_text()`
- `_byte_len()`
- `_numeric_chunk_name()`
- `_safe_source_path()`
- `_script_entries()`

Inputs: Paths, text, raw source names, script indices or manifest objects depending on helper.

Outputs: Text, byte counts, chunk names, resolved paths or validated script entries.

Side effects: `_read_text()` reads files; `_write_text()` creates parent directories and writes files; other helpers have no side effects.

Reason: These helpers keep the public build/validate functions small and make path-safety and Python-version-compatible newline writing explicit.

Tests: Covered through fixture build, validation failure and standard-library import tests.

## Changed functions

None.

## Removed functions

None.

## Important unchanged functions

None.

## Design deviations during implementation

The implementation added private support helpers listed above. This does not expand package scope; it only factors the documented build/validate behavior into small test-covered functions.
