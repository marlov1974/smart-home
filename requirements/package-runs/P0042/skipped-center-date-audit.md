# P0042 skipped center-date audit

P0041 reason counts: {'dataset_start_boundary': 2, 'dataset_end_boundary': 4, 'dst_or_timezone_issue': 56}
P0042 skipped_center_dates = 6
P0042 reason counts: {'dataset_end_boundary': 4, 'dataset_start_boundary': 2}
calendar_year_boundary_bug = 0

| center_date | reason | start | end | missing_model_dates |
|---|---|---|---|---|
| 2022-05-30 | dataset_start_boundary | 2022-05-28 | 2022-06-03 | 2022-05-28, 2022-05-29 |
| 2022-05-31 | dataset_start_boundary | 2022-05-29 | 2022-06-04 | 2022-05-29 |
| 2026-05-22 | dataset_end_boundary | 2026-05-20 | 2026-05-26 | 2026-05-26 |
| 2026-05-23 | dataset_end_boundary | 2026-05-21 | 2026-05-27 | 2026-05-26, 2026-05-27 |
| 2026-05-24 | dataset_end_boundary | 2026-05-22 | 2026-05-28 | 2026-05-26, 2026-05-27, 2026-05-28 |
| 2026-05-25 | dataset_end_boundary | 2026-05-23 | 2026-05-29 | 2026-05-26, 2026-05-27, 2026-05-28, 2026-05-29 |
