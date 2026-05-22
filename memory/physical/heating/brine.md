# Brine / Borehole Planning Baseline

## Brine temperature by heat-pump load

Observed practical planning model:

```text
Light heat-pump operation:
  borehole/brine temperature about 6-8 C

Medium heat-pump operation:
  borehole/brine temperature about 3-4 C

Hard heat-pump operation:
  borehole/brine temperature about 2-3 C
```

## Planning interpretation

Higher heat-pump load pulls borehole/brine temperature down.

Lower brine temperature reduces effective heat-pump efficiency.

A very cheap price block is not automatically optimal if it requires heavy operation that depresses brine temperature and reduces efficiency across the period.

## Summer brine reference

When brine is used for cooling/free-cooling behavior in warm periods, the planning reference is often about:

```text
brine = 8 C
```

This value should be treated as a practical planning boundary until calibrated with G2 measurements.

## Measurement principle

Brine-related decisions must distinguish:

- brine before shunt/blending
- brine after cooling shunt toward cooling battery
- resulting cooling surface/floor/coil temperature

## Source

Imported from G1 heat-pump schedule memory and later project discussion during `P0002`.
