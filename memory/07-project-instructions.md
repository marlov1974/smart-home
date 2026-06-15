# Project Instructions for AI Sessions

This file contains the intended ChatGPT project-instruction model for the Smart Home project.

## Repository roles

Primary source of truth for current production Smart Home work:

```text
marlov1974/smart-home
```

Historical Gen1 provenance repository:

```text
marlov1974/shelly
```

Separate forecast/simulation lab repository:

```text
market-simulator
```

G1 is retired. Do not use `marlov1974/shelly` as the source of truth for current production runtime behavior.

`market-simulator` is a separate lab for AI/ML-based consumption forecasts, spot-price forecasts and market simulation. Do not load it during Smart Home startup.

## Recommended project instruction text

Use this as the project-level instruction for future ChatGPT sessions:

```text
Primary source of truth for current production Smart Home work:
- marlov1974/smart-home

Historical Gen1 provenance repository:
- marlov1974/shelly

Separate forecast/simulation lab repository:
- market-simulator

Before producing any user-facing answer in a new chat:
1. Bootstrap marlov1974/smart-home:
   - read README.md
   - read memory/bootstrap-manifest.json
   - read every mandatory file listed in read_order, in order
   - read REPOSITORY_FILES.md when the tool context cannot enumerate tracked repository paths directly, when path discovery is needed, or when the task may add, remove or move tracked files
2. Treat REPOSITORY_FILES.md as a tracked path catalog, not as a command to read every file in the repository. Use it to discover candidate paths, then read only the files required by the manifest, active package, package-run evidence, or current task.
3. Do not bootstrap or read market-simulator during Smart Home startup. Inspect it only when the user explicitly asks for Market Simulator work, lab forecast experiments, model work or cross-repo comparison involving that project.
4. Also inspect marlov1974/shelly only when the task explicitly asks for:
   - historical Gen1 behavior
   - pre-G2 comparison
   - provenance for old Shelly scripts or G1 KVS contracts
   - analysis of why retired G1 behavior differed from current G2 behavior
5. If any mandatory bootstrap step fails, report BOOTSTRAP FAILED and include the missing step/file.
6. After bootstrap, use:
   - smart-home as source of truth for G2 production architecture, packages, Mac tooling, Home Assistant/Shelly implementation, deploy artifacts and current runtime behavior
   - shelly only as historical Gen1 provenance, not as production truth
   - market-simulator only as a separate lab project, not as Smart Home startup context or G2 production truth
7. For requirements-analysis continuity, read smart-home/memory/06-chatgpt-requirements-analyst.md after the normal smart-home bootstrap.
8. If ChatGPT or Codex adds, removes or moves tracked files, update REPOSITORY_FILES.md in the same change.
```

## Operating rule

If the task is G2 work, current runtime behavior, production operation, Home Assistant, Mac tooling, Shelly deploy/runtime or package review, bootstrap `marlov1974/smart-home` first and treat it as the current source of truth.

If the task needs historical G1 facts, inspect `marlov1974/shelly` only for that historical/provenance purpose and keep those claims separate from current G2 production claims.

If the task is about AI/ML consumption forecasts, spot-price forecasts, market simulation or lab/model experimentation, use `market-simulator` only when explicitly asked and keep it separate from Smart Home production truth.

## Repository file index rule

`REPOSITORY_FILES.md` is the tracked path catalog for contexts that cannot enumerate repository files directly.

Use it to discover paths and avoid broad tree reads. It is not ordinary bootstrap content for every listed file. Do not read every tracked file simply because it appears in `REPOSITORY_FILES.md`; read the files needed by the manifest, active package, package-run evidence, or current task.

When a tracked file is added, removed or moved, update `REPOSITORY_FILES.md` in the same change and mention whether it changed in the final report or package-run changelog.

## Why this exists

Older project instructions treated `marlov1974/shelly` as the current runtime source of truth. That is no longer correct.

G2 package workflow, Mac tooling, Home Assistant/Shelly implementation, requirements-analysis continuity and current production runtime truth now belong in `marlov1974/smart-home`.

Forecast/simulation lab work that previously lived in G2 now belongs in `market-simulator` and should not consume Smart Home bootstrap context.
