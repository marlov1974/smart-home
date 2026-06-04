# P0053C Stale Metrics Classification

| Package / artifact | Classification | Reason |
| --- | --- | --- |
| P0043 package-run metrics | `needs_rebuild_due_to_split_change` | Uses earliest..2024-12-31 / 2025 / 2026 split. |
| P0044 package-run metrics | `needs_rebuild_due_to_split_change` | Uses earliest..2024-12-31 / 2025 / 2026 split. |
| P0045 package-run metrics | `needs_rebuild_due_to_split_change` | Forecast-window validation/holdout are 2025/2026 under old policy. |
| P0053B original package-run metrics | `obsolete_do_not_compare` | Replaced by P0053C rebuild for policy-comparable SE1 consumption metrics. |
| P0053B-A STOP evidence | `still_valid_under_new_policy` | STOP conclusion is about missing price forecast-origin provenance, not split metrics. |
| P0043/P0044/P0045 package design notes | `diagnostic_only_historical` | Still useful to understand model lineage, but not current evaluation truth. |

Current P0053C-compatible SE1 consumption metrics are under:

```text
requirements/package-runs/P0053C/p0053b-rebuild/
```
