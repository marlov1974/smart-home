# P0073 standalone export and research

Destination private repository: marlov1974/procon-melcobems-mini-a1m. Working firmware stays unchanged; source-only export has portable build,CI,release generation and GPL-3.0-only under operator delegation.

Destination tools/inventory_original.py accepts optional original BIN plus private manual inventory, verifies hash, enumerates packet/SET/register descriptors and bounded payload→RAM influence. CPU context/RAM reset per run; aborted runs excluded; conditional cases remain partial. Only numeric conclusions and independent semantic labels are published. No original code or vendor artifact is exported.

catalog_external.py extracts named parser/setter/service/header facts from pinned F1p/m000c400 sources, separates profile/family/direction, records conflicts and merges references to original mappings. render_catalogs.py produces human-readable coverage/differences. tests/test_catalogs.py preserves verified anchor mappings and provenance/conflict invariants.

setup.sh installs pinned hash-checked compiler and isolated dependencies. release.py enforces clean committed source, deterministic BIN and source metadata; it strips release ELF debug paths, normalizes MAP paths and rejects remaining host paths. sanitize.py checks tracked export inventory for binaries/private paths/secrets/vendor instruction patterns. Detailed limits,results and destination commits: requirements/package-runs/P0073/.
