from datetime import date
from pathlib import Path
import tempfile
import unittest

from src.mac.services.spotprice_history.models import HourlySpotPrice
from src.mac.services.spotprice_history.storage import (
    connect_db,
    expected_utc_hours_for_local_date,
    init_db,
    upsert_prices,
    validate_range,
)


def row(local_date, local_hour, utc_hour, price=1.0):
    return HourlySpotPrice(
        area="SE3",
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


class StorageTests(unittest.TestCase):
    def test_expected_hours_follow_dst_shape(self):
        self.assertEqual(23, len(expected_utc_hours_for_local_date(date(2025, 3, 30))))
        self.assertEqual(25, len(expected_utc_hours_for_local_date(date(2025, 10, 26))))
        self.assertEqual(24, len(expected_utc_hours_for_local_date(date(2025, 1, 2))))

    def test_upsert_is_idempotent_and_validation_detects_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            init_db(db)
            expected = expected_utc_hours_for_local_date(date(2025, 1, 2))
            rows = [row("2025-01-02", index, hour.strftime("%Y-%m-%dT%H:00Z")) for index, hour in enumerate(expected)]
            with connect_db(db) as conn:
                self.assertEqual(24, upsert_prices(conn, rows))
                self.assertEqual(24, upsert_prices(conn, rows))
                report = validate_range(conn, "SE3", date(2025, 1, 2), date(2025, 1, 2), db_path=str(db))

            self.assertTrue(report.ok)
            self.assertEqual(24, report.row_count)

            with connect_db(db) as conn:
                conn.execute("DELETE FROM spot_prices WHERE utc_hour_start=?", (rows[0].utc_hour_start,))
                report = validate_range(conn, "SE3", date(2025, 1, 2), date(2025, 1, 2), db_path=str(db))

            self.assertFalse(report.ok)
            self.assertEqual(1, report.gap_count)


if __name__ == "__main__":
    unittest.main()
