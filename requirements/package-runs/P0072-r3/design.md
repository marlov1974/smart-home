# P0072 r3 design

Keep command envelope2 and telemetry1. Firmware identity revision3. Append GET28 to ordinary FAST cycle, never inside A3. Preserve old raw200–255 map. Expose raw GET28, age/generation, relevant and blocking masks, rejection byte/value in input283–298, readable before any command. Retain rejection details until next accepted new command; passive observations cannot clear them.

Snapshot gate: holiday4 and server10 always block; DHW5 only for boost or DHW target; heatingZ1 byte6 only for FIXED_FLOW or flow target. CoolingZ1 byte7 and Zone2 bytes8/9 do not block those Zone1/DHW operations. Unknown nonbinary flag values in4–10 still block conservatively, even outside relevance mask. Never write those flags or override native inhibits. Existing boost validity and all original baseline range checks remain. OFF still observes global holiday/server gate. AUTO restoration unchanged.

Native tests exhaust mode/target/flag relevance and malformed values, no SET before rejection, passive diagnostic retention and wire encodings that cannot alter prohibit bits. ARM regression model includes nonzero unrelated flags in accepted fixed flow, plus blocking heating flag with no SET. Read helper supports r1/r2/r3 and decodes new diagnostics. Immutable r3 release, deterministic image checks. Power-loss recovery remains unsupported.
