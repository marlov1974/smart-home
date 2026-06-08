from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo

from src.mac.services.spotprice_model_diagnostics import p0054k, p0056h, p0056h2


class P0056H2StaticStyleLagTests(unittest.TestCase):
    def test_static_style_lags_match_origin_anchored_values(self) -> None:
        values = [float(index) for index in range(200)]
        features = p0056h2.static_style_lag_features_at_origin(values, 168)

        self.assertEqual(features["area_consumption_lag_1h"], 167.0)
        self.assertEqual(features["area_consumption_lag_24h"], 144.0)
        self.assertEqual(features["area_consumption_lag_168h"], 0.0)
        self.assertEqual(features["area_consumption_roll_mean_6h"], 164.5)
        self.assertEqual(features["area_consumption_same_hour_24h_vs_168h"], 144.0)

    def test_modeling_rows_keep_lags_constant_across_36h_horizon(self) -> None:
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        target_rows = []
        weather_rows = {}
        for index in range(220):
            timestamp = p0056h.format_dt_utc(start + timedelta(hours=index))
            target_rows.append({"timestamp_utc": timestamp, "consumption_mw": float(index)})
            weather_rows[timestamp] = {"weather_dummy": float(index)}

        origin_local = (start + timedelta(hours=168)).astimezone(ZoneInfo("Europe/Stockholm"))
        origin = p0056h.OriginWindow(
            origin_local=origin_local,
            origin_utc=p0056h.format_dt_utc(origin_local),
            origin_id="test-origin",
        )
        rows = p0056h2.build_static_style_modeling_rows("SE1", target_rows, weather_rows, [origin], "TEST")

        self.assertEqual(len(rows), 36)
        self.assertEqual({row["area_consumption_lag_1h"] for row in rows}, {167.0})
        self.assertEqual({row["area_consumption_roll_mean_6h"] for row in rows}, {164.5})
        self.assertEqual({row["forecast_origin_timestamp_utc"] for row in rows}, {origin.origin_utc})
        self.assertEqual(rows[0][p0054k.TARGET_FIELD], 168.0)
        self.assertEqual(rows[-1][p0054k.TARGET_FIELD], 203.0)


if __name__ == "__main__":
    unittest.main()
