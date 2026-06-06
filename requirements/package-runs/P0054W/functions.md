# P0054W function design

`run_p0054w_esett_fetch(...)` orchestrates preflight, schema creation, checkpoint creation, full fetch and evidence writing.

`create_schema(...)` creates `esett_mga_masterdata_v1`, `esett_mga_consumption_native_v1` and `esett_mga_consumption_ingestion_checkpoint_v1`.

`fetch_se3_masterdata(...)` reads public eSett SE3 MGA masterdata.

`run_preflight(...)` loads a small 1-3 MGA / 1-2 month sample and validates source shape.

`ensure_full_checkpoint_manifest(...)` creates resumable per-MGA/per-month work items.

`process_checkpoint(...)` fetches and persists pending chunks incrementally.

`native_rows_from_payload(...)` converts eSett `LoadProfileDTO` rows into the native contract while preserving source sign, unit, resolution and settlement class.

`write_fetch_evidence(...)` writes P0054W package-run evidence.
