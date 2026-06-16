# P0067 Design

## Package Interpretation

Create a Home Assistant-compatible FTX SVG with a black industrial/classic visual style.

## Implementation Structure

- `src/ha/assets/ftx-industrial.svg` is the source asset.
- `dep/ha/assets/ftx-industrial.svg` is the deployable copy.
- `tests/mac/ha/test_ftx_dashboard.py` verifies source/deploy sync and basic SVG validity/contract.
- `REPOSITORY_FILES.md` is regenerated because new tracked files are added.

## Intended Visual Design

- Black background.
- Steel cabinet/chassis.
- Duct arrows for outdoor air, supply, extract and exhaust.
- Fan circles and a central VVX/core section.
- Restrained amber/green/cyan accents against dark industrial greys.
- Compact technical labels suitable for HA dark theme.

## Files Intentionally Not Changed

- The FTX dashboard YAML is not changed because the user asked to create an SVG, not to alter the dashboard layout or go live.
- Shelly and Mac runtime files are not changed.

## Test Strategy

- Unit test source/deploy asset equality.
- Parse XML and verify the root SVG element/viewBox.
- Assert requested visual contract markers: black background, FTX title, VVX, supply/extract labels.
- Run `git diff --check`.

## Risks and Uncertainties

- Home Assistant serving path is deployment-specific; this package creates the asset but does not install or reference it live.
- Visual preference may need iteration after the user sees it in HA.
