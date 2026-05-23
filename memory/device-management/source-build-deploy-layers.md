# Source / Build / Deploy Layers

G2 Shelly code uses three layers.

```text
1. Source layer
2. Built script layer
3. Deploy chunk layer
```

The layers must not be confused.

## 1. Source layer

Source is organized for humans, ChatGPT and Codex.

It should be logical, readable and testable.

Example:

```text
src/shelly/ftx/brain/
  build.json
  inputs.js
  needs.js
  hard_constraints.js
  resolver.js
  intent.js
  main.js
```

Source files are split by responsibility, not by Shelly upload constraints.

Do not create one file per tiny function as a default. Prefer one file per coherent responsibility.

## 2. Built script layer

A build tool concatenates/assembles source into one complete Shelly script per runtime role.

Example:

```text
build/shelly/ftx/brain/brain.js
```

This file represents what the Shelly script should become after all chunks are uploaded.

It may include build metadata at the top.

Example:

```js
// g2_script=brain
// g2_package=P0049
// g2_built_from=src/shelly/ftx/brain
```

## 3. Deploy chunk layer

Deploy chunks are generated from the complete built script and split only by byte size.

Example:

```text
dep/s/ch/brain/01.js
dep/s/ch/brain/02.js
dep/s/ch/brain/03.js
```

Chunks have numeric names and no logical meaning.

A chunk may contain parts of multiple source files. That is acceptable because chunks are transport artifacts, not source architecture.

## Recipe

The recipe only stores chunk count.

Example:

```json
{"v":1,"n":3}
```

Installer derives paths by convention:

```text
dep/s/ch/<role>/01.js
dep/s/ch/<role>/02.js
...
```

## Build tool responsibility

Deploy layers must be generated deterministically by tools, not manually assembled by an LLM.

The Shelly build tool must:

```text
1. read source build manifest
2. concatenate/assemble source in deterministic order
3. write complete built script
4. split into numeric chunks by max byte size
5. write recipe with chunk count
6. verify concat(chunks) == built script
7. verify chunk size limits
```

## Codex rule

For Shelly code packages, Codex should:

```text
1. modify src/
2. run source tests
3. run Shelly build tool
4. run deploy validation
5. commit source and generated deploy artifacts when package allows
```

Codex must not manually maintain deploy chunks unless the package explicitly modifies build/deploy tooling or generated artifact policy.

## Why this replaces G1 chunk thinking

G1 chunks were partly shaped by manual GitHub editing and Shelly limitations.

G2 keeps Shelly limitations only in generated deploy artifacts. Source code should remain normal, logical and testable.
