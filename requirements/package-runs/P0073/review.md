# P0073 review — WARN

Source c73e462 (firmware baseline7ae48e6), clean/synchronized. Destination existing private repository verified via GitHub API, initial head1977028. Private CLI clone has no credentials; use connected GitHub API with expected-head leases, never change visibility. No live hardware actions.

Inventory before export: allow freshly written firmware/include/startup/linker, native/ARM tests, image checker and sanitized read-only helpers. Rebuild all artifacts to avoid local debug-path leakage. Exclude entire reference/original, original-analysis dumps, updater, PDFs, raw hardware logs, local tooling, global Smart Home files. Write standalone docs from factual findings; no copied manual prose/tables.

License: MIT allows proprietary redistribution while retaining notice; GPLv3 keeps distributed derivative source available under GPL. Operator delegated suitable selection; choose GPL-3.0-only, compatible with GPLv3 F1p reference. Source implementation is independently written, protocol facts independently summarized; preserve reference attribution. m000c400 has GPLv3-or-later notices in source headers despite no top-level LICENSE; no source/prose copied from it. Toolchain libgcc has GCC Runtime Library Exception; document separately.

Research scope: inventory descriptors plus switch/data flow and reconcile against all supplied register definitions and both external sources. Unknown edges remain explicit; complete coverage of an extraction domain must not be represented as proof of all possible runtime-generated commands. Public readiness requires passing hosted CI and review of unresolved research, not just file copying.
