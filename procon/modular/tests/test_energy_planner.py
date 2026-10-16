#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import sys
import unittest


PATH = Path(__file__).parents[1] / "tools" / "energy_planner.py"
SPEC = importlib.util.spec_from_file_location("energy_planner", PATH)
planner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = planner
SPEC.loader.exec_module(planner)

BACKTEST_PATH = Path(__file__).parents[1] / "tools" / "backtest_energy_mpc.py"
BACKTEST_SPEC = importlib.util.spec_from_file_location("backtest_energy_mpc", BACKTEST_PATH)
backtest = importlib.util.module_from_spec(BACKTEST_SPEC)
assert BACKTEST_SPEC.loader
BACKTEST_SPEC.loader.exec_module(backtest)


class EnergyPlannerTests(unittest.TestCase):
    def test_linear_ramp_energy_is_math_only(self):
        result = planner.integrate_power(
            [planner.PowerPoint(0, 5000), planner.PowerPoint(150, 7000)],
            max_gap_s=180,
        )
        self.assertAlmostEqual(result.wh, 250.0)
        self.assertEqual(result.covered_s, 150)

    def test_gap_is_unknown_and_not_booked(self):
        result = planner.integrate_power(
            [
                planner.PowerPoint(0, 4000),
                planner.PowerPoint(30, 4000),
                planner.PowerPoint(100, 4000),
            ]
        )
        self.assertAlmostEqual(result.wh, 4000 * 30 / 3600)
        self.assertEqual(result.covered_s, 30)
        self.assertEqual(result.unknown_s, 70)

    def test_remaining_energy_becomes_average_power(self):
        self.assertEqual(planner.required_average_w(1000, 500, 450), 4000)

    def test_four_kw_pair_uses_one_pump(self):
        devices = [planner.DeviceEnvelope(), planner.DeviceEnvelope()]
        result = planner.allocate_pair(4000, devices, lead=0)
        self.assertEqual(result.target_w, (4000, 0))
        self.assertEqual(result.duty_fraction, 1)

    def test_below_floor_uses_duty_cycle(self):
        devices = [planner.DeviceEnvelope(), planner.DeviceEnvelope()]
        result = planner.allocate_pair(2000, devices, lead=1)
        self.assertEqual(result.target_w, (0, 3000))
        self.assertAlmostEqual(result.duty_fraction, 2 / 3)

    def test_twelve_kw_balances_both(self):
        devices = [planner.DeviceEnvelope(), planner.DeviceEnvelope()]
        result = planner.allocate_pair(12000, devices)
        self.assertEqual(result.target_w, (6000, 6000))

    def test_six_kw_splits_at_both_continuous_floors(self):
        devices = [planner.DeviceEnvelope(), planner.DeviceEnvelope()]
        result = planner.allocate_pair(6000, devices)
        self.assertEqual(result.target_w, (3000, 3000))

    def test_ten_kw_stays_inside_preferred_band(self):
        devices = [planner.DeviceEnvelope(), planner.DeviceEnvelope()]
        result = planner.allocate_pair(10000, devices)
        self.assertEqual(result.target_w, (5000, 5000))

    def test_equal_daily_energy_example(self):
        self.assertEqual(2 * 3000 * 16, 2 * 2000 * 24)

    def test_capacity_shortfall_is_reported(self):
        devices = [
            planner.DeviceEnvelope(maximum_feasible_w=5000),
            planner.DeviceEnvelope(maximum_feasible_w=5000),
        ]
        result = planner.allocate_pair(12000, devices)
        self.assertEqual(result.target_w, (5000, 5000))
        self.assertEqual(result.shortfall_w, 2000)

    def test_start_has_five_minute_zero_output_pause(self):
        state = planner.project_toward(planner.ResponseState(), 6000, 300)
        self.assertEqual(state.power_w, 0)
        self.assertTrue(state.enabled)
        state = planner.project_toward(state, 6000, 300)
        self.assertAlmostEqual(state.power_w, 4000)

    def test_per_device_ramps_can_cross(self):
        vp1 = planner.ResponseState(6000, True, 0)
        vp2 = planner.ResponseState(2000, True, 0)
        vp1 = planner.project_toward(vp1, 3000, 300)
        vp2 = planner.project_toward(vp2, 6000, 300)
        self.assertAlmostEqual(vp1.power_w, 4000)
        self.assertAlmostEqual(vp2.power_w, 6000)
        self.assertAlmostEqual(vp1.power_w + vp2.power_w, 10000)

    def test_ramp_to_zero_requires_a_new_start_pause(self):
        state = planner.ResponseState(2000, True, 0)
        state = planner.project_toward(state, 0, 300)
        self.assertEqual(state, planner.ResponseState())
        state = planner.project_toward(state, 4000, 150)
        self.assertEqual(state.power_w, 0)
        self.assertEqual(state.startup_remaining_s, 150)

    def test_pair_model_is_asymmetric(self):
        up, _ = planner.project_pair_step(6000, 12000, 0)
        down, _ = planner.project_pair_step(12000, 6000, 0)
        self.assertEqual(up, 6900)
        self.assertEqual(down, 11910)

    def test_pair_model_honors_observed_start_delay(self):
        power, delay = planner.project_pair_step(0, 12000, 330)
        self.assertEqual(power, 0)
        self.assertEqual(delay, 300)

    def test_scalar_four_quarter_mpc_replay(self):
        targets = (1500, 2000, 2500, 4000, 2500, 2000, 1500)
        model = planner.PairModel()
        elapsed = 0
        delivered = 0.0
        power = 0.0
        command = 6000
        startup = 330.0
        maximum_command = command
        while elapsed < len(targets) * 900:
            decision = planner.scalar_mpc_command(
                elapsed_s=elapsed,
                delivered_wh=delivered,
                power_w=power,
                current_command_w=command,
                startup_remaining_s=startup,
                quarter_targets_wh=targets,
            )
            command = decision.command_w
            maximum_command = max(maximum_command, command)
            new_power, startup = planner.project_pair_step(
                power, command, startup, model
            )
            delivered += (power + new_power) * 0.5 * model.step_s / 3600
            power = new_power
            elapsed += model.step_s
        self.assertLess(abs(delivered - sum(targets)), 25)
        self.assertLessEqual(maximum_command, 16000)
        self.assertGreaterEqual(min(command, power), 6000)

    def test_bounded_shelly_mpc_replay(self):
        targets = (1500, 2000, 2500, 4000, 2500, 2000, 1500)
        model = planner.PairModel()
        elapsed, delivered, power, command, startup = 0, 0.0, 0.0, 6000, 330.0
        maximum_command = command
        while elapsed < len(targets) * 900:
            command = planner.bounded_mpc_command(
                elapsed_s=elapsed,
                delivered_wh=delivered,
                power_w=power,
                current_command_w=command,
                startup_remaining_s=startup,
                quarter_targets_wh=targets,
            ).command_w
            maximum_command = max(maximum_command, command)
            new_power, startup = planner.project_pair_step(power, command, startup, model)
            delivered += (power + new_power) * 0.5 * model.step_s / 3600
            power = new_power
            elapsed += model.step_s
        self.assertLess(abs(delivered - sum(targets)), 1)
        self.assertLessEqual(maximum_command, 16500)

    def test_remaining_energy_controller_reports_active_capability_shortfall(self):
        decision = planner.remaining_energy_command(
            elapsed_s=2700,
            delivered_wh=6600,
            power_w=10500,
            current_command_w=13500,
            quarter_targets_wh=(1500, 2000, 2500, 4000, 2500, 2000, 1500),
            reachable_w=11000,
        )
        self.assertEqual(decision.reachable_w, 11000)
        self.assertGreater(decision.projected_shortfall_w, 0)
        self.assertLessEqual(decision.wanted_w, 11000)

    def test_unreachable_boundary_does_not_create_unbounded_windup(self):
        decision = planner.remaining_energy_command(
            elapsed_s=890,
            delivered_wh=800,
            power_w=8000,
            current_command_w=10000,
            quarter_targets_wh=(1500, 2000),
        )
        self.assertLessEqual(decision.command_w, 12000)
        self.assertLessEqual(decision.wanted_w, decision.reachable_w)

    def test_shortfall_includes_remaining_time_ramp_limit(self):
        decision = planner.remaining_energy_command(
            elapsed_s=850,
            delivered_wh=1000,
            power_w=6000,
            current_command_w=6000,
            quarter_targets_wh=(1500, 2000),
            reachable_w=24000,
        )
        self.assertGreater(decision.projected_shortfall_w, 0)
        self.assertLess(decision.forecast_error_wh, 0)

    def test_q7_reduction_does_not_credit_five_minutes_at_peak_power(self):
        # Field-run fixture near 05:11 UTC: 1,101 Wh remained, measured pair
        # power was 12.489 kW and the command had already fallen to 10.5 kW.
        # v1.4.1 credited 1,040.75 Wh at constant measured power and therefore
        # asked for only about 7.2 kW after the lag.
        targets = (1500, 2000, 2500, 4000, 2500, 2000, 1500)
        projection = planner.conservative_committed_projection(
            power_w=12489,
            command_w=10500,
            seconds=300,
        )
        self.assertAlmostEqual(projection.wh, 957.875)
        self.assertEqual(projection.end_power_w, 10500)
        self.assertLess(projection.wh, 12489 * 300 / 3600)

        limited_vp1 = planner.conservative_committed_projection(
            power_w=6037,
            command_w=5000,
            seconds=300,
            thermal_limited=True,
        )
        reducing_vp2 = planner.conservative_committed_projection(
            power_w=6452,
            command_w=5500,
            seconds=300,
        )
        self.assertAlmostEqual(limited_vp1.wh + reducing_vp2.wh, 749.5416666667)
        self.assertEqual(limited_vp1.end_power_w + reducing_vp2.end_power_w, 5500)

        decision = planner.remaining_energy_command(
            elapsed_s=5990,
            delivered_wh=14899,
            power_w=12489,
            current_command_w=10500,
            quarter_targets_wh=targets,
            response_gain=1.15,
        )
        self.assertGreater(decision.wanted_w, 12000)
        self.assertEqual(decision.command_w, 12500)

        limited = planner.remaining_energy_command(
            elapsed_s=5990,
            delivered_wh=14899,
            power_w=12489,
            current_command_w=10500,
            quarter_targets_wh=targets,
            thermal_limited=True,
        )
        self.assertEqual(limited.wanted_w, limited.reachable_w)
        self.assertEqual(limited.command_w, 12500)

    def test_thermal_limiter_prevents_constant_committed_projection(self):
        projection = planner.conservative_committed_projection(
            power_w=10000,
            command_w=12000,
            seconds=300,
            thermal_limited=True,
        )
        self.assertEqual(projection.end_power_w, 0)
        self.assertAlmostEqual(projection.wh, 10000 * 0.5 * 300 / 3600)
        self.assertLess(projection.wh, 10000 * 300 / 3600)

        stable = planner.conservative_committed_projection(
            power_w=10000,
            command_w=8000,
            seconds=300,
            command_changing=False,
        )
        self.assertEqual(stable.end_power_w, 10000)
        self.assertAlmostEqual(stable.wh, 10000 * 300 / 3600)

    def test_unexpected_q7_collapse_gets_one_bounded_recovery_step(self):
        # The field pair fell 12.489 -> 8.659 kW inside the 120 s dwell. The
        # bypass is exactly one 1 kW step, even though the planner wants +2 kW.
        decision = planner.apply_retarget_dwell(
            current_command_w=9500,
            planned_command_w=11500,
            power_w=8659,
            previous_power_w=12489,
            seconds_since_previous_power=60,
            seconds_since_retarget=60,
            seconds_since_recovery=1000,
        )
        self.assertEqual(decision.command_w, 10500)
        self.assertTrue(decision.changed)
        self.assertTrue(decision.collapse_recovery)

    def test_quantization_and_repeated_collapse_do_not_chatter(self):
        ordinary = planner.apply_retarget_dwell(
            current_command_w=9500,
            planned_command_w=11500,
            power_w=11800,
            previous_power_w=12489,
            seconds_since_previous_power=30,
            seconds_since_retarget=60,
            seconds_since_recovery=1000,
        )
        self.assertEqual(ordinary.command_w, 9500)
        self.assertFalse(ordinary.collapse_recovery)

        cooldown = planner.apply_retarget_dwell(
            current_command_w=10500,
            planned_command_w=12500,
            power_w=8500,
            previous_power_w=12000,
            seconds_since_previous_power=30,
            seconds_since_retarget=30,
            seconds_since_recovery=30,
        )
        self.assertEqual(cooldown.command_w, 10500)
        self.assertFalse(cooldown.changed)
        self.assertFalse(cooldown.collapse_recovery)

    def test_normal_dwell_and_limiter_down_paths_are_preserved(self):
        elapsed = planner.apply_retarget_dwell(
            current_command_w=9500,
            planned_command_w=11500,
            power_w=9000,
            previous_power_w=9000,
            seconds_since_previous_power=30,
            seconds_since_retarget=120,
        )
        self.assertEqual(elapsed.command_w, 11500)
        self.assertFalse(elapsed.collapse_recovery)
        limited = planner.apply_retarget_dwell(
            current_command_w=9500,
            planned_command_w=8500,
            power_w=9000,
            previous_power_w=9000,
            seconds_since_previous_power=30,
            seconds_since_retarget=30,
            limited_down=True,
        )
        self.assertEqual(limited.command_w, 8500)
        self.assertFalse(limited.collapse_recovery)

    def test_python_rounding_matches_shelly_half_up(self):
        self.assertEqual(planner.round_step_half_up(6250, 500), 6500)
        self.assertEqual(planner.round_step_half_up(6249.9, 500), 6000)

    def test_constant_time_v2_improves_field_model_quarter_replay(self):
        model = planner.PairModel()
        v1 = backtest.simulate("trajectory", model)
        v2 = backtest.simulate("remaining", model)
        self.assertLess(abs(v2["error_wh"]), abs(v1["error_wh"]))
        self.assertLess(
            v2["absolute_quarter_error_wh"], v1["absolute_quarter_error_wh"]
        )
        self.assertLess(
            v2["maximum_absolute_quarter_error_wh"],
            v1["maximum_absolute_quarter_error_wh"],
        )


if __name__ == "__main__":
    unittest.main()
