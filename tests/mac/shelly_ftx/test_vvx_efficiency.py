from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PERF_VVX = ROOT / "src" / "shelly" / "ftx" / "state" / "perf-vvx.js"


class VvxEfficiencySourceTests(unittest.TestCase):
    def test_stopped_vvx_guard_sets_zero_before_running_formula(self) -> None:
        source = PERF_VVX.read_text(encoding="utf-8")

        guard_index = source.index("if (!ctx.run || !ctx.run.vvx)")
        running_formula_index = source.index("var eff = calcVvxEfficiency")

        self.assertLess(guard_index, running_formula_index)
        self.assertIn("ctx.vvx_eff_pct = 0;", source)
        self.assertIn("ctx.vvx_eff_hist = { r0: 0, r1: 0, r2: 0 };", source)
        self.assertIn("return;\n  }\n  var eff = calcVvxEfficiency", source)


if __name__ == "__main__":
    unittest.main()
