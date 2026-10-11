# FTC6 display/CN105 research

Last changed: P0084.

`tools/ftc6/p84/` adds bounded local relative-switch reconstruction and compact hash-qualified evidence extraction. Function contracts and tests are in [P84 functions](../../requirements/package-runs/P0084/functions.md); commands and required private inputs are in [reproduction](../../requirements/package-runs/P0084/reproduce.md).

These tools produce research evidence, not a live control API. Full Ghidra exports remain private. Use exact image identity and assembly operands; never infer connector identity from shared service code or latency. A staged field write is not a validated operational transaction. The current capability matrix explicitly leaves total display parity NOT ESTABLISHED.
