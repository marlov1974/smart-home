# P0072 — Procon MVP telemetry and control API

Operator request 2026-10-06: evolve the hardware-verified P0071 clean-room Procon firmware into the first practical Smart Home MVP interface. Preserve the working P0069-P0071 transport, Modbus, heartbeat, compressor telemetry and exclusive A3 service sequencing. Operator alone flashes physical hardware.

## Objective

Expose a compact stable API consisting of 20 process values plus the minimum useful control surface for normal operation and experiments. Do not add closed-loop kW/L1 control or COP calculation in this package.

Shelly remains responsible for electrical-power measurement, COP calculation, logging and higher-level control.

## CN105 scheduler

Maintain a continuously repeating measurement cycle.

FAST telemetry consists of ordinary CN105 requests that complete normally.

SERVICE telemetry is exclusive: once an A3 service operation starts, no other CN105 request may be inserted between its retries.

Alternate the slow service query between complete cycles:

```text
FAST cycle -> A3/27 until complete -> FAST cycle -> A3/28 until complete -> repeat
```

A3/27 and A3/28 must retain the P0071-r2 rule: the service operation owns CN105 until completion/exhaustion. No compressor GET, connect, or other CN105 query may appear between retries.

Implement the slow-query scheduler generically so additional service queries can later be added without redesigning the state machine.

## MVP telemetry — 20 values

Expose stable read-only Modbus registers for:

1. brine inlet temperature, TH32;
2. brine outlet temperature, TH34;
3. brine delta-T, calculated locally;
4. heating flow/supply temperature;
5. heating return temperature;
6. heating-water delta-T, calculated locally;
7. primary/heating-water flow rate;
8. instantaneous delivered thermal power, calculated from measured flow and flow/return delta-T;
9. compressor frequency Hz;
10. compressor running state;
11. brine-pump running state;
12. brine-pump actual/output step if a trustworthy read path is established;
13. heating-water circulation-pump running state;
14. heating-water circulation-pump actual level if a trustworthy read path is established;
15. DHW tank temperature;
16. outdoor temperature;
17. current heating-flow target;
18. current DHW target;
19. current operating mode;
20. electric/booster-heater state or stage.

Do not fabricate unavailable values. If 12 or 14 cannot yet be read reliably, expose explicit unavailable/invalid status and document the missing protocol mapping rather than guessing.

All dynamic measurements need validity/freshness semantics. Preserve sample age or equivalent diagnostics outside the 20-value product list.

## Thermal power

Calculate instantaneous delivered heat locally from measured primary/heating-water flow and flow/return delta-T. Use fixed-point/integer arithmetic where practical.

Document:
- units and scaling;
- fluid heat-capacity/density assumption;
- sign convention;
- behavior with stale/invalid flow or temperature samples;
- whether glycol correction is applied.

Do not calculate COP in Procon. Shelly combines Procon thermal power with the external electrical meters.

The Geodan service documentation states that its own delivered-heat calculation is based on flow/return delta-T multiplied by measured flow; use that as design corroboration, not as permission to invent unavailable sensor precision.

## Control API

Provide these user-facing controls:

### 1. Operating mode

Stable enum:
- OFF
- AUTO
- FIXED_FLOW
- DHW

Semantics:
- OFF: request normal supported Mitsubishi off/standby behavior.
- AUTO: return control to normal Mitsubishi/ETC logic for heating and DHW.
- FIXED_FLOW: operate space heating using the configured flow-temperature target.
- DHW: request/force DHW production using the supported Mitsubishi mechanism.

Map these abstractions onto verified CN105 SET behavior. Do not invent unsupported combinations.

### 2. Heating flow target

Writable desired flow temperature used by FIXED_FLOW. Validate range before transmitting. Readback must expose the effective/current target separately.

### 3. DHW target

Writable desired DHW temperature. Validate range before transmitting. Readback must expose the effective/current target separately.

### 4-5. Command robustness

Implement a command sequence/acknowledgement mechanism and an external-control lease/failsafe or equivalent robust design so Shelly can distinguish:
- Modbus write accepted;
- command actually applied/acknowledged;
- command failed/rejected;
- external controller stopped refreshing commands.

AUTO is the preferred safe fallback for loss of external control unless verified Mitsubishi behavior requires a safer alternative. Document timeout and reboot behavior.

## Pump control research

Pump override is intentionally not part of the mandatory MVP control API yet, but this package must investigate it because it is required for planned experiments.

Determine, with evidence, whether CN105 or an A3/service mechanism permits:
- commanding brine-pump output step/speed;
- commanding heating-water circulation-pump speed/level;
- manual pump operation with compressor off.

Classify each as:
- verified writable;
- verified read-only;
- strong candidate requiring hardware test;
- unsupported/unknown.

Do not transmit speculative pump-write commands on hardware.

Document findings in `procon/docs/PUMPS.md` and update the protocol map.

## Planned experiments this MVP must support

The telemetry/logging API must be sufficient for later read-only analysis of:

1. borehole/brine stress test: both heat pumps operated at high sustained load for hours, observing whether brine temperature decline is smooth or has identifiable knees/regime changes;
2. hydraulic interaction: investigate whether brine can circulate through an inactive heat pump;
3. heat-output characterization: vary supported flow-temperature target and measure resulting thermal kW;
4. heating-water pump/COP characterization once safe pump control is verified; Shelly supplies electrical power and computes COP.

Do not implement autonomous test routines that defeat Mitsubishi protections.

## Evidence basis

Project documentation already supports:
- TH32 = brine inlet and TH34 = brine outlet;
- P0071 hardware-confirmed A3 service sequencing behavior;
- compressor frequency;
- flow/return temperatures;
- primary flow sensor existence and use in delivered-heat calculation;
- brine-pump output step 0-10 as an internal service/display quantity;
- Mitsubishi heating flow target and DHW target concepts.

Use the existing procon documentation and P0069-P0071 evidence as authoritative project context. Clearly distinguish direct protocol evidence from service-manual evidence and hypotheses.

## Regression requirements

Must not regress:
- Modbus input0 = 888;
- existing register addresses unless explicitly versioned/migrated;
- heartbeat;
- compressor telemetry;
- A3/27 and A3/28 completed brine reads;
- exclusive service retry rule;
- watchdog;
- CN105 recovery;
- deterministic build/image checks;
- immutable original firmware.

Add automated tests for:
- alternating service scheduler 27/28;
- proof that no FAST request occurs inside an active service retry sequence;
- freshness/invalid propagation;
- thermal-power arithmetic, scaling, sign and overflow boundaries;
- mode command validation;
- flow/DHW target range validation;
- command acknowledgement/sequence behavior;
- lease expiry/fallback;
- concurrent Modbus reads during active A3 operation;
- continued watchdog/heartbeat behavior.

## Hardware validation

Operator alone flashes.

Read-only validation first:
- all available MVP values plausibility-checked against controller/service display where possible;
- brine 27/28 continue completing;
- compressor remains live;
- thermal-power inputs and calculated result logged;
- no CN105/UART regression.

Control validation only after read telemetry passes. Test one command dimension at a time with conservative values:
- AUTO/OFF behavior;
- FIXED_FLOW with a safe target;
- return to AUTO;
- DHW request;
- DHW target;
- lease/fallback.

Do not test speculative pump writes under this package.

Maximum three hardware debug attempts before reassessing assumptions.

## Deliverables

Update source, tests, release artifacts and living documentation in the existing Smart Home repository. Add/update:
- stable Modbus register map;
- mode/command semantics;
- thermal-power formula and scaling;
- `procon/docs/PUMPS.md`;
- CN105 direct-vs-service protocol map;
- hardware evidence;
- BIN/ELF/MAP/disassembly/SHA256 and deterministic rebuild verification.

No unrelated Shelly/G2 runtime changes.
