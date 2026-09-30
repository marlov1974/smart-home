# Package P0068: P3 office autonomous L1/L2 floor-heating pilot

## Status
planned

## Package order
P0068

## Primary area
G2 / Shelly / floor heating / room control

## Label
G2

## Linked requirements

Epic:
- E_ROOM_CLIMATE

Features:
- F_LOCAL_ADAPTIVE_FLOOR_HEAT

User stories:
- US_P3_OFFICE_22C_AUTONOMOUS

## Decision summary

P3 office is the first G2 room-level floor-heating pilot.

The room shall initially control itself to a fixed comfort target of:

```text
22.0 °C
```

The first implementation shall use a two-layer control model:

```text
L1 = deterministic local room controller
L2 = slow adaptive room learner / predictor
```

L1 is authoritative for actuation and must work without Mac, Home Assistant, cloud services or L2.

L2 shall initially run in shadow/learning mode. It may observe L1, room temperature and other allowed local context, but it must not independently change the actuator or target in P0068.

The purpose of P0068 is therefore both:

1. make the office independently hold approximately 22 °C using local floor heat; and
2. begin learning the real thermal behavior of this room so a later package can add predictive/feed-forward optimization.

## Room and hardware facts

Operator-confirmed room facts:

```text
Room: P3 office / "P3 Kontor"
Floor: top floor
Windows: north-facing
External walls: north and west
Initial target: 22.0 °C
```

These geometry/orientation facts are metadata and useful priors. They must not be converted into arbitrary hard-coded thermal corrections. The learned model must be based on measured room response.

Current Shelly UI evidence supplied by the operator:

```text
Shelly display name: P3 Kontor
Device type: Shelly Plus Uni
Device model: SNSN-0043X
Physical Shelly id: e08cfe8c04bc
Observed reachable IP during requirements discussion: 192.168.86.79
Temperature component: temperature:100
Humidity component: humidity:100
Observed example: 20.5 °C / 63.8 %RH
```

The observed IP is reachability evidence only and must not be treated as durable device identity. Live implementation must verify device identity before writes.

The operator states that the Shelly is physically wired for control of the office floor heating. The exact actuator output/component, electrical semantics, polarity, fail-safe state and physical valve behavior are not yet durable repository truth.

P0068 must not actuate until those facts are verified.

## Solution model

### L1: autonomous deterministic room control

L1 owns only the P3 office room-heating actuator/demand.

L1 shall:

- use the local P3 office room temperature as its authoritative comfort input;
- target 22.0 °C;
- run locally on the P3 office Shelly;
- remain functional if Mac, Home Assistant, Internet and other G2 brains are unavailable;
- use slow-control behavior appropriate for hydronic floor heating;
- avoid rapid output chatter;
- start from a safe non-heating state after reboot until a valid room-temperature sample exists;
- fail safe to no heat demand when the authoritative temperature signal is invalid or stale;
- expose enough local state for diagnosis and later Home Assistant integration;
- never command VP1/VP2, global floor supply temperature, floor-cooling mode or other rooms in this package.

L1 must be usable with L2 completely disabled.

### Initial comfort contract

The fixed first target is:

```text
target_c = 22.0
```

The control design should aim for a normal settled comfort band around the target, with an initial engineering objective of approximately:

```text
21.5 °C .. 22.5 °C
```

This is a pilot acceptance objective, not a claim that floor heat can always achieve the target. If usable heating water is unavailable or insufficient, L1 shall saturate safely at its allowed maximum room demand and expose that the target cannot currently be achieved; it shall not escalate to heat-pump/source control in P0068.

The implementation design must define a conservative over-temperature cutout and restart hysteresis. It must not continue requesting heat when the room is clearly above the 22 °C target.

### Actuator abstraction

Before implementation can PASS review, Codex must identify the actual P3 office floor-heating actuator path.

The room controller should reason in normalized demand:

```text
heat_demand = 0.0 .. 1.0
```

The implementation may map that demand to the verified physical interface only after discovery.

Examples of possible physical mappings include proportional or time-proportioned control, but P0068 must not assume one before the live hardware/configuration is verified.

The design must document:

- Shelly output/component id;
- electrical output type;
- whether command polarity is normal or inverted;
- what physical valve state corresponds to no heat;
- actuator travel/response time if relevant;
- safe output on Shelly reboot/script stop;
- whether output feedback exists;
- whether the current Siemens room-control hardware remains electrically in the path.

If any of these are ambiguous enough to risk wrong actuation, review result is STOP until the operator confirms the mapping.

## L2: room-learning shadow layer

L2 shall learn the room online while L1 controls comfort.

P0068 L2 has no actuator authority.

L2 must use a compact, explainable and bounded online model suitable for Shelly memory limits. It must not keep a large raw time-series history on-device.

### Minimum observations

L2 shall be able to learn from local data only:

- room temperature;
- elapsed time;
- L1 heat demand / actuator command;
- valid/stale state.

Relative humidity may be recorded as context but shall not affect P0068 heating control.

Optional external signals such as outdoor temperature, floor supply temperature, weather or whole-house state may be added later, but P0068 learning must continue safely when they are absent.

### Minimum learned properties

The model shall estimate, with confidence/sample metadata where practical:

1. **heat-response rate** — how quickly room temperature tends to rise while heat is applied;
2. **passive loss/cooling rate** — how quickly room temperature tends to fall without room heat;
3. **response delay** — approximate delay between a meaningful actuator change and measurable room response;
4. **post-off thermal tail / overshoot** — continued temperature rise or reduced cooling after heat demand is removed;
5. **time-to-target estimate** — a bounded prediction of how long the room is likely to need to approach 22 °C under comparable conditions;
6. **model confidence / maturity** — enough information to distinguish early guesses from repeated observations.

The exact estimator may be chosen in package design, but it must remain interpretable, numerically bounded and testable.

### Learning safety and persistence

L2 shall:

- ignore invalid/stale temperature periods;
- avoid learning across boot gaps with unknown actuator state;
- avoid treating clearly incomplete short samples as settled room response;
- bound all learned parameters to physically plausible ranges defined in design;
- persist only compact model state and sample/confidence metadata;
- rate-limit persistent writes to protect flash endurance;
- survive reboot without losing all learned state;
- start with low confidence after first deployment;
- never change L1 target or actuator directly in P0068.

A later package may promote selected L2 predictions into L1 feed-forward control only after P0068 evidence shows the learned model is useful.

## Current behavior

G2 has no implemented final room-level floor-control design.

The existing baseline is Siemens room thermostats and Siemens floor-valve control. P3 office now has a Shelly Plus Uni connected for a room-control pilot, but repository truth does not yet define its actuator mapping or runtime behavior.

## Problem

The office currently lacks a G2-owned autonomous room controller.

The house-level/global heating system is too coarse to learn or compensate for the thermal characteristics of this particular room:

- top floor;
- north-facing windows;
- two external walls;
- slow floor-heating dynamics.

A conventional fixed thermostat can hold temperature, but it does not create the measured thermal knowledge needed for later predictive heating, price shifting or coordinated whole-house control.

## Target behavior

After P0068 implementation and successful staged verification:

- P3 office controls its own floor-heating demand locally;
- target is 22.0 °C;
- loss of Mac/HA/Internet does not stop basic room control;
- invalid/stale temperature causes safe no-heat fallback;
- L1 state and L2 learning state are observable;
- L2 learns room dynamics in shadow mode;
- L2 cannot independently actuate;
- no other room, VP, floor-cooling or FTX actuator is changed by this package.

## Non-goals

- No cooling control.
- No dewpoint control.
- No price optimization.
- No weather feed-forward control.
- No occupancy control.
- No scheduling/setback.
- No remote user-adjustable setpoint in the first pilot.
- No control of heat-pump source temperature.
- No control of rest-of-house floor pump/shunt.
- No Home Assistant dashboard work.
- No promotion of L2 to actuator authority.
- No rollout to bedrooms, bathrooms or other rooms.

## Invariants

- L1 must remain locally autonomous.
- L1 must remain deterministic and safe if L2 fails.
- L2 must have zero direct actuator authority in P0068.
- Physical actuator mapping must be verified before writes.
- Device identity is the physical Shelly id/logical role, not the current IP.
- No broad cross-device polling is required for basic room control.
- No large on-device raw history.
- Persistent learning writes must be rate-limited.
- Source/build/deploy separation must be preserved.
- Shelly deploy artifacts must come from `dep/s/`, not `src/`.
- Once device identity, actuator mapping, no-heat polarity and fail-safe behavior are verified, P0068 shall proceed to autonomous pilot activation without a separate operator approval prompt.

## Knowledge updates

On successful hardware discovery/implementation, update:

- `memory/infrastructure/devices.md`
  - add logical P3 office floor-controller role and verified physical identity/reachability facts;
- `memory/physical/home/rooms-zones.md`
  - add P3 office geometry/orientation and room-control role;
- `memory/physical/home/comfort-sensors.md`
  - add authoritative P3 office temperature/humidity sensor mapping;
- `memory/physical/floor/floor-heating.md`
  - record P3 office as first concrete G2 room-level L1/L2 pilot and verified actuator mapping;
- `docs/functions/**`
  - document durable L1/L2 runtime functions/contracts when implemented.

Do not record unverified actuator wiring as memory truth.

## Implementation updates

Expected implementation area:

```text
src/shelly/floor/p3-office/**
build/shelly/floor/p3-office/**
dep/s/**
tests/mac/shelly_floor/**
docs/functions/shelly/**
requirements/package-runs/P0068/**
```

Exact source layout may be refined in design, but L1 and L2 responsibilities must remain logically separate even if memory constraints lead to a single built Shelly script.

## Files to inspect

- `AGENTS.md`
- `README.md`
- `memory/bootstrap-manifest.json`
- manifest `read_order`
- `REPOSITORY_FILES.md`
- `memory/02-design-principles.md`
- `memory/05-package-lifecycle.md`
- `memory/06-chatgpt-requirements-analyst.md`
- `memory/device-management/identity-and-registry.md`
- `memory/infrastructure/devices.md`
- `memory/physical/floor/floor-heating.md`
- `memory/physical/floor/shunts-pumps-valves.md`
- `memory/physical/home/rooms-zones.md`
- `memory/physical/home/comfort-sensors.md`
- `memory/knowhow/shelly.md`
- current Shelly build/deploy tooling
- current Shelly Plus Uni live read-only status/config on the P3 office device

## Files allowed to change

- `requirements/packages/P0068-p3-office-autonomous-l1-l2-floor-heating.md`
- `requirements/package-runs/P0068/**`
- `src/shelly/floor/**`
- `build/shelly/floor/**`
- `dep/s/**` only for deterministic P0068 deploy artifacts
- `tests/mac/shelly_floor/**`
- `src/mac/tools/**` only if a small generic deploy/readback extension is strictly required
- `tests/mac/tools/**` only for such a generic tooling extension
- `docs/functions/**`
- `memory/infrastructure/devices.md`
- `memory/physical/home/rooms-zones.md`
- `memory/physical/home/comfort-sensors.md`
- `memory/physical/floor/floor-heating.md`
- `memory/knowhow/**` when reusable lessons are learned
- `memory/bootstrap-manifest.json` if package/status bootstrap context changes
- `REPOSITORY_FILES.md` when tracked paths change

## Forbidden changes

- No FTX runtime changes.
- No VP1/VP2 control changes.
- No VVB/VVC changes.
- No floor-cooling control changes.
- No control of other room valves.
- No Home Assistant changes.
- No G1 repository changes.
- No external cloud/runtime dependency for L1.
- No actuator writes to any device except the verified P3 office floor-heating actuator.
- No activation is allowed while device identity, actuator mapping, polarity or fail-safe behavior remain uncertain.

## Pre-implementation consistency review

Before editing implementation, Codex must verify P0068 against repository truth and live read-only device state.

Review must classify the package:

- `PASS`: device identity, sensor mapping and actuator semantics are sufficiently verified;
- `WARN`: implementable with documented non-safety-critical uncertainty;
- `STOP`: actuator mapping/polarity/fail-safe is ambiguous, target identity is uncertain, or required local sensor data is unavailable.

Store review evidence in:

```text
requirements/package-runs/P0068/review.md
```

The review must include a section named:

```text
P3 office live hardware contract
```

with the verified device, sensors, actuator output and safe-state semantics.

## Implementation design policy

Before coding, create:

```text
requirements/package-runs/P0068/design.md
```

The design must cover:

- L1 control law and timing;
- target/deadband/over-temperature behavior;
- sensor validation and staleness timeout;
- actuator adapter and fail-safe;
- reboot behavior;
- L1 observable state contract;
- L2 estimator choice;
- learned parameter bounds;
- L2 sampling/gating rules;
- persistence schema and flash-write cadence;
- L2 observable state contract;
- script/process split and memory budget;
- live staged-test plan;
- automatic activation/rollback procedure.

## Function design policy

Before coding, create:

```text
requirements/package-runs/P0068/functions.md
```

Document all new/changed functions including:

- sensor read/validation;
- L1 demand calculation;
- actuator application;
- safe-off handling;
- learning sample acceptance;
- incremental model update;
- prediction calculation;
- persistence/load;
- telemetry/state serialization.

If implementation needs materially different responsibilities, update `functions.md` before coding further.

## Live test/debug policy

Live testing allowed:
yes, P3 office Shelly only

Read-only discovery allowed:
yes

Script/config/KVS writes allowed:
only P0068-owned scripts/state on the verified P3 office Shelly

Physical actuator writes allowed:
only after all of the following are true:

1. physical Shelly id is verified as `e08cfe8c04bc`;
2. exact actuator output/component and no-heat polarity are verified;
3. package review is PASS or WARN without actuator-safety uncertainty;
4. Stage A/B verification has completed without actuator-safety uncertainty.

No separate operator approval is required after these conditions are met. No other actuator may be changed.

Shelly log capture required:
yes during staged live test

Max implementation/debug attempts:
3

## Staged live verification

### Stage A: read-only discovery

Verify:

- device identity/model/firmware;
- `temperature:100` and `humidity:100`;
- current script/config state;
- actuator component candidate and configuration;
- memory/heap baseline if exposed.

No actuator write.

### Stage B: controller shadow mode

Run L1 calculation and L2 learning without applying physical output.

Verify:

- temperature validation;
- 22.0 °C target;
- bounded demand;
- stale/invalid fallback state;
- L2 state updates only from accepted samples;
- no output state changes.

### Stage C: bounded actuator proof

Proceed automatically after Stage A/B verification passes and the actuator contract is unambiguous.

Apply a short, bounded room-heating command through only the verified office actuator.

Verify expected physical direction and safe return to no-heat state.

Stop immediately on inverted semantics, unexpected device/output change or uncertain readback.

### Stage D: autonomous pilot activation

Proceed automatically after Stage C verifies the expected physical direction and safe no-heat state.

Enable autonomous L1 at 22.0 °C and L2 shadow learning and leave the pilot active unless a verification or safety check fails.

The final report must state the resulting pilot state.

## Test cases

### TC1: fixed target
Given valid room temperature
When L1 runs
Then its target is exactly 22.0 °C.

### TC2: autonomous local operation
Given Mac, Home Assistant and Internet are unavailable
When the local temperature sensor and actuator are available
Then L1 continues room control.

### TC3: no-heat above target
Given room temperature is clearly above the defined upper comfort/control threshold
When L1 runs
Then room heat demand is zero.

### TC4: demand below target
Given valid room temperature is sufficiently below target and heating source is usable
When L1 runs
Then heat demand increases within configured bounds.

### TC5: stale/invalid sensor fail-safe
Given the authoritative temperature sample is stale or invalid
When L1 runs
Then heat demand becomes zero and a fault/stale state is observable.

### TC6: safe reboot
Given the Shelly/script restarts
When no valid temperature has yet been accepted
Then physical heat demand remains in the verified no-heat state.

### TC7: L2 has no authority
Given any L2 model output
When P0068 runs
Then L2 cannot directly write the actuator or change the 22.0 °C target.

### TC8: learning heat response
Given a valid heating interval with sufficient duration and room response
When L2 updates
Then heat-response statistics move in the observed direction and remain inside defined bounds.

### TC9: learning passive loss
Given a valid non-heating interval
When room temperature falls measurably
Then passive-loss statistics update without creating actuator output.

### TC10: response-delay and tail estimation
Given synthetic/fixture temperature traces with known delay and post-off tail
When L2 processes them
Then estimated delay/tail converge within test tolerances defined in design.

### TC11: persistence
Given learned model state with nonzero confidence
When the script restarts
Then compact model state is restored and L1 still starts safely.

### TC12: persistence rate limit
Given frequent L2 sample updates
When model state changes continuously
Then persistent writes do not exceed the write cadence defined in design.

### TC13: room metadata is not a hard-coded correction
Given north windows, north/west external walls and top-floor metadata
When L1 computes demand
Then those facts do not directly alter target or actuator demand through arbitrary constants.

### TC14: no cross-domain actuation
Given P0068 execution
When reviewed
Then no VP, FTX, floor-cooling, VVB/VVC or other-room actuator writes occurred.

## Verification commands

Codex must define exact commands after design, including equivalents of:

```bash
python3 -m unittest discover tests/mac/shelly_floor
python3 -m unittest discover tests/mac/tools
git diff --check
```

If a Shelly manifest/build role is introduced, also run deterministic build and validate commands through the existing G2 Shelly build tool.

Live evidence must record:

- verified physical Shelly id;
- runtime endpoint used for the execution environment;
- component/status mapping;
- actuator mapping and no-heat polarity;
- shadow-mode output;
- bounded actuator proof result;
- final L1/L2 script state;
- current room temperature/humidity;
- final physical heat-demand state;
- relevant log excerpts;
- whether autonomous pilot activation completed and was left active;
- memory/heap observations if available.

## Runtime health checks

Check for:

- script exceptions;
- unexpected restarts;
- sensor read failures;
- stale sensor loops;
- output chatter;
- actuator commands outside bounds;
- persistent-write spam;
- model parameters reaching bounds repeatedly;
- low/falling heap margin;
- L2 work delaying L1 control;
- any actuator write outside P3 office.

L1 timing and safety always take priority over L2 learning.

## Deployment plan

P0068 is a staged single-room pilot.

Successful repository verification authorizes commit/push.

Live deployment shall proceed through Stages A-D automatically when each preceding stage passes its verification and no actuator-safety uncertainty remains.

The intended successful end state is autonomous L1 control at 22.0 °C with L2 shadow learning left active.

There is no whole-house rollout in P0068.

## Rollback plan

Rollback is a new forward-moving package for repository history.

For immediate live pilot safety, the operator must also have a simple way to disable the P0068 script/control and return the office actuator to the verified no-heat/manual baseline state.

The design must document that immediate operator procedure before Stage C.

## Expected Codex output

- consistency review result: PASS/WARN/STOP;
- P3 office live hardware contract;
- design path;
- functions path;
- verified device identity;
- verified sensor mapping;
- verified actuator mapping and fail-safe semantics;
- L1 control contract;
- L2 model/persistence contract;
- files changed;
- tests run and results;
- staged live actions performed;
- logs/evidence paths;
- autonomous pilot final state;
- knowhow promotion created/updated/skipped;
- commit SHA after push if successful;
- uncertainty and skipped checks;
- diff summary.

## Completion notes

Fill after implementation and pilot verification.
