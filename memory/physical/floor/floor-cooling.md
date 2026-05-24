# Floor Cooling

## Scope

Physical and control-relevant facts about floor cooling belong here.

## Five heating/cooling loops context

The house has five relevant heating/cooling loops:

1. FTX cooling coil
2. FTX heating coil
3. bathroom floor heating loop
4. rest-of-house floor loop, switchable between heating and cooling
5. brine loop for floor cooling

This file focuses on the floor-cooling parts of that topology.

## Rest-of-house floor loop

The rest-of-house floor loop can switch between two sources:

```text
heating mode: connected to the heat-pump/heating side
cooling mode: connected to the floor-cooling automation
```

A three-way valve changes this loop between heat-pump connection and floor-cooling automation connection.

Control ownership:

```text
The three-way valve should be controlled by the floor-cooling automation.
```

Hardware status:

```text
Three-way valve hardware/control hardware: to be documented later
```

Pump fact:

```text
The rest-of-house floor loop has its own circulation pump.
```

Reason:

When the system runs floor cooling, the heat-pump pumps are disconnected from this floor loop. The floor loop therefore needs its own pump to circulate cooling water through the house.

## Brine loop for floor cooling

There is a dedicated brine loop for floor cooling.

Known facts:

```text
Dedicated brine-side pump: yes
Dedicated shunt/mixing solution: yes
```

Purpose:

The shunt solution mixes brine until the floor-water side reaches the desired cooling temperature.

Control implication:

The floor-cooling automation must control the brine-side pump and shunt/mixing solution so floor-water temperature stays above condensation-safe limits while still providing useful cooling.

## Relation to FTX cooling coil

The FTX cooling coil is also connected to brine before the heat pumps, but it is a separate consumer from the floor-cooling brine loop.

The FTX cooling coil is semi-parallel with the heat-pump brine path:

- it can take/return brine before the heat pumps
- the brine does not have to pass the FTX cooling coil for the heat pumps to receive brine
- FTX controls its own cooling-coil shunt

## Known design concern

Floor cooling must be coordinated with dewpoint and moisture/condensation safety.

FTX cooling/dehumidification may help keep the house dry enough for floor cooling to run safely, but exact coordination belongs to later G2 design packages.

## Open gaps

Known remaining gaps:

- three-way valve hardware identity
- floor-cooling automation hardware
- floor-loop pump identity
- brine-loop pump identity
- shunt/mixing hardware identity
- valve/switch states
- analog outputs
- Shelly device mappings
- Home Assistant entities
- floor temperature sensors
- house dewpoint sensors/entities
- fallback/default behavior
- condensation safety limits

## Source

Physical topology added from operator-provided hardware knowledge during direct documentation update.
