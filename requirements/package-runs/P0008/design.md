# Package P0008 Implementation Design

## Package

`P0008`

## Package interpretation

Create deterministic Mac-side Python tooling that builds logical Shelly source into complete runnable scripts, splits those scripts into numeric deploy chunks, writes compact recipe JSON and validates the result.

This package implements only a minimal first tool and fixture. It does not implement a Shelly installer, live deploy, real FTX migration or external dependency.

## Chosen implementation structure

The tool will live under:

```text
src/mac/tools/shelly_build/
```

Planned files:

- `src/mac/tools/shelly_build/__init__.py`: package marker and public import surface.
- `src/mac/tools/shelly_build/__main__.py`: command-line entry point for build and validate operations.
- `src/mac/tools/shelly_build/core.py`: manifest loading, source assembly, chunk generation, recipe writing and validation.
- `src/shelly/fixture/manifest.json`: minimal build manifest for the fixture role.
- `src/shelly/fixture/helpers.js`: explicit helper source.
- `src/shelly/fixture/hello.js`: role source.
- `tests/mac/tools/shelly_build/test_core.py`: unit tests for build, chunking, validation failures and stdlib-only behavior.
- `docs/functions/mac/shelly-build-tool.md`: durable function catalog entry.

Generated files:

- `build/shelly/fixture/hello.js`
- `dep/s/ch/hello/01.js`
- `dep/s/rec/hello.json`

## Manifest schema

The first build manifest is JSON:

```json
{
  "scripts": [
    {
      "role": "hello",
      "sources": [
        "helpers.js",
        "hello.js"
      ]
    }
  ]
}
```

Paths are relative to the manifest directory. The tool resolves them deterministically and rejects missing files, absolute paths and paths that escape the source root.

## Intended changes

### Files/modules to change

- Create the package-scoped tool, fixture, tests, generated deploy output and function docs listed above.

### Files/modules intentionally not changed

- No G1 repository files.
- No live device files or scripts.
- No installer implementation.
- No real FTX Shelly source.
- No bootstrap manifest update, because P0008 does not add mandatory bootstrap context.

## Refactoring decisions

No existing code is refactored. This package creates the first implementation in new package-scoped paths.

## Test strategy

Unit tests will cover:

- fixture manifest builds one complete script
- numeric chunk and compact recipe generation
- chunk reconstruction equals the built script
- validation failure for missing chunks
- validation failure for oversize chunks
- obvious external dependency import violations in the tool package

## Build / generated artifact strategy

The tool writes generated artifacts from source input. Generated chunks are not manually edited after build.

Default chunk size for production generation is conservative and configurable. Tests use a smaller chunk size where needed to force multiple chunks.

Final verification commands:

```bash
python3 -m unittest discover tests/mac/tools/shelly_build
python3 -m src.mac.tools.shelly_build build --manifest src/shelly/fixture/manifest.json --build-root build/shelly/fixture --dep-root dep/s
python3 -m src.mac.tools.shelly_build validate --build-root build/shelly/fixture --dep-root dep/s --role hello
git diff --check
```

## Risks and uncertainties

- The manifest schema is package-local and may need refinement in a future package when real G2 Shelly roles are introduced.
- The first recipe format contains only `{"v":1,"n":<chunk_count>}` as required. Future installer work may add registry or device-level references in separate files.

## Design deviations during implementation

None yet.
