from __future__ import annotations

from datetime import date, timedelta
import unittest

from src.mac.services.spotprice_model_diagnostics.p0037 import (
    build_component_matrix,
    build_subset_metrics,
    count_splits,
    fit_strict_components,
    series_for_variant,
    split_for_p0037,
)


def fixture_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = date(2022, 5, 30)
    end = date(2025, 12, 31)
    current = start
    while current <= end:
        for hour in range(24):
            doy = current.timetuple().tm_yday
            seasonal = 0.1 * ((doy % 30) / 30)
            se1 = 0.5 + seasonal + hour / 200
            area = 0.08 + (hour % 6) / 200
            if current.year == 2025 and current.month == 1 and hour in (7, 8):
                se1 += 0.4
            is_special = current.month == 12 and current.day == 25
            row = {
                "utc_hour_start": f"{current.isoformat()}T{hour:02d}:00:00Z",
                "local_date": current.isoformat(),
                "local_hour": hour,
                "day_of_year": doy,
                "weekday": current.weekday(),
                "iso_week": current.isocalendar().week,
                "actual_se1": se1,
                "actual_area_diff": area,
                "actual_se3": se1 + area,
                "se1_system_temperature": -5.0 + (doy % 20),
                "temp_gradient_se3_load_minus_se1_core": -1.0 + (hour % 4),
                "split": split_for_p0037(current),
                "year": current.year,
                "month": current.month,
                "special_day_type": "fixed_public_holiday" if is_special else "normal_weekday",
                "special_day_name": "christmas_day" if is_special else "normal",
                "special_day_group": "public_holiday" if is_special else "normal",
                "bridge_anchor": "none",
                "bridge_strength": "none",
                "is_special_day": 1 if is_special else 0,
                "is_holiday_period_day": 1 if is_special else 0,
                "full_period_m1_se1": se1,
                "full_period_m1_area": area,
            }
            rows.append(row)
        current += timedelta(days=1)
    return rows


class P0037DiagnosticsTests(unittest.TestCase):
    def test_full_year_2025_holdout_has_8760_rows(self):
        rows = fixture_rows()
        counts = count_splits(rows)
        self.assertEqual(8760, counts["holdout"])

    def test_fit_strict_components_does_not_use_2025_for_m1(self):
        rows = fixture_rows()
        fit_strict_components(rows)
        original = {row["utc_hour_start"]: row["m1_raw_se1"] for row in rows if row["split"] == "holdout"}
        for row in rows:
            if row["split"] == "holdout":
                row["actual_se1"] = 999.0
        fit_strict_components(rows)
        changed = {row["utc_hour_start"]: row["m1_raw_se1"] for row in rows if row["split"] == "holdout"}
        self.assertEqual(original, changed)

    def test_component_matrix_contains_required_variants_and_targets(self):
        rows = fixture_rows()
        fit_strict_components(rows)
        for row in rows:
            row["m4_se1"] = 0.0
            row["m4_area"] = 0.0
        matrix = build_component_matrix(rows)
        variants = {row["variant"] for row in matrix if row["target_mode"] == "observed"}
        targets = {row["target"] for row in matrix}
        self.assertIn("M1+M3A+M3B+M4", variants)
        self.assertEqual({"system_proxy_se1", "area_diff_proxy_se3", "recomposed_se3"}, targets)

    def test_recomposed_se3_equals_parts_for_variant(self):
        rows = fixture_rows()
        fit_strict_components(rows)
        for row in rows:
            row["m4_se1"] = 0.01
            row["m4_area"] = -0.01
        holdout = [row for row in rows if row["split"] == "holdout"][:24]
        actual_se1, pred_se1 = series_for_variant(holdout, "observed", "M1+M3A+M3B+M4", "system_proxy_se1")
        actual_area, pred_area = series_for_variant(holdout, "observed", "M1+M3A+M3B+M4", "area_diff_proxy_se3")
        actual_se3, pred_se3 = series_for_variant(holdout, "observed", "M1+M3A+M3B+M4", "recomposed_se3")
        self.assertEqual(actual_se3, [a + b for a, b in zip(actual_se1, actual_area)])
        self.assertEqual(pred_se3, [a + b for a, b in zip(pred_se1, pred_area)])

    def test_subset_metrics_are_computed(self):
        rows = fixture_rows()
        fit_strict_components(rows)
        for row in rows:
            row["m4_se1"] = 0.0
            row["m4_area"] = 0.0
        subsets = build_subset_metrics(rows)
        self.assertIn("special_day_hours", subsets)
        self.assertIn("normal_temperature", subsets)


if __name__ == "__main__":
    unittest.main()
