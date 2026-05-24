# Heat Pumps

## Physical units

The house has two physically identical ground-source heat pumps:

```text
Manufacturer: Mitsubishi
Product family/model: Ecodan ground-source heat pump / bergvärme
Quantity: 2
```

The two heat pumps have different operational roles in the control model, but the underlying hardware is treated as identical unless future nameplate/manual data proves otherwise.

Known capacity note:

```text
Manual nominal/max value: 11 kW
Observed/practical peak capability: about 16 kW
```

Interpretation:

Mitsubishi appears to rate the unit conservatively compared with practical observed peak behavior. Treat `11 kW` as the documented/manual capacity value and `16 kW` as a short-term peak capability, not as a confirmed sustainable average-day output.

Planning implication:

- use conservative capacity assumptions for daily energy planning
- do not assume 16 kW is continuously available over a full day
- peak/recovery logic may use the higher observed capability only with caution and future calibration

Open details:

- exact Mitsubishi Ecodan model designation / nameplate
- whether manual `11 kW` refers to nominal, maximum, or sustainable continuous output under specified brine/flow conditions
- measured duration for observed/practical 16 kW peak behavior

## Physical command model

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

Physical unit identity and capacity notes added from operator-provided hardware knowledge during direct documentation update.
