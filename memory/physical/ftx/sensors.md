# FTX Sensors

This file maps FTX sensor roles to known Shelly/UNI device sources.

Device identity and reachability are defined in:

```text
memory/infrastructure/devices.md
```

## Supply UNI

Device:

```text
ftx-supply-uni / 192.168.77.20
```

Known imported roles:

- supply-side pressure / Pa
- outdoor or supply air before VVX proxy
- supply air after VVX
- supply fan RPM

## Extract UNI

Device:

```text
ftx-extract-uni / 192.168.77.21
```

Known imported roles:

- extract-side pressure / Pa
- extract/house air before VVX
- exhaust/to-outdoor temperature after VVX
- extract fan RPM

## Process UNI

Device:

```text
ftx-process-uni / 192.168.77.22
```

Known imported roles:

- house CO2/VOC ppm-equivalent input
- house relative humidity
- VVX RPM
- supply air to house after battery
- brine reference
- brine after cooling shunt
- hot water / heating water reference
- hot water after heating shunt

## Air quality sensor

Identified sensor:

```text
Siemens QPM2102
```

Known behavior:

The air-quality signal can report high ppm-like values from VOC events, not only human CO2.

Known triggers include:

- hair spray
- perfume
- ethanol/brine spill

Control implication:

Do not treat all high ppm readings as occupancy-driven CO2.

## Source

Imported from G1 `memory/ftx-fysiskt/02-hardware-inventory.md` during `P0002`.
