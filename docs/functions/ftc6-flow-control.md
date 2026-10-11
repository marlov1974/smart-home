# FTC flow-control research — P0087

Package-local offline functions: `evaluate` qualifies a restricted ordinary heating branch; `lookup` reproduces ROM8355A; temperature/error encoders preserve clamps and signed rounding; `pump_step` modelsAF400/AF452; `TimerWord` reproduces generic helper semantics. `replay` accepts only existing private JSONL and emits sanitized transition evidence, never device reads.

[Findings](../../requirements/package-runs/P0087/findings.md), [signal chain](../../requirements/package-runs/P0087/flow-target-trace.md), [EFFECT implications](../../requirements/package-runs/P0087/effect-integration-guidance.md), [reproduction](../../requirements/package-runs/P0087/reproduce.md).

Input profile is20.01 only. Effective3908 differs from fallback390C. Lookup output is temperature-like, notHz. Timers are raw counts; source-board frequency and fixed-flow thermostat are unresolved. Production EFFECT and live interfaces are unchanged.
