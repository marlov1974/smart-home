from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
FEATURE_TARGET = ROOT / "src" / "shelly" / "ftx" / "brain" / "feature-target.js"


class DewpointMarginSourceTests(unittest.TestCase):
    def test_min_supply_temp_uses_dewpoint_without_added_margin(self) -> None:
        source = FEATURE_TARGET.read_text(encoding="utf-8")

        self.assertNotIn("DEWPOINT_SUPPLY_MARGIN_C", source)
        self.assertNotIn("dewPointHouseC +", source)
        self.assertIn("var TARGET_TO_HOUSE_MIN_C = 12.0;", source)
        self.assertNotIn("var TARGET_TO_HOUSE_MIN_C = 14.0;", source)
        self.assertIn(
            "ctx.sig.min_supply_temp_c = d1(max2(dewPointHouseC, TARGET_TO_HOUSE_MIN_C));",
            source,
        )


if __name__ == "__main__":
    unittest.main()
