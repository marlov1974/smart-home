# Floor Shunts, Pumps and Valves

## Scope

Physical facts about floor-side shunts, pumps, valves and mode switching belong here.

## Five heating/cooling loops context

The house has five relevant heating/cooling loops:

1. FTX cooling coil
2. FTX heating coil
3. bathroom floor heating loop
4. rest-of-house floor loop, switchable between heating and cooling
5. brine loop for floor cooling

## Three-way valve for rest-of-house floor loop

Known facts:

```text
Function: switch rest-of-house floor loop between heating and floor-cooling automation
Control owner: floor-cooling automation
Hardware identity: to be documented later
```

Mode semantics:

```text
heating mode = floor loop connected to heat-pump/heating side
cooling mode = floor loop connected to floor-cooling automation side
```

Design implication:

This valve is safety-critical for mode selection. G2 must not assume a relay/channel mapping until the actual hardware and wiring are documented.

## Rest-of-house floor-loop pump

Known facts:

```text
Dedicated pump: yes
Loop: rest-of-house floor loop
Purpose: circulate floor water during cooling mode
```

Reason:

When floor cooling is active, the heat-pump pumps are disconnected from the rest-of-house floor loop, so this loop needs its own pump.

Hardware identity and control mapping are still open.

## Brine loop for floor cooling

Known facts:

```text
Dedicated brine-side pump: yes
Dedicated shunt/mixing solution: yes
Purpose: mix brine until floor-water temperature reaches the desired cooling temperature
```

Control implication:

The floor-cooling automation must coordinate:

- brine-side pump
- shunt/mixing position or output
- rest-of-house floor-loop pump
- three-way mode valve
- dewpoint/condensation safety

## FTX shunts in the five-loop topology

FTX cooling coil:

- directly connected to brine before the heat pumps
- semi-parallel with the heat-pump brine path
- brine does not have to pass the FTX cooling coil for the heat pumps to receive brine
- FTX controls its own cooling-coil shunt

FTX heating coil:

- always connected to the heat-pump/heating side
- parallel with the other heating loops
- FTX controls whether to use it through its own heating-coil shunt

## Open gaps

Known remaining gaps:

- three-way valve identity
- rest-of-house floor-loop pump identity
- brine-loop pump identity
- shunt/mixing hardware identity
- valve/switch states
- analog outputs
- Shelly device mappings
- Home Assistant entities
- safe default mode
- heating/cooling mode semantics at relay/channel level

## Source

Physical topology added from operator-provided hardware knowledge during direct documentation update.
