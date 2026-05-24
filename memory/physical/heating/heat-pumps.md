# Heat Pumps

## Physical units

The house has two physically identical ground-source heat pumps:

```text
Manufacturer: Mitsubishi Electric
Product name/family: Geodan
Model: EHGT17D-YM9ED
Service ref. from service manual: EHGT17D-YM9ED.UK
Type: ground-source heat pump / bergvärme with integrated DHW tank
Quantity: 2
```

The two heat pumps have different operational roles in the control model, but the underlying hardware is treated as identical unless future nameplate/manual data proves otherwise.

Known capacity note:

```text
Product/manual design value: 11 kW
Observed/practical peak capability: about 16 kW
```

Interpretation:

Mitsubishi appears to rate the unit conservatively compared with practical observed peak behavior. Treat `11 kW` as the documented/design capacity value and `16 kW` as a short-term peak capability, not as a confirmed sustainable average-day output.

Planning implication:

- use conservative capacity assumptions for daily energy planning
- do not assume 16 kW is continuously available over a full day
- peak/recovery logic may use the higher observed capability only with caution and future calibration

Open details:

- exact nameplate text on the installed units
- whether product/manual `11 kW` refers to nominal, maximum, Pdesign, or sustainable continuous output under specified brine/flow conditions
- measured duration for observed/practical 16 kW peak behavior

## Active Geodan facts to remember

These facts are condensed for future control and requirements work.

### Performance / COP

```text
SCOP 35 C, average climate: 5.48, Pdesign 11 kW, A+++
SCOP 55 C, average climate: 4.05, Pdesign 11 kW, A+++
SCOP 35 C, cold climate:   5.86, Pdesign 11 kW, A+++
SCOP 55 C, cold climate:   4.16, Pdesign 11 kW, A+++

COP B0/W35:  11 kW output, 2.48 kW input, COP 4.44
COP B0/W45:  11 kW output, 3.16 kW input, COP 3.48
COP B10/W35: 11 kW output, 1.88 kW input, COP 5.83
COP B10/W45: 11 kW output, 2.56 kW input, COP 4.30

Heating output at B0/W35: 1.5-11 kW
```

Planning interpretation:

- flow temperature matters strongly: B0/W35 is much better than B0/W45
- brine temperature matters strongly: B10/W35 is much better than B0/W35
- avoid unnecessary high flow temperatures when floor heating / thermal storage can accept lower temperature
- heavy operation that drags brine down can reduce effective COP across later blocks

### Hydraulic and operating limits

```text
DHW volume: 170 L
DHW 40 C amount: 241 L
Primary/heating circuit volume inside unit: 5.47 L
Brine circuit volume inside unit: 3.11 L
Refrigerant: R32, charge 0.9 kg

Heating flow temperature operating range: 20-60 C
DHW operating range: 40-60 C
Legionella prevention: 60-70 C
Brine inlet operating range: -8 to +30 C
Minimum brine outlet temperature: -12 C
Ambient/frost-free indoor operating environment: 0-35 C, <=80 %RH

Primary circuit flow range: 7.1-27.7 L/min
Brine circuit flow range: 7.1-27.7 L/min
Swedish product page brine flow min/max: 0.12/0.46 L/s
Primary/heating circuit max pressure: 0.3 MPa / 3 bar
DHW tank pressure relief: 1.0 MPa / 10 bar
```

### Electrical and acoustic facts

```text
Heat pump supply: 3N~, 400 V, 50 Hz
Heat pump breaker: 16 A
Recommended compressor module fuse: 3 x 16 A
Max compressor module operating current: 10 A
Booster heater supply: 3~, 400 V, 50 Hz
Booster heater capacity: 3 kW + 6 kW
Booster heater breaker: 16 A
Optional immersion heater: 1 kW, 230 V
Sound power level @B0/W35: 42 dB(A)
Product page sound power min/nom/max: 33 / 42 / 47 Lw(A)
```

### Built-in components useful for control reasoning

```text
Primary circulation pump: DC motor
Brine circulation pump: DC motor
Sanitary/DHW circulation pump: AC motor
Built-in 3-way valve: heating vs DHW
Flow sensor: primary circuit
Flow switch: brine circuit
Thermistors: flow, return, DHW upper/lower, brine inlet/outlet, refrigerant, ambient, heat sink
High-pressure switch/sensor and pressure sensor in refrigerant circuit
Main remote controller and FTC controller board
```

## Useful Geodan terminals and I/O

This section describes Mitsubishi FTC terminals that may be useful for future integration. It does not mean they are currently wired to G2.

### Signal inputs on TBI terminals

All listed input semantics are from the service manual table.

```text
IN1  TBI.1 7-8  Room thermostat 1 input
IN2  TBI.1 5-6  Flow switch 1 input
IN3  TBI.1 3-4  Flow switch 2 input, Zone1
IN4  TBI.1 1-2  Demand control input
                 OFF/open: Normal
                 ON/short: Heat source OFF or Boiler operation, depending external input setting

IN5  TBI.2 7-8  Outdoor thermostat input
                 OFF/open: Standard operation
                 ON/short: Heater operation or Boiler operation, depending external input setting
IN6  TBI.2 5-6  Room thermostat 2 input
IN7  TBI.2 3-4  Flow switch 3 input, Zone2
IN10 TBI.2 1-2  Heat meter input

IN8  TBI.3 7-8  Electric energy meter 1 input
IN9  TBI.3 5-6  Electric energy meter 2 input
IN11 TBI.3 3-4  spare/unspecified in table
IN12 TBI.3 1-2  Smart Grid Ready input

INA1 TBI.4 1-3 / CN1A  Flow sensor input
OUTA1 TBI.4 7-8       Analog output
```

Practical integration interpretation:

- IN4 Demand control is the cleanest manual-visible binary input for external suppression of heat source operation, if configured appropriately in the Mitsubishi controller.
- IN12 Smart Grid Ready exists and may be a better future integration path for price/energy coordination if its behavior matches house needs after verification.
- IN8/IN9 electric meter inputs and IN10 heat meter input may allow Mitsubishi energy monitor integration, but pulse semantics and current wiring must be verified.
- Room thermostat inputs IN1/IN6 may be useful only if Mitsubishi control mode is intentionally changed; avoid accidental short-cycling.

### Outputs on TBO terminals

```text
OUT1  TBO.1 1-2  Water circulation pump 1 output, Space heating & DHW
OUT2  TBO.1 3-4  Water circulation pump 2 output, Zone1 local supply
OUT3  TBO.1 5-6  Water circulation pump 3 output, Zone2 local supply / 2-way valve 2b depending setup

OUT4  CN851      Built-in 3-way valve output, Heating vs DHW
OUT5             Mixing valve output for 2-zone temperature control; state is stop/open/close
OUT6  CNBH 1-3   Booster heater 1 output
OUT7  CNBH 5-7   Booster heater 2 output
OUT8  TBO.4 7-8  Signal output, Cooling
OUT9  TBO.4 5-6  Immersion heater output
OUT10 TBO.3 1-2  Boiler output
OUT11 TBO.3 5-6  Error output
OUT13 TBO.4 3-4  2-way valve 2a output
OUT14 CNP4       Water circulation pump 4 output, DHW
OUT15 TBO.4 1-2  Compressor ON signal
OUT16 TBO.3 3-4  Heating thermo ON signal
```

Practical integration interpretation:

- OUT15 Compressor ON and OUT16 Heating thermo ON are useful non-invasive status outputs if available/wired.
- OUT11 Error output may be useful for G2 fault awareness.
- OUT8 Cooling output and OUT5 mixing valve output are interesting for floor cooling / 2-zone work but must not be assumed wired.
- OUT10 Boiler output may be repurposable only if Mitsubishi configuration intentionally uses boiler mode; do not assume safe.

### Service/request values useful for diagnostics

```text
Request 1: compressor RMS current
Request 16: compressor operating frequency
Request 17: compressor target frequency
Request 18: brine pump output step
Request 19: brine pump speed rpm
Request 25: primary current
Request 27: brine inlet temperature TH32
Request 28: brine outlet temperature TH34
Request 48: thermostat ON operating time
Request 54: actuator output state
Request 176: FTC input signal information
Request 175: FTC output signal information
Request 504-535: FTC thermistor readings including zones, flow/return, DHW, brine and mixing tank
Request 540: primary circuit flow rate
Request 571: flow rate at time of error
```

These are available through the Mitsubishi main remote controller running-information/request-code system, not yet through a known G2 digital integration.

## Physical command model currently used by house control

Each heat pump is controlled through two external digital inputs.

The two inputs form a 2-bit command code:

```text
00
01
10
11
```

Notation:

```text
flow_temperature / domestic_hot_water_temperature
```

Example:

```text
30/32 = 30 C flow temperature and 32 C domestic hot water target
```

Open mapping detail:

The existing house-specific 2-bit command model may be implemented via Mitsubishi external inputs/settings rather than directly matching the generic IN4/IN5 descriptions above. Before changing hardware or software, verify actual wiring from Shelly/relay outputs to the Geodan/FTC terminals on VP1 and VP2.

## VP1 command mapping

```text
00 = 30/32
10 = 20/52
01 = OFF
11 = 36/52
```

Interpretation:

- `00` = low / efficient heating operation
- `10` = near domestic-hot-water-priority mode
- `01` = heat pump off
- `11` = aggressive charging / high heat + high domestic hot water

VP1 is primarily treated as:

- low-temperature machine
- efficient base-load heat pump
- everyday heating machine
- domestic-hot-water-oriented machine through `20/52`

## VP2 command mapping

```text
00 = 28/52
10 = 32/52
01 = UNUSED
11 = 36/52
```

Interpretation:

- `00` = efficient base operation with low flow temperature and high domestic hot water target
- `10` = medium heating level
- `01` = unused / reserve
- `11` = max / boost mode

VP2 is primarily treated as:

- boost machine
- top-load heat pump
- pool / warm-water charging machine
- aggressive recovery machine after thermal deficit

## Idle power

Each heat pump draws approximately 50 W even when it is not actively producing heat, as long as it is powered/awake in a resting state.

Planning values:

```text
VP_IDLE_W = 50 W per heat pump
VP_IDLE_BOTH_W = 100 W for two heat pumps
```

## Logical winter operating levels

```text
L0 = OFF
L1 = 0/28
L2 = 0/32
L3 = 30/28
L4 = 30/32
L5 = 36/36
```

Interpretation:

- `L1 / L2` = efficient low-power maintenance
- `L3` = economy heating
- `L4` = normal winter charging / recovery
- `L5` = aggressive recovery / boost

## Summer hot-water offset trick

Summer lowest active level:

```text
L0 = VP1 20/52 + VP2 28/52
```

Purpose:

- keep sacred 00-02 block for VP1 domestic hot-water recovery
- prevent VP1 from accidentally producing house heat during summer hot-water recovery

Important rule:

```text
Summer L0 must not be accidentally upgraded by monotonic level-upgrade logic.
```

## Daily blocks

Planning resolution:

```text
2h blocks
```

Day blocks:

```text
1  = 00-02
2  = 02-04
3  = 04-06
4  = 06-08
5  = 08-10
6  = 10-12
7  = 12-14
8  = 14-16
9  = 16-18
10 = 18-20
11 = 20-22
12 = 22-24
```

## Sacred block

Only one block is sacred:

```text
Block 1 = 00-02
```

Purpose:

- give VP1 a daily opportunity to restore / charge its domestic-hot-water tank
- provide a stable night recovery opportunity independent of spot optimization

## Source

Imported from G1 `memory/house-control/02-heat-pump-operating-schedules.md` during `P0002`.

Physical unit identity and initial capacity notes added from operator-provided hardware knowledge during direct documentation update.

Geodan model/specification, COP/SCOP, operating limits and terminal notes condensed from Mitsubishi Electric product page for `EHGT17D-YM9ED` and uploaded service manual `Geodan SER.pdf` during direct documentation update.
