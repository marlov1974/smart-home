# P0072 r3 — software verified, hardware pending

Corrected operation/zone relevance of binary GET28 flags and retained conservative unknown-value rejection. Added passive FAST GET28 and read-only diagnostics283–298, firmware revision3, compatible command envelope2. Existing SET encoders, AUTO/lease restoration and A3 whole-operation ownership unchanged.

Changed control.c/h,cn105.c for gate/diagnostics; read_mvp.py for decoded flags; native/ARM/helper tests for acceptance and rejection; API/function docs and new immutable r3 artifacts. REPOSITORY_FILES.md updated for added evidence/release paths. Promoted precondition-observability lesson to memory/knowhow/codex.md.

Verification: all four native ASan/UBSan suites pass, including84 mode/flag/value combinations, multiple blockers, raw little-endian retention, passive sample without command, bounded age and retained rejection. Python6 read-helper +3 encoder tests pass.15 ARM scenarios pass with independent SET/controller model, irrelevant binary flags accepted and restored, relevant heating inhibit rejected with no SET. Deterministic11320-bytecode/98304-byteBIN SHA f0d33dab1a181d133bc1d5b9c5501ceb1952e71b798d93514a6bf9a1932a2fde. No flash writes in ARM; native code touches no new write masks.

No live commands or flashing this build. One prior r2 hardware attempt remains in history; exact site flag unknown until r3 is flashed and read. Physical control validation and power-loss recovery remain pending. Next read CONTROL_API.md and live-20261007/report.md before a new supervised test. Do not rerun a control command merely to obtain flags: new FAST diagnostics expose them passively.

## Physical validation 2026-10-07

[Live report](live-20261007/report.md): r3 confirms only cooling flags blocked r2. FIXED_FLOW38C, explicit AUTO and runtime lease expiry all passed. A15-minute trial reached39.5C/max42Hz; mode2/28C restored and later compressor0Hz observed. Other controls/reset recovery remain untested. Added compressed logs,harness,summary/report and synchronized file index. Existing precondition-diagnostics knowhow confirmed; no additional promotion. No firmware changes in this validation pass.
