# Procon clean-room firmware

This is a subproject of the existing Smart Home repository. Do not create a nested Git repository.

Read `CODEX_TASK.md`, then `docs/KNOWN_FACTS.md`, `docs/EXPERIMENT_HISTORY.md`, and `docs/PROJECT_PLAN.md`.

First hardware milestone: build a clean replacement Procon application that preserves the existing bootloader if verified possible and answers the existing RS485/Modbus reader with **Input Register 0 = 888 decimal (0x0378)**.

Do not implement CN105 until this milestone works.
