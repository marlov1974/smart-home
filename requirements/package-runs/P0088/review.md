# P0088 review

2026-10-11: user explicitly pauses P87 and orders the new package. Fetched origin; clean main7d9a919, manifest33. Active-thread package bootstrap applies. P88 authorizes offline enumeration, tools/tests/reports and scoped commit/push only. No device/network discovery, hardware reads/writes, actuation or deployment. Prior P86/P87 outputs and production modules are read-only. Separate P88 Ghidra project copied from the clean P87 final project; no earlier project is written.

PASS for offline scope. Critical risks: incomplete indirect-table coverage, confusing software path with physical connector, false semantic closure from UNKNOWN rows, and known M16C EXITD/bit-FB decoder defects. Assembly operands and explicit table bounds remain primary. Hardware attribution may remain qualified while software enumeration proceeds.
