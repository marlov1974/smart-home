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


## Complete original-firmware CN105 cross-reference

In addition to the clean-room firmware documentation, perform a systematic static-analysis inventory of **all CN105 query/command codes present in the original Procon application**, including codes that the replacement firmware does not currently use.

This is a documentation/research deliverable, not permission to publish vendor binaries or raw vendor disassembly.

For every CN105 code or descriptor found in the original application:

1. locate every occurrence in the original binary and determine whether it is code, descriptor/table data, or a false positive;
2. identify the original Procon query/handler path and relevant flash/file offsets for traceability;
3. determine which Procon RS485/Modbus register(s), object(s), or exposed value(s) receive the decoded result, where the mapping can be established;
4. use the project's Procon/Mitsubishi manuals to determine the documented name, unit, range and description of that corresponding RS485 value;
5. link that RS485 semantic name/description back to the CN105 code;
6. record request type, response type, payload offsets/scaling/encoding, and read/write direction where supported by evidence;
7. record whether the mapping is verified from original-firmware data flow, strongly inferred, or still unknown.

The goal is a complete cross-reference of the form:

```text
CN105 code -> original Procon handler/descriptor -> RS485 register/value -> documented RS485 name/meaning
```

Do not limit the inventory to values used by P0069-P0072. Unknown and unused CN105 codes are important and must remain in the table with their uncertainty explicitly recorded.

Create a standalone public document such as `docs/cn105-procon-cross-reference.md` plus a machine-readable equivalent such as `docs/cn105-procon-cross-reference.csv` or JSON. The table should include at least:

- CN105 request/response code;
- packet/function family;
- original binary evidence location(s);
- Procon RS485/Modbus register/address;
- register type if known;
- documented Procon register name;
- description;
- unit;
- scale/encoding;
- read/write direction;
- payload byte/bit mapping where known;
- evidence source;
- confidence;
- notes/unknowns.

Use scripts under `tools/` or `analysis/` so extraction is reproducible. Prefer systematic scanning plus control/data-flow confirmation over manual cherry-picking.

The private Smart Home analysis may use the original BIN and manuals as evidence. The public destination repository must contain only our independently written cross-reference and reproducible clean-room analysis conclusions; do not export the original BIN, manuals, raw decompilation or substantial copied vendor text.

Before declaring this inventory complete, reconcile it against:
- all CN105 descriptors/tables found by static analysis;
- all Procon RS485 values/register definitions available in the supplied documentation;
- all CN105 codes already known from P0069-P0072;
- any code that remains unmapped.

Publish explicit coverage statistics, for example: total unique CN105 codes/descriptors found, mapped to RS485 semantics, partially mapped, and unknown. Do not hide unresolved entries.


## External CN105 project reconciliation

Also scan the external open-source CN105 projects already used as protocol references in this work, especially:

- `F1p/Home-Assistant-Mitsubishi-CN105-to-MQTT`;
- `m000c400/Mitsubishi-CN105-Protocol-Decode`.

Inspect their source, protocol documentation, packet definitions, parsers, setters, service/A3 handling and model-specific branches. Extract CN105 request/response codes, payload fields, scaling, enums, service codes and SET operations that are not yet present in our original-Procon cross-reference.

Reconcile external findings against the original Procon binary-derived table rather than mixing all evidence into one undifferentiated list. Every row/field must carry provenance such as:
- `procon-original-binary`;
- `procon-rs485-manual`;
- `mitsubishi-service-manual`;
- `P007x-hardware-verified`;
- `F1p-cn105-project`;
- `m000c400-cn105-project`.

For externally discovered items not present in the Procon original binary, keep them in the master CN105 catalog and mark them explicitly as `external-only / not found in Procon A1M v3.1.05`. Conversely, retain Procon-only codes even if neither external project knows them.

For conflicts in code meaning, byte offsets, scaling or enum interpretation, do not silently choose one. Record both interpretations, evidence/provenance and a conflict status requiring resolution.

The public repository should therefore contain:
1. a Procon-A1M-specific cross-reference;
2. a broader CN105 master catalog merging our independently established mappings with additional open-source findings;
3. explicit provenance/confidence per mapping;
4. a short differences section showing Procon-only, F1p-only, m000c400-only and shared findings.

Respect the external projects' licenses. Do not copy substantial source or documentation text merely to create the catalog; independently summarize protocol facts and preserve required attribution/links.

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
