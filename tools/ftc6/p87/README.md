# P87 offline native-control research

Pure Python partial FTC20.01 lookup, encoding, pump-selection and timer-word model. `evaluate()` accepts already selected heating inputs; it does not send commands, simulate a compressor or predict thermostat state. Unqualified paths return UNKNOWN. Run tests and scenarios using [reproduction instructions](../../../requirements/package-runs/P0087/reproduce.md). Evidence and limitations are in [findings](../../../requirements/package-runs/P0087/findings.md).
