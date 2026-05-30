from datetime import date
from pathlib import Path
import tempfile
import unittest

from src.mac.services.spotprice_history.models import HourlySpotPrice
from src.mac.services.spotprice_history.storage import connect_db, expected_utc_hours_for_local_date, init_db, upsert_prices, validate_system_proxy


def row(area, local_date, local_hour, utc_hour, price):
    return HourlySpotPrice(
        area=area,
        utc_hour_start=utc_hour,
        local_hour_start=f"{local_date}T{local_hour:02d}:00:00+01:00",
        local_date=local_date,
        local_hour=local_hour,
        utc_offset="+01:00",
        fold=0,
        price_sek_per_kwh=price,
        price_eur_per_kwh=None,
        exchange_rate=None,
        source="fixture",
        source_resolution="hour",
        samples=1,
    )


class SystemProxyTests(unittest.TestCase):
    def test_system_proxy_view_aligns_se3_and_se1(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "spot.sqlite3"
            init_db(db)
            hours = expected_utc_hours_for_local_date(date(2025, 1, 2))
            rows = []
            for index, hour in enumerate(hours):
                utc = hour.strftime("%Y-%m-%dT%H:00Z")
                rows.append(row("SE3", "2025-01-02", index, utc, 3.0))
                rows.append(row("SE1", "2025-01-02", index, utc, 2.0))
            with connect_db(db) as conn:
                upsert_prices(conn, rows)
                report = validate_system_proxy(conn, date(2025, 1, 2), date(2025, 1, 2), db_path=str(db))

        self.assertTrue(report["complete"])
        self.assertEqual(24, report["aligned_count"])
        self.assertEqual(1.0, report["area_diff_stats"]["mean"])
        self.assertEqual(1.5, report["area_ratio_stats"]["mean"])


if __name__ == "__main__":
    unittest.main()
