from __future__ import annotations

import unittest

from src.mac.services.spotprice_model_diagnostics import p0054z


class P0054ZTest(unittest.TestCase):
    def test_cluster_weather_mapping(self) -> None:
        mapping = {row["component_id"]: row["climate_zone_id"] for row in p0054z.cluster_weather_mapping()}
        self.assertEqual(mapping["C11"], "SE3_EAST_COAST_MALARDALEN_STOCKHOLM")
        self.assertEqual(mapping["C24"], "SE3_WEST_COAST_GOTHENBURG")
        self.assertEqual(mapping["C44"], "SE3_SOUTHERN_INLAND_SMALAND_NORTH_GOTALAND")
        self.assertEqual(mapping["SE3_RESIDUAL_METERED_NON_PROFILED_UNOBSERVED"], "SE3_BROAD_PROXY")

    def test_zone_station_weights_sum_to_one(self) -> None:
        for stations in p0054z.zone_station_weights().values():
            self.assertAlmostEqual(sum(weight for _, weight in stations), 1.0)

    def test_correlation(self) -> None:
        self.assertAlmostEqual(p0054z.correlation([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]), 1.0)


if __name__ == "__main__":
    unittest.main()
