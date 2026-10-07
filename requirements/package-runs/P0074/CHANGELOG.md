# P0074 — standalone platform specification

Added hardware/protocol references, from-empty-project M0–M10 instructions, recovery boundaries, machine-readable evidence-tagged platform data, golden vectors and executable documentation checks. P0073catalogs integrated without rewriting their research conclusions. Source firmware unchanged.

Local checks: documentation vectors/platform/sequencing/wrap/links pass;82tracked standalone text files pass sanitizer with zero findings;13firmware source files match baseline. Hosted CI run37586676765 passed for destination474bc171, including all tests, source build, sanitization, deterministic release and artifact upload; details in hosted-ci.json. New checker runs in existing test and host-test Makefile targets.

REPOSITORY_FILES.md regenerated for package evidence and function-catalog addition, including the newly received P0074package definition. Knowhow promotion: intentionally kept in the standalone engineering specification and package findings; no new global Smart Home runtime rule. No live actions or visibility changes. Destination commits and exact file inventory recorded in traceability.json/sanitization.json.
