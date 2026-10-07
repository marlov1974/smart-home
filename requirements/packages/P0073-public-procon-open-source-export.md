# P0073 — Public open-source Procon A1M export

Operator request 2026-10-07: prepare a sanitized, standalone open-source export of the clean-room Procon firmware and interoperability knowledge from Smart Home into the newly created repository `marlov1974/procon-melcobems-mini-a1m`.

The destination repository is currently private. Keep it private throughout this package. Do not change repository visibility. Operator decides when to make it public after review.

## Purpose

Create a high-quality standalone repository that:
- builds the clean-room replacement firmware without depending on the private Smart Home repository;
- preserves the working P0069-P0072 source, tests and useful protocol knowledge;
- is easy for humans, search engines and AI systems to discover and understand;
- contains no vendor firmware, updater binaries, vendor PDFs or other copied proprietary artifacts;
- clearly distinguishes observed facts, hardware verification, external references and hypotheses.

## Destination

Target repository:
`marlov1974/procon-melcobems-mini-a1m`

Do not create another repository and do not add a nested Git repository inside Smart Home.

Suggested public-facing description:
`Open-source replacement firmware for Procon MELCOBEMS MINI (A1M), with Mitsubishi Electric Ecodan/Geodan CN105 and Modbus support.`

## Mandatory sanitization

Before copying anything, inventory the candidate files.

MUST NOT export:
- original Procon/Mitsubishi firmware BIN files;
- original firmware ZIP/update packages;
- vendor updater executables/libraries;
- Mitsubishi/Procon manuals or PDFs;
- raw decompilation/disassembly dumps of vendor firmware;
- copied vendor source/code;
- credentials, tokens, local machine paths, private network details or unrelated Smart Home data;
- hardware logs containing unrelated private infrastructure data.

Clean-room build artifacts generated from our own source may be exported.

Our own concise interoperability documentation may describe packet formats, observed behavior, register semantics and reverse-engineering conclusions necessary to understand/use the project.

Run automated secret/binary/license-sensitive-content checks and document the result before recommending public visibility.

## Source baseline

Export the current clean-room implementation, not the historical patched-vendor firmware experiments.

Preserve working behavior from P0069-P0072, including:
- bare-metal ARM application;
- Modbus RTU;
- input register 0 = 888 compatibility marker;
- heartbeat;
- CN105 connection and normal telemetry;
- compressor frequency;
- P0071 A3 service implementation and exclusive retry behavior;
- P0072 MVP telemetry/control work that is complete and verified at export time.

Historical test1-test14 binary patches are not release source. Summarize lessons where useful but do not export patched vendor BINs.

## Standalone repository structure

Create a clear structure such as:

```text
README.md
LICENSE
SECURITY.md
CONTRIBUTING.md
.github/
  workflows/
docs/
  architecture.md
  hardware.md
  modbus.md
  cn105-protocol.md
  cn105-packets.md
  a3-service-protocol.md
  geodan-service-codes.md
  building.md
  flashing-and-recovery.md
  verification.md
firmware/
  startup/
  include/
  src/
  linker.ld
tests/
tools/
releases/ or documented GitHub Release process
```

Adapt to the actual clean-room tree rather than duplicating files unnecessarily.

## Discoverability

README title and introductory text must naturally contain:
- Procon MELCOBEMS MINI;
- A1M;
- Mitsubishi Electric;
- Ecodan;
- Geodan;
- CN105;
- Modbus;
- replacement firmware;
- heat pump.

Make the first section explain what the project is, supported hardware, current verification state and that it is an independent community project not affiliated with or endorsed by Mitsubishi Electric or Procon.

Recommend repository topics for operator configuration:
- procon
- melcobems
- a1m
- mitsubishi-electric
- ecodan
- geodan
- cn105
- modbus
- heat-pump
- stm32
- home-automation

Do not use branding that implies an official Mitsubishi/Procon repository.

## CN105/A3 knowledge documentation

Create a dedicated document designed to be useful as a technical reference, including the important hardware-derived finding:

- Geodan TH32 is brine inlet and TH34 is brine outlet according to project service-document evidence.
- The project uses service queries corresponding to 27/28 for those values.
- A3 service requests are multi-transaction operations.
- A not-ready response must be retried without inserting ordinary CN105 GET queries between attempts.
- Hardware testing showed that interleaving normal queries left the service operation pending.
- The working implementation grants the whole service operation exclusive ownership of CN105 until completion/exhaustion.
- Document timing, status interpretation, frame/checksum construction and raw evidence to the extent supported by clean-room project evidence.
- Clearly label what is hardware-confirmed versus inferred/reference-derived.

Use searchable terminology such as `CN105 A3`, `Geodan brine temperature`, `TH32`, `TH34`, `service 27`, `service 28`, and `status 0`.

Do not copy prose/tables from vendor manuals. State our independently documented facts in our own words and cite/link lawful external references where appropriate.

## Build reproducibility

The destination repo must build independently on a clean supported development environment.

Provide:
- documented toolchain/version;
- one-command build where practical;
- host tests;
- ARM image verification;
- deterministic/reproducible build check where currently supported;
- generated ELF/MAP/BIN/disassembly/SHA256 through the release process.

Do not depend on files that remain only in Smart Home.

## CI

Add GitHub Actions for at least:
- host unit tests;
- clean firmware build;
- image/vector/bounds checks;
- deterministic build or equivalent artifact consistency check where practical.

CI must not require proprietary firmware.

If ARM toolchain installation in Actions is nontrivial, document and implement a reproducible pinned approach rather than silently weakening verification.

## License

Do not choose a license silently. Prepare a short comparison in the package review between at least MIT and GPLv3, with the practical consequence for this firmware project.

The operator previously expressed interest in public reuse/discoverability but has not made a final license selection. Keep the destination private and request the operator's license decision before final public release if a license has not already been explicitly chosen.

Do not copy third-party code into the repository unless its license is compatible with the selected project license and attribution/notice requirements are satisfied.

## Security and safety documentation

Add a concise SECURITY/safety document covering:
- experimental replacement firmware;
- potential loss of vendor warranty/support;
- operator responsibility for flashing/recovery;
- no bypass of heat-pump safety protections;
- read/write control risks;
- how to report protocol or firmware defects.

Do not make unsupported safety certification claims.

## Releases

Prepare a release process for our own generated firmware.

A release should include:
- source commit/tag;
- BIN;
- ELF;
- MAP;
- disassembly;
- SHA256;
- hardware/feature verification status.

Do not bundle original vendor firmware or updater.

## Traceability back to Smart Home

In Smart Home P0073 package-run evidence, record:
- source commit(s);
- destination commit(s);
- exact exported file inventory;
- sanitization report;
- tests/build results;
- files intentionally excluded;
- outstanding public-release blockers.

The public repo itself should not require access to Smart Home to understand/build the project.

## Public-release gate

P0073 may populate and prepare the private destination repository, but it must NOT make it public.

Before recommending public visibility, verify:
1. no vendor binaries/PDFs/updaters are present;
2. no secrets/private Smart Home data are present;
3. build/test CI passes;
4. README/protocol docs are standalone;
5. third-party license obligations are documented;
6. project license has been explicitly selected by operator;
7. recovery/safety limitations are documented.

Provide a final checklist for the operator. The operator performs the visibility change.

## Scope exclusions

Do not modify unrelated Smart Home/Shelly runtime.
Do not publish Smart Home itself.
Do not rewrite the working firmware merely to make the repository prettier.
Do not add speculative protocol claims as facts.
