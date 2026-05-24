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

## Floor-cooling hardware controllers

### Shelly Pro Dimmer 0-10V

Known controlled hardware:

```text
Device type: Shelly Pro Dimmer 0-10V
Analog output: 0-10 V
Analog actuator: Siemens SAS61.03 valve actuator
Switch output: floor-loop pump ON/OFF
Floor-loop pump: Wilo Yonos PICO 25/1-8
```

Function:

- the 0-10 V output controls a Siemens SAS61.03 valve as part of the floor-cooling shunt
- the shunt mixes brine until the floor-water side reaches the desired temperature
- the switch output turns the pump on/off that sends water through the rest-of-house floor loop

Control note:

The floor-loop pump should not start before the three-way valve has opened into the intended cooling path. This is one reason the hardware/control split is intentionally cautious even though it mixes brine-side and floor-side responsibilities across Shelly devices.

### Shelly Pro 2 for three-way valve and brine pump

Known controlled hardware:

```text
Device type: Shelly Pro 2
Output 1: drive three-way valve toward heating mode
Output 2: drive three-way valve toward cooling mode
Three-way valve motor: probably ESBE ARA661
Output 2 also starts brine pump
Brine pump: Grundfos MAGNA3 32-100 180
```

Function:

- the three-way valve switches the rest-of-house floor loop between heating-side connection and floor-cooling connection
- output 1 drives/commands the valve toward heat
- output 2 drives/commands the valve toward cooling
- output 2 also starts the brine pump for the brine shunt

Design caveat:

The solution intentionally mixes brine handling and floor-loop handling between Shelly devices. This is because the floor-loop pump should wait until the three-way valve is open, which takes roughly one minute.

## Three-way valve for rest-of-house floor loop

Known facts:

```text
Function: switch rest-of-house floor loop between heating and floor-cooling automation
Control owner: floor-cooling automation
Valve motor: probably ESBE ARA661
Controller: Shelly Pro 2
```

Mode semantics:

```text
heating mode = floor loop connected to heat-pump/heating side
cooling mode = floor loop connected to floor-cooling automation side
```

Design implication:

This valve is safety-critical for mode selection. G2 must verify final hardware identity, wiring and timing before live control.

## Rest-of-house floor-loop pump

Known facts:

```text
Dedicated pump: yes
Pump: Wilo Yonos PICO 25/1-8
Controller: Shelly Pro Dimmer 0-10V switch output
Loop: rest-of-house floor loop
Purpose: circulate floor water during cooling mode
```

Reason:

When floor cooling is active, the heat-pump pumps are disconnected from the rest-of-house floor loop, so this loop needs its own pump.

## Brine loop for floor cooling

Known facts:

```text
Dedicated brine-side pump: yes
Brine pump: Grundfos MAGNA3 32-100 180
Brine pump controller: Shelly Pro 2 output 2
Dedicated shunt/mixing solution: yes
Valve actuator: Siemens SAS61.03
Valve actuator controller: Shelly Pro Dimmer 0-10V analog output
Purpose: mix brine until floor-water temperature reaches the desired cooling temperature
```

Control implication:

The floor-cooling automation must coordinate:

- brine-side pump
- shunt/mixing output
- rest-of-house floor-loop pump
- three-way mode valve
- valve timing delay before floor pump start
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

## Heat-pump and hot-water controller notes

Heat pumps:

- VP control will use two Shelly Pro 2 devices
- one unit will also have a Shelly Pro Sensor Add-on
- the Sensor Add-on will measure temperatures related to floor cooling, floor heating, VP water tanks and in/out temperatures for heat pumps and boreholes
- if useful VP digital outputs are available, the Sensor Add-on digital inputs may read them

Hot water:

- NIBE ES23-300 VVB will be controlled by a Shelly Pro 2PM
- VVC will be switched on/off together with the VVB control

## Open gaps

Known remaining gaps:

- confirmed three-way valve identity; likely ESBE ARA661
- final Shelly device names and IDs
- final relay/channel mapping
- timing requirement for valve-open delay before floor pump start
- Sensor Add-on temperature sensor list and IDs
- VP digital output availability and semantics
- Home Assistant entities
- safe default mode
- heating/cooling mode semantics at relay/channel level

## Source

Physical topology and hardware details added from operator-provided hardware knowledge during direct documentation update.
