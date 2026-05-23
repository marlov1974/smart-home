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
knowhow/            reusable lessons from packages and debugging
```

## Boundary

Requirements and ordered work packages belong in `requirements/`.

Implementation source belongs in `src/`.

Deployable artifacts belong in `dep/`.

## Package rule

Memory may be updated by any package when the package changes system understanding.

No durable knowledge change should be made without a package id.
