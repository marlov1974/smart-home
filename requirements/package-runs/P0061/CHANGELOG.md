# P0061 Changelog

Moved the Mac-side energy-market simulator and forecasting lab out of G2 Smart Home into `marlov74/Market-Simulator`.

Moved to Market-Simulator:

- spot forecast, spot history, weather history, Swedish calendar, temperature normalization, ML model and diagnostics services
- weekly home optimizer POC
- market simulator tests and small local data fixtures
- market function docs, memory/planning/knowhow docs and market package evidence for P0017-P0025 and P0030-P0056

Changed in G2:

- removed migrated market simulator source, tests, docs, memory, package specs and package-run evidence
- updated `README.md`, `memory/bootstrap-manifest.json`, `memory/00-index.md`, `memory/knowhow/00-index.md` and `docs/functions/00-index.md`
- added P0061 package spec and package-run evidence

Not changed:

- no live devices
- no Shelly runtime/deploy cleanup
- no production activation

Knowhow promotion:

Skipped. This package was a repository ownership migration, not a live debugging or runtime anomaly package.
