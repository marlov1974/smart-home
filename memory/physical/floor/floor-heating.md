# Floor Heating

## Scope

Physical and control-relevant facts about floor heating belong here.

## Design status

There is no final G2 room-level floor-control design yet.

Current documentation separates:

- existing physical/control baseline
- operator design ideas
- open design decisions

Do not treat the bedroom-control ideas below as implemented G2 behavior until a later design/package makes them concrete.

## Existing room-control baseline

The existing floor room-control solution is a Siemens solution:

```text
Room thermostats: Siemens room thermostats
Room control capability: heating and cooling logic
Valve control: Siemens 0-10 V valves
Remote setpoint control: not available
```

Each room temperature is manually set on the room thermostat.

The current Siemens room thermostats cannot be remotely controlled by G2.

## Current design idea for general rooms

Design idea:

Keep the old Siemens room-control solution in the general rooms:

```text
- kitchen
- living room
- TV room
- hall
- laundry room
- corridor
```

Operating idea:

- in winter, manually set the room thermostats slightly high
- in summer, manually set the room thermostats slightly low
- then let the heat pump / floor-cooling system control these rooms globally through source temperature, operating windows and mode selection

Interpretation:

The general rooms remain locally/manual-set rooms. G2 should mainly influence them through the global heating/cooling supply behavior, not by remote room setpoint changes.

## Current design idea for bedrooms

Bedrooms have more fine-grained comfort requirements than the general rooms.

Design idea:

Replace bedroom room-control hardware with equipment that G2 can control remotely.

Winter behavior idea:

- bedrooms are normally kept a little cooler than general rooms
- bedrooms are warmed after midnight
- goal: cool when going to sleep, warm when waking up
- secondary goal: avoid expensive daytime heating by shifting some bedroom heat into cheaper night periods

Summer behavior idea:

- bedrooms should generally be cold/cool around the clock
- bedroom summer comfort is more important than using the same thermal-mass strategy as general rooms

Design implication:

Bedroom control likely needs separate controllable actuators/thermostats/sensors from the existing Siemens manual thermostats.

## Five heating/cooling loops context

The house has five relevant heating/cooling loops:

1. FTX cooling coil
2. FTX heating coil
3. bathroom floor heating loop
4. rest-of-house floor loop, switchable between heating and cooling
5. brine loop for floor cooling

This file focuses on the floor-heating parts of that topology.

## Functional roles

Bathroom floor loop:

- always heating
- primary purpose is bathroom comfort
- contributes a little to the house heat-energy battery

Rest-of-house floor loop:

- primary house heater when it is cold
- primary house cooler when it is warm
- primary actuator for using the house thermal mass as an energy battery
- can switch between heat-pump/heating side and floor-cooling automation side

FTX heating coil:

- secondary house heater
- can heat quickly
- can act as counter-heater against the FTX cooling coil when the system wants to dry the house without cooling it down
- primary focus is comfort rather than slow thermal storage

FTX cooling coil:

- primarily for air humidity and air-temperature comfort
- has limited ability to cool the house mass or store cooling

## Bathroom floor heating loop

Known facts:

```text
Loop: bathroom floor heating
Connection: parallel with other heating loops
Heat source: always connected to the heat-pump/heating side
```

Control/topology implication:

The bathroom floor heating loop is not part of the floor-cooling source switching. It remains a heating-side loop.

## Rest-of-house floor loop in heating mode

Known facts:

```text
Loop: rest-of-house floor loop
Heating connection: heat-pump/heating side
Cooling connection: floor-cooling automation side
Mode switching: via three-way valve
```

In heating mode, the rest-of-house floor loop is connected to the heat-pump/heating side.

In cooling mode, it is switched away from the heat-pump/heating side and connected to the floor-cooling automation.

The three-way valve that switches this loop should be controlled by the floor-cooling automation.

## Relation to FTX heating coil

The FTX heating coil is always connected to the heat-pump/heating side, in parallel with the other heating loops.

FTX can choose to use or not use the heating coil through its own shunt.

## Open gaps

Known remaining gaps:

- final G2 room-level floor-control design
- bedroom replacement thermostat/actuator/sensor hardware
- mapping from existing Siemens thermostats to rooms/zones
- bathroom floor loop pump/valve/shunt identities, if any
- rest-of-house floor-loop pump identity
- three-way valve hardware identity
- floor-cooling automation hardware
- valve/switch states
- analog outputs
- Shelly device mappings
- Home Assistant entities
- fallback/default behavior
- interaction with heat-pump planner

## Source

Physical topology and loop role details added from operator-provided hardware knowledge during direct documentation update.

Existing Siemens room-control baseline and room-level design ideas added from operator-provided hardware/design knowledge during direct documentation update.
