# P0070 changelog

Attempt1: new CN105 read-only transport/parser/GET04 scheduler, compressor Hz with validity/staleness, input0–15 diagnostics. Existing RS485 and heartbeat retained. Original hardware init/reference sources reviewed; ACK confirmed1-byte zero before firstbuild. No previous reference code copied. Modbus TX waits service CN105 to prevent receive overrun.

Validation: host ASan/UBSan suites and10 actual-ELF ARM cases pass, including48Hz/0Hz/corrupt simultaneous traffic. Warnings-as-errors, deterministic forced rebuild, originalhash,FFtail and imagebounds pass. BIN3496raw bytes,98304packaged, BSS384. Physical CN105 test pending operator flash. Prior M1r2 evidence added; no live device actions in P0070.

Files: source/include/build/imagecheck/tests, P0070 package/review/design/functions/evidence, new release, relevant living docs and catalog. Fileindex regenerated. Knowhow promotion kept in domain-specific procon/docs/CN105.md: validate ACK shape and service both UARTs during blocking waits; no global Shelly rule changed.

Completion: publish reviewable build/artifacts, not hardware M3/M4 completion. Three physical attempts maximum; none performed yet. Exact MCU package/pins remain inferred. Source handoff in clean isolated /tmp/procon-compressor checkout; original dirty worktree untouched.
