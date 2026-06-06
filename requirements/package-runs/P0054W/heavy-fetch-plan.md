# P0054W heavy-fetch plan

Chosen strategy: outer loop MGA, inner loop month.

Requested range: `2022-06-01T00:00:00Z` through `2026-06-06T15:00:00Z`.

Masterdata count: `211` SE3 MGAs.

Checkpoint table: `esett_mga_consumption_ingestion_checkpoint_v1`.

The fetch is serial with conservative pacing and can resume from checkpoint without discarding completed chunks.
