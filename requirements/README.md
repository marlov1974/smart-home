# Requirements

Requirements describe desired behavior and ordered change packages. They do not mirror the code folder structure.

## Levels

```text
Epic       long-term direction / large objective
Feature    system capability
User Story observable behavior or scenario
Package    ordered whole-solution change version
```

## IDs

```text
E0001   Epic
F0001   Feature
US0001  User Story
P0001   Package
```

## Package rule

Package is the implementation anchor.

Every code change must reference exactly one package id.

A package may update:

- memory
- requirements
- source code
- deploy artifacts
- diagnostics
- tests

Rollback is also a new package.

## Linking rule

- Epics link to features.
- Features link to user stories.
- User stories link to packages.
- Packages link back to epics/features/stories.

Use explicit IDs in files rather than relying on folder structure.
