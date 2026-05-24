# Project Instructions for AI Sessions

This file contains the intended ChatGPT project-instruction model for the Smart Home project.

## Repository roles

This project has two repositories with different roles.

Primary source of truth for G2 Smart Home work:

```text
marlov1974/smart-home
```

Source of truth for current Gen1 Shelly/FTX runtime behavior:

```text
marlov1974/shelly
```

## Recommended project instruction text

Use this as the project-level instruction for future ChatGPT sessions:

```text
This project has two repositories with different roles.

Primary source of truth for G2 Smart Home work:
- marlov1974/smart-home

Source of truth for current Gen1 Shelly/FTX runtime behavior:
- marlov1974/shelly

Before producing any user-facing answer in a new chat:
1. Bootstrap marlov1974/smart-home:
   - read README.md
   - read memory/bootstrap-manifest.json
   - read every mandatory file listed in read_order, in order
2. Also bootstrap marlov1974/shelly if the task touches:
   - current Gen1 runtime behavior
   - existing Shelly scripts
   - G1 KVS contracts
   - physical/runtime truth currently running in G1
   - migration from G1 to G2
3. If any mandatory bootstrap step fails, report BOOTSTRAP FAILED and include the missing step/file.
4. After bootstrap, use:
   - smart-home as source of truth for G2 architecture, packages, Mac tooling, Home Assistant/Shelly future implementation
   - shelly as source of truth for current G1 runtime implementation
5. For requirements-analysis continuity, read smart-home/memory/06-chatgpt-requirements-analyst.md after the normal smart-home bootstrap.
```

## Operating rule

If the task is clearly G2 work, bootstrap `marlov1974/smart-home` first.

If the task needs facts about currently running G1 code or existing Shelly implementation, bootstrap `marlov1974/shelly` too and ground runtime claims in implementation files.

## Why this exists

Older project instructions treated `marlov1974/shelly` as the only primary source of truth. That is no longer correct for G2 development.

G2 package workflow, Mac tooling, future Home Assistant/Shelly design and requirements-analysis continuity now belong in `marlov1974/smart-home`.
