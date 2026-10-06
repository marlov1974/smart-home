# P0069 — Procon M1 Modbus 888

User-authorized 2026-10-06: establish development environment and build first minimal firmware. Operator flashes physically from another computer. User explicitly allows an inferred MCU target when the marking is unavailable ("Vet inte, du får gissa"). This relaxes the exact-marking prerequisite for an experimental candidate, not a claim of verified hardware.

Scope: procon tools, original analysis, fresh bare-metal source, host/ARM tests, experimental release artifacts and documentation. Input register 0 returns 888 via FC04, slave 1, 9600 8N1. All other addresses are unavailable. No CN105, RTOS, EEPROM or flash writes. No device actions by Codex. Hardware pass requires operator flash followed by read-only confirmation; software completion alone is not M1 hardware completion.

Completion: build/test and publish reviewable development result in the existing Smart Home repository. Operator alone performs physical installation. Keep original firmware immutable. No modifications to unrelated G2 runtime or existing P0068 work.

Validation: source warnings-as-errors; native parser/framing tests with sanitizers; ARM ELF emulation with mocked peripherals; image vector/base/bounds checks; deterministic rebuild; original hashes; diff and file index. Deliver BIN/ELF/MAP/disassembly/SHA256 plus explicit hardware assumptions and recovery instructions.
