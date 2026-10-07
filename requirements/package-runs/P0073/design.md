# P0073 design

Standalone export outside Smart Home, private GitHub API publication. Preserve firmware bytes/behavior, adapt Makefile/setup/image verification so no vendor evidence is needed. Pin toolchain and Python dependencies, add Linux Actions and deterministic build. Source-only tracked export plus generated release process prevents proprietary artifact and path leakage. GPLv3 selected under operator delegation.

Research: scan original byte image for packet descriptors and every header occurrence, decode three profile tables and dispatch table, symbolically/experimentally trace payload influence into RAM, correlate pointer descriptor registers and manual definitions. Publish numeric offsets and own semantic summaries, never raw vendor instructions. External extraction records function/code/field/offset/encoding provenance and conflicts; master catalog retains all unknown/external-only findings.

Sanitization tool checks tracked candidates, allowed extensions, paths, network/secrets, proprietary names/raw dumps and unexpected binaries; explicit inventory/hash report in private package evidence. Public docs include limitations and release checklist. Build/test locally and hosted CI; verify destination remains private. Export does not alter heat-pump settings or source firmware behavior.
