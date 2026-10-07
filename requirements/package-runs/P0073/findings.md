# P0073 findings

Original packet tables:55descriptors,3profiles,all55complete-header matches reconciled. ATW SET table34entries at0x0801ED4C,queue event→builder linkage established. Register descriptor domains:H436,C3,DI108,I271;796entries point into valid RAM. Bounded payload influence touches751register aliases;457/470supplied manual rows have matches. Read/write aliases and conditional transforms remain explicit confidence levels,not verified live commands.

New concrete conclusion: original GET1E mapsH238–244/I117–123,GET1F mapsH245–249/I124–128. Both remain semantically unnamed in supplied FTC6 documentation; neither proves brine availability. GET04→RAM0x2000251C→H73/I32. A3 absent from original static table,provided by external reference plus replacement hardware work.

External reconciliation:123F1p parser/encoder/service functions,18m000c400 functions; normal ATW GET-only additionalF1p codes08/12/A3.5field interpretation conflicts,including GET0BZone2bytes3–4versus7–8. Complex setters/relay direction/branch-dependent details retained as unresolved; catalogs intentionally do not claim full semantic completion. Source headers establish m000c400GPLv3-or-later despite no top-level LICENSE. Project GPL-3.0-only selected under explicit operator delegation.

Standalone source-only destination has55tracked text files. Exact firmware source retained,portable build/tests added; regeneratedBIN matchesP0072SHA256 f8823fab325018c31f093215cd72d19c6d28dd28082bcd64d83df82e88b3b4a9. No vendor image/manual/updater/originaldisassembly/hardwareprivate logs exported. Local independent dependency environment,13ARMtests,nativeASan/UBSan,4helpertests,2catalogtests,deterministicbuild and sanitizationpass. CIresult recorded separately.

Final review: CPU context and RAM reset per original-handler probe; instruction-limit executions excluded from mapping dependencies. GET1C remains partial with explicit bound diagnostics. Unified master catalog122entries:13Procon-only,43shared,66external-only/unresolved, retaining packet/profile distinctions. First hosted CIrun37579002118passed completely, including generated release upload. Final destination commit be4f02e4b31c09eed5073a151925361b4fd2bad8 passed hosted CI run 37581048808, including the complete release and artifact upload.

Release packaging strips host-specific DWARF paths from the distributed ELF and normalizes MAP paths. Firmware BIN is unchanged. Local ELF/MAP sanitization check passed; the complete release process is checked by hosted CI.
