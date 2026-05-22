# FTX Airflow and Pressure Model

## Core relation

Airflow is estimated from pressure using an empirical K-factor model:

```text
lps = K * sqrt(Pa)
```

Current practical constants:

```text
K_SUPPLY_FAN = 11.6
K_EXTRACT_FAN = 12.1
```

These are operational calibration constants, not universal fan or duct constants.

## Fan balance

Current documented normal operation rule:

```text
supply_pct = round(0.9 * extract_pct - 1)
```

Equivalent supply-primary relation used in later G1 notes:

```text
extract_pct = round((supply_pct + 1) / 0.9)
```

Explicit overpressure/fireplace modes may override normal balancing.

## Run thresholds

Canonical fan run semantics from G1:

```text
fan.run = 1 iff switch = 1 and pct > 10 and rpm > 250
```

## Capacity references

Historical maximum airflow with old fans, clean filters and open terminals:

```text
about 300 l/s
```

Current practical maximum after modifications:

```text
about 250 l/s
```

## Measurement caution

Pressure measurements must be tied to physical point and method.

Do not mix:

- pressure at measurement port/stoss
- pressure across fan
- duct/static pressure
- house differential pressure

## Source

Imported from G1 `memory/ftx-fysiskt/03-airflow-and-pressure-model.md`, `04-fans-and-flow-calibration.md` and `13-baseline-measurements.md` during `P0002`.
