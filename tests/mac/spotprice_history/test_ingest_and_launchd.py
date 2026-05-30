from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

from src.mac.services.spotprice_history.ingest import ingest_daily
from src.mac.services.spotprice_history.launchd import LABEL, render_launch_agent_plist
from src.mac.services.spotprice_history.storage import connect_db, init_db


def payload_for(day):
    return json.dumps(
        [
            {
                "SEK_per_kWh": 1.0,
                "EUR_per_kWh": 0.1,
                "EXR": 10.0,
                "time_start": f"{day}T{hour:02d}:00:00+01:00",
                "time_end": f"{day}T{hour + 1:02d}:00:00+01:00" if hour < 23 else f"{day}T23:59:59+01:00",
            }
            for hour in range(24)
        ]
    ).encode("utf-8")


class IngestAndLaunchdTests(unittest.TestCase):
    def test_ingest_daily_is_noop_when_latest_complete_day_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            init_db(db)
            calls = []

            def fetcher(area, target_date):
                calls.append((area, target_date))
                return payload_for(target_date.isoformat())

            with connect_db(db) as conn:
                first = ingest_daily(conn, area="SE3", db_path=str(db), today=date(2025, 1, 3), fetcher=fetcher)
                second = ingest_daily(conn, area="SE3", db_path=str(db), today=date(2025, 1, 3), fetcher=fetcher)

        self.assertEqual(1, first.fetched_days)
        self.assertEqual(0, second.fetched_days)
        self.assertEqual([("SE3", date(2025, 1, 2))], calls)

    def test_launchd_plist_contains_contract(self):
        plist = render_launch_agent_plist(db_path="/tmp/spot.sqlite3", python_executable="/usr/bin/python3")

        self.assertIn(LABEL, plist)
        self.assertIn("<integer>14</integer>", plist)
        self.assertIn("src.mac.services.spotprice_history", plist)
        self.assertIn("spotprice-history-daily.out.log", plist)
        self.assertIn("/tmp/spot.sqlite3", plist)


if __name__ == "__main__":
    unittest.main()
