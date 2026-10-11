# P0087 findings

P87 offline handoff is complete with **PARTIAL native reconstruction**, not a solved whole-machine regulator. The useful new result is a connected fixed-flow target path, an exact error-to-temperature lookup and independent request encodings, plus a conditional water-pump step correction. They support a bounded executable model without inventing the other controller's frequency algorithm.

1. Accepted fixed target38DE flows through mode/alternate selection into effective3908;390C is a separate fallback. Sensor0662/0664 includes conditional calibration. Error calculation locally floors the selected target at25C; the independent outgoing target does not share that floor.
2. A1ED8 maps heating error in0.5C bands to29..24C temperature-like output, with a post-lookup27C override. The lookup is memoryless (no retained sum); it is **not** aHz/kW law. A separate serializer prepares target and feedback in0.5C units. Active Geodan personality and peer law remain unresolved.
3. Generic timer enable/count/reset/pause semantics are proven; their control-specific tick-to-second chain is not. No fixed-flow+2C stop or ten-minute restart is asserted. The manual's thermo-diff settings retain their room-control scope.
4. Pump selection is phase-dependent and can be corrected by49C7 under request1/3AD2=2. This is more than a universally fixed stored pump level; its menu/closed-loop origin is not yet proven.
5. Historical traces show time-dependentHz at constant target, but also mode/measurement confounders. They do not identify an integrator or validate a no-overshoot6kW response.

| Track | Status | Physical |
|---|---|---|
| A target/feedback | PARTIAL: connected ordinary path and encoders; scheduler/filter/profile unknown | NOT RUN |
| B running demand/ownership | PARTIAL: exact local table, no peerHz law | NOT RUN |
| C timing/start-stop | PARTIAL: helper/branch catalog, no complete thermostat graph or seconds | NOT RUN |
| D actuators | PARTIAL: pump selection/correction/upstream gates; brine/valve boundaries remain | NOT RUN |
| E executable evidence | PASS for deliberately partial model,8 scenarios, historical replay and limits | NOT RUN |

E PASS denotes tested tooling and honest UNKNOWN outputs, not a full physical model. Existing EFFECT and all live devices remain untouched. The next smallest useful verification is identifying the active outbound temperature/request representation and correlating it with targetHz/actualHz and limit state; proposed physical work remains unexecuted.
