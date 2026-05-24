# Hot Water / VVB / VVC Baseline

## Scope

Domestic hot water, VVB and VVC physical/system knowledge.

## Hardware

Known VVB hardware:

```text
VVB: NIBE ES23-300
Controller: Shelly Pro 2PM
```

Known VVC control:

```text
VVC is switched on/off together with the VVB control.
```

## Serial hot-water topology

Domestic hot water is serial through VP1, VP2 and VVB:

```text
street cold water -> VP1 -> VP2 -> VVB -> house hot water/VVC
```

## VP1 hot-water role

VP1 takes the first hit from cold street water.

Known control intent:

```text
VP1 makes domestic hot water only during 00-02.
```

Purpose:

- use the protected/sacred night block for VP1 DHW recovery
- avoid uncontrolled daytime hot-water production when energy optimization prefers otherwise

## VP2 hot-water role

VP2 is the next stage after VP1.

Known control intent:

```text
VP2 always has domestic hot-water production enabled.
```

Purpose:

- protect the final VVB from cold incoming water
- normally deliver about 50 C water toward the VVB

## VVB role

The VVB is the final stage.

Known role:

```text
VVB target/function: afterheat water to about 60 C
```

The VVB should mainly heat:

- its own standing losses
- VVC losses
- the final lift from about VP2 50 C to about 60 C

It should not normally be the primary heater from cold water.

## Hot-water system as energy storage

VP1, VP2 and VVB together create large domestic hot-water volume.

Planning principle:

- accept different available hot-water amounts at different times of day and week
- optimize energy cost by charging and discharging the hot-water stores intentionally
- treat the hot-water system as a set of energy batteries that can be charged and discharged

## Current imported baseline

VP1 has a daily sacred opportunity to restore its domestic-hot-water tank:

```text
00-02
```

In summer, the protected low operating level is intended to let VP1 handle domestic hot water without meaningful house-heating intent:

```text
VP1 20/52
```

VP2 low/base support can be:

```text
VP2 28/52
```

## Open gaps

Known remaining gaps:

- final Shelly Pro 2PM device identity and channel mapping
- exact VVC electrical/control mapping
- VVC schedule/default behavior
- temperature sensors and IDs
- Home Assistant integration points
- fallback/default behavior
- interaction with heat-pump planner

## Source

Imported from G1 heat-pump operating schedule memory during `P0002`.

Serial hot-water topology, VVB hardware and energy-storage role added from operator-provided hardware knowledge during direct documentation update.
