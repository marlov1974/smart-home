# Procon firmware development

Latest build: [P0071 Geodan brine r2](releases/P0071-brine-r2/README.md). Adds read-only service27/28 with raw payload retention, validity/age and diagnostic counters. **P0071 hardware brine decoding is not yet verified.** Operator alone flashes and validates. Register map/procedure: [docs/BRINE.md](docs/BRINE.md).

P0070 remains hardware-confirmed: six20Hz reads, fresh CN105 counter updates and zero errors. P0071 preserves input0=888, compressor telemetry and heartbeat, with input1=71; addresses0–67, max16registers per request. Original and prior release files remain immutable.

Build: `sh procon/tools/setup.sh`, then `make -C procon verify`. All artifacts are in the release directory. Inferred STM32L433 target; exact marking/density unavailable. No unrelated Shelly runtime changes. See docs/HARDWARE.md, docs/TOOLCHAIN.md and docs/RECOVERY.md.

R2 order: **Hz → all service27 attempts → all service28 attempts → repeat**, with no interleaved Hz. Input68=2. Hz may become stale during long service attempts. r1 hardware test returned pending-only; r2 physical result is pending.
