# FTX Physical Devices

## Aggregate

Physical FTX unit:

```text
Karfax TOPIC-12
```

Known major functions:

- supply fan
- extract fan
- rotating heat exchanger / VVX
- heating battery
- cooling battery
- dampers
- condensate drain/tray

## Rotating heat exchanger / VVX

Identified rotating heat exchanger:

```text
Heatex WA0540V-200-020-200-0-220
```

VVX is currently treated as on/off control.

## VVX motor

Identified motor/gearbox:

```text
Manufacturer: Japan Servo Co., Ltd.
Series: H MKII
Gearbox: 8H12.5FBN-2
Gear ratio: 12.5:1
Motor: IHT8PF25N-1
Type: geared induction motor
Power: 25 W
Voltage: 220 V AC
Current: 0.28 A
Frequency: 50 Hz
Duty: continuous
Run capacitor: 12 uF
```

Control implication:

```text
Treat as AC on/off unless future hardware proves safe variable-speed operation.
```

## EC fans

Installed fans:

```text
Supply fan:  ebm-papst RadiCal K3G250-RE07-07
Extract fan: ebm-papst RadiCal K3G250-RE09-07
```

Known facts:

- EC fans
- 0-10 V / dimmer percentage speed control in digital model
- tach output is open collector
- tach output gives 1 pulse per revolution

## Dampers

Identified damper actuator:

```text
Siemens GCA121.1E
Supply: 24 V AC +/-20%, 50/60 Hz
Power: 8 VA
Spring return: yes
Type: NC
Torque: 16 Nm
Runtime motor: 90 s
Runtime spring return: 15 s
```

Supply and extract dampers are wired/controlled together as one actuator group in the current digital model.

## Heating and cooling valve actuators

Identified actuator:

```text
Siemens Building Technologies SSB61
Supply: AC 24 V +/-20%, 50/60 Hz
Control signal: DC 0-10 V
Power: 2.5 VA
Runtime: 150 s
```

Role mapping from physical appearance:

```text
Cooling actuator: clean SSB61 actuator
Heating actuator: dirty SSB61 actuator
```

## Source

Imported from G1 `memory/ftx-fysiskt/01-system-overview.md` and `02-hardware-inventory.md` during `P0002`.
