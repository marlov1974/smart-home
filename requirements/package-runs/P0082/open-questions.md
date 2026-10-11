# P0082 next evidence

- Confirm which board each chip photograph depicts and the provenance/model/version of this firmware. No need to flash anything.
- Validate more operand/p-code semantics; resolve the instruction at 9B038 before relying on full decompilation. Upstream direct call/jump metadata is incomplete.
- Trace callers 8BAB9/8BBD6/8BF6B/CEC8A to a verified transport parser; identify CN105 versus display routing.
- Follow descriptor callback 493D from C96E6 and map setting-file offsets before labeling pump-level fields.
- Locate transport response packers before naming energy accumulators; current search absence is not proof they do not exist.
- Extend local synthetic opcode vectors to signed branches, all call forms, bit operations and far loads. This package provides a useful starting project, not a complete processor-validation suite.
