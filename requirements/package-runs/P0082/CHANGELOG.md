# P0082 changelog

Installed pinned Ghidra/JDK and built Mac ARM natives. Added independent S-record validation, synthetic parser tests, headless audit script and image-specific reproducible runner. Validated 349,889 address-byte pairs against the Ghidra loader. Two independent initial analyses match byte-for-byte. Identified service-dispatch and indexed setting-path evidence; retained uncertainty for MCU identity, pump writes and live energy.

Six parser tests pass. Four documented instruction decodings pass with a separately reported static-flow defect; failed local module patches were reverted. Full projects and vendor inputs remain local. No live actions. New paths require synchronized REPOSITORY_FILES.md. Knowhow promoted in `memory/knowhow/ftc6-static-analysis.md`. Status PARTIAL, not full acceptance.
