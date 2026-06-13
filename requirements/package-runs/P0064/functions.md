# P0064 Function Design

## New Test Function

### _total_power_gauge_block()

Purpose: Extract the `Total effekt` gauge block from the YAML text using simple line-based parsing.

Inputs: YAML text.

Outputs: Gauge block text.

Side effects: none.

Reason: The repository does not depend on PyYAML. A narrow text test is enough for this static dashboard artifact.

Coverage: `tests/mac/ha/test_ftx_dashboard.py`.

## No Runtime Functions

P0064 does not add Home Assistant runtime code or Shelly/Mac service functions.
