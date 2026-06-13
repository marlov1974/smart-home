# FTX Cooling and Condensate Risk

Cooling through the FTX cooling battery creates condensation risk.

Condensate handling is therefore a control constraint, not only a plumbing detail.

## Known risk

There has been concern around condensate tray/drain behavior and water lock/open drain details.

Cooling capacity or fan levels should not be expanded without confirming that condensate can be safely removed.

## Control implication

Cooling should require:

- fans running
- dampers open
- cooling water/brine available
- safe condensate path
- dewpoint/temperature logic where relevant

## Dewpoint margin observation

P0059 records an operator-tested physical observation: the ventilation pipe surface is a few degrees warmer than the air inside the pipe. In the current installation, no condensation occurs on the pipe even when the air in the pipe is a couple of degrees colder than calculated dewpoint.

Control implication: G2 FTX should not add an extra generic safety margin on top of calculated dewpoint for the supply-air minimum. The absolute minimum supply target still remains a separate control floor, lowered to 12.0 C by P0060.

## Safety principle

When uncertain, limit cooling. Condensate and moisture problems are more serious than missing some cooling effect.

## Source

Imported from G1 `memory/ftx-fysiskt/08-condensate-and-cooling-risk.md` during `P0002`.
