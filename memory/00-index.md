# G2 Smart Home Memory Index

This folder contains durable solution understanding for G2 Smart Home.

Memory is not a backlog and not a task list. It describes the decided system model:

- purpose and goals
- architecture
- design principles
- hardware and network facts
- G1/G2 boundaries
- Codex working model
- package lifecycle
- device management and deploy architecture

## Read order

1. `00-index.md`
2. `01-system-overview.md`
3. `02-design-principles.md`
4. `03-g1-g2-boundary.md`
5. `04-codex-workflow.md`
6. `05-package-lifecycle.md`
7. `device-management/00-index.md`

## Key folders

```text
device-management/  Shelly device identity, installer, deploy and build model
infrastructure/     network, NAT and device reachability facts
physical/           physical hardware, sensors and domain facts
planning/           planning notes and future-domain structure
knowhow/            reusable lessons from packages and debugging
```

## Market Simulator Boundary

Energy-market, spot-price forecasting, consumption-forecasting and simulator lab work moved to `marlov74/Market-Simulator` in `P0061`.

G2 may still contain historical Shelly spot-price runtime/deploy artifacts until a later package explicitly removes or migrates them.

## Boundary

Requirements and ordered work packages belong in `requirements/`.

Implementation source belongs in `src/`.

Deployable artifacts belong in `dep/`.

## Package rule

Memory may be updated by any package when the package changes system understanding.

Pure documentation and memory updates do not require a package id when they only record or correct physical facts, hardware inventory, model numbers, properties, notes, or other already-decided knowledge.

Use package linkage when the documentation change is discovered during package development, explains package behavior, records package evidence, or is required to keep code, tests, deploy artifacts or runtime behavior synchronized.

Examples:

- Documenting heat-pump brand, model and properties can be a direct documentation update.
- If P0014 discovers during implementation that `ftx-dampers` is now a Shelly Pro 1PM rather than a Shelly Pro 2, that finding belongs in the P0014 package log/evidence and the relevant memory update should reference the package context.
