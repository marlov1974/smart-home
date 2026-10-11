# P0081 — asynchronous diagnostics and Shelly mode transitions

Validated during P0081 activation and the physical mapping run:

- Shelly `Serial.SetConfig` can return `restart_required: true`. Read back the configuration after the authorized reboot, then validate the actual Modbus path. A successful configuration RPC alone does not qualify the transport.
- A successful Modbus FC16 response acknowledges diagnostic acceptance, not receipt of a heat-pump reply. Poll an isolated result block and validate request ID, kind, code, completion generation, status, length and checksum.
- Capture submission intent before transmission and preserve terminal responses before propagating a subsequent health-check failure. A failed safety/quality check should stop new work without discarding the evidence that preceded it.
- Keep direct GET A3 distinct from a parameterized A3 service transaction. A direct reply containing zeros does not contradict a successful parameterized service read.
- The A3 status byte is not a simple supported/unsupported boolean. This scan observed status 3 on fault-history codes, 4 on operation-state codes and 6 on condensing-temperature codes. Established numeric/hex decoders handle 1/2; retain other checksum-valid frames as unhandled formats, without declaring the service absent. Display-format semantics for 3/4/6 remain unverified.
- Empty, zero-filled and FF-pattern replies require separate classifications. None establishes a physical sensor mapping. Likewise, a bounded timeout is no response under the tested conditions, not proof of unsupported firmware functionality.
- Preserve raw private evidence, but publish only sanitized code/status coverage and reproducible tools. Energy dates and plausible power values require unit, clock and update-time validation before being used as live COP.

Evidence: `requirements/package-runs/P0081/implementation-report.md` and the private P0081 installation, mode-transition, baseline and mapping records. Full scan coverage is recorded separately; these lessons do not assert that mapping is already complete.
