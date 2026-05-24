# Floor Heating

## Scope

Physical and control-relevant facts about floor heating belong here.

## Five heating/cooling loops context

The house has five relevant heating/cooling loops:

1. FTX cooling coil
2. FTX heating coil
3. bathroom floor heating loop
4. rest-of-house floor loop, switchable between heating and cooling
5. brine loop for floor cooling

This file focuses on the floor-heating parts of that topology.

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

The three-way valve that switches this loop should be controlled by the floor-cooling automation. Hardware details will be documented later.

## Relation to FTX heating coil

The FTX heating coil is always connected to the heat-pump/heating side, in parallel with the other heating loops.

FTX can choose to use or not use the heating coil through its own shunt.

## Open gaps

Known remaining gaps:

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

Physical topology added from operator-provided hardware knowledge during direct documentation update.
