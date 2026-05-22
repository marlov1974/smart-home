# AGENTS.md

This repository is the G2 Smart Home source of truth.

Before coding:

1. Read `README.md`.
2. Read `memory/bootstrap-manifest.json`.
3. Read every file in the manifest `read_order`, in order.
4. Read the active package in `requirements/packages/`.
5. Summarize understanding and plan before editing.

Rules:

- Keep G1 (`marlov1974/shelly`) and G2 (`marlov1974/smart-home`) separate.
- Do not treat G2 design as current G1 runtime behavior.
- Every code change must reference exactly one package id.
- A package is an ordered whole-solution version: `P0001`, `P0002`, ...
- Rollback is also a new forward-moving package.
- Shelly deploy artifacts live under `dep/s/`.
- Shelly devices must not fetch from `src/`.
- Do not invent Shelly APIs.
- Do not write to live devices unless the package explicitly allows it.
- Prefer read-only diagnostics by default.
- Run package test cases and verification commands before reporting done.
- Report diff, tests run, results and uncertainty before commit unless the package explicitly allows committing.
