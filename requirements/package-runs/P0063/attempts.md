# P0063 Attempts

## Attempt 1

Status: passed.

Precheck:

- dampers identity: `shellypro1pm-8813bfd99f54`
- dampers `Number 202`: `54`
- dampers `ftx.state.run.vvx`: `0`
- dampers `ftx.state.hist`: `{r0:53.8,r1:53.8,r2:53.8}`
- vvx endpoint does not have `Number 202`, so it was not targeted.

Implementation:

- added `deploy-ftx-state` to `src.mac.tools.shelly_live`
- added unit coverage for recipe build, allowlist and deploy verification sequence
- added cross-package function documentation

Live result:

- deployed `state_v1_8_0` to dampers script id `5`
- uploaded in `9` RPC chunks
- observed `state DON`
- verified `Number 202 = 0`
- verified `ftx.state.hist = {r0:0,r1:0,r2:0}`

Unexpected observation:

- `brain_v2_13_0` was running before the deploy command and stopped afterwards.
- The debug log shows the existing live `master_v1_8_0` issued `Script.Stop {"id":7}` during the same window.
- P0063 did not upload or start brain/executor scripts. No compensating brain start was performed because the package did not authorize it.
