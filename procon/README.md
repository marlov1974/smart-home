# Procon firmware development

Subproject of Smart Home. Latest experimental candidate: [P0070 compressor r1](releases/P0070-compressor-r1/README.md).

M1 r2 is hardware-confirmed (five input0=888 replies and operator-reported heartbeat). P0070 adds read-only CN105 connect/GET0x04 and input2 compressor Hz. Input3 must be1 before using it;65535 means unknown/stale. Physical P0070 verification awaits operator flash. RS485 remains slave1,96008N1,FC04; input0=888, input1=70. Full register map and recovery notes are in the release README.

Build/test: `sh procon/tools/setup.sh`, then `make -C procon verify`. Operator alone performs physical flashing. Original ZIP/BIN and old M1 releases remain immutable. Inferred STM32L433 target; exact part marking unavailable. See docs/HARDWARE.md, docs/TOOLCHAIN.md and docs/RECOVERY.md.
