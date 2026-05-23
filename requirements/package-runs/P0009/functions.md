# Package P0009 Function Design

## Package

`P0009`

## Functions To Create

### _manifest_label()

Status: new

Purpose:
- Convert the manifest path supplied to the build into deterministic metadata text.

Inputs:
- Manifest path as `str` or `Path`.

Outputs:
- POSIX-style manifest path string.

Side effects:
- None.

Reason:
- P0009 requires manifest metadata in the generated built script.

Test coverage:
- Header metadata assertions in `test_build_fixture_script`.

### _format_header()

Status: new

Purpose:
- Generate deterministic built-script metadata header comments.

Inputs:
- Role, manifest path and source path list.

Outputs:
- Header text ending with a blank line.

Side effects:
- None.

Reason:
- P0009 requires generated-file, role, manifest, source, tool and package metadata.

Test coverage:
- Header and metadata assertions in `test_build_fixture_script`.

### _indent_source()

Status: new

Purpose:
- Indent assembled source for placement inside the IIFE wrapper.

Inputs:
- Source text.

Outputs:
- Indented source text.

Side effects:
- None.

Reason:
- P0009 requires original source content inside an IIFE-style wrapper.

Test coverage:
- Wrapper/source assertions in `test_build_fixture_script`.

### _wrap_script()

Status: new

Purpose:
- Combine header and assembled source into the final generated built script.

Inputs:
- Header text and assembled source text.

Outputs:
- Complete generated built script.

Side effects:
- None.

Reason:
- P0009 requires IIFE wrapper and strict mode in the built output.

Test coverage:
- Wrapper and strict-mode assertions in `test_build_fixture_script`.

## Functions To Change

### build_script()

Status: changed

Purpose:
- Build one complete generated Shelly script from explicit source files.

Inputs:
- Manifest path and script definition.

Outputs:
- Role name and generated built script text.

Side effects:
- Reads source files.

Change description:
- Preserve source ordering and path safety, but return header + IIFE-wrapped output instead of plain concatenated source.

Reason:
- P0009 makes wrapper/header behavior required repository truth.

Test coverage:
- Existing build, chunking and reconstruction tests.
- New header, metadata, wrapper and strict-mode assertions.

## Functions To Leave Unchanged

### load_manifest()

Reason:
- Existing manifest validation remains sufficient for P0009.

### chunk_text()

Reason:
- P0009 changes built text content, not chunking semantics.

### write_built_script()

Reason:
- File writing behavior remains unchanged.

### write_chunks()

Reason:
- Generated deploy chunks still use P0008 numeric chunk semantics.

### write_recipe()

Reason:
- Recipe format remains `{"v":1,"n":<chunk_count>}`.

### validate_role()

Reason:
- Existing chunk size and exact reconstruction validation remains required.

### build_from_manifest()

Reason:
- The build orchestration remains correct; it receives changed built text from `build_script()`.

### main()

Reason:
- CLI behavior remains unchanged.

## Functions To Remove

None.
