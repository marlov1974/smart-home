import unittest

from src.mac.services.spotprice_model_diagnostics.p0038 import (
    P0038_WIND_LOCATIONS,
    series,
    solar_generation_proxy,
    wind_power_proxy,
)


class P0038DiagnosticsTests(unittest.TestCase):
    def test_mandatory_wind_locations_exist(self):
        self.assertEqual({"Malmo", "Kalmar", "Kristinehamn", "Pitea", "Ange", "Harnosand"}, set(P0038_WIND_LOCATIONS))

    def test_wind_group_weights_sum_to_one(self):
        groups = {}
        for _name, (_lat, _lon, group, weight) in P0038_WIND_LOCATIONS.items():
            groups[group] = groups.get(group, 0.0) + weight
        self.assertEqual({"south_wind_proxy", "central_wind_proxy", "north_wind_proxy"}, set(groups))
        for value in groups.values():
            self.assertAlmostEqual(1.0, value)

    def test_wind_power_proxy_is_monotonic_and_capped(self):
        values = [wind_power_proxy(speed) for speed in (0, 3, 6, 9, 12, 15, 20)]
        self.assertEqual(0.0, values[0])
        self.assertEqual(1.0, values[-1])
        self.assertEqual(values, sorted(values))

    def test_night_solar_proxy_is_zero(self):
        self.assertEqual(0.0, solar_generation_proxy(0.0, 100.0))

    def test_area_only_recomposition_uses_no_se1_m4(self):
        row = {
            "actual_se1": 10.0,
            "actual_area_diff": 2.0,
            "m1_abcd_se1": 9.0,
            "m1_abcd_area": 1.0,
            "m3a_se1": 0.1,
            "m3a_area": 0.2,
            "m3b_se1": 0.3,
            "m3b_area": 0.4,
            "m3c_se1": 0.5,
            "m3c_area": 0.6,
            "m3d_se1": 0.7,
            "m3d_area": 0.8,
            "m4_area": 0.9,
            "m4_se1_disabled": 99.0,
        }
        _actual, se1 = series([row], "M1+M3A+M3B+M3C+M3D+M4_area_diff_only", "system_proxy_se1")
        _actual, area = series([row], "M1+M3A+M3B+M3C+M3D+M4_area_diff_only", "area_diff_proxy_se3")
        self.assertAlmostEqual(10.6, se1[0])
        self.assertAlmostEqual(3.9, area[0])


if __name__ == "__main__":
    unittest.main()
