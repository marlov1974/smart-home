import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src" / "ha" / "dashboards" / "ftx.yaml"
DEP = ROOT / "dep" / "ha" / "dashboards" / "ftx.yaml"
SRC_FTX_SVG = ROOT / "src" / "ha" / "assets" / "ftx-industrial.svg"
DEP_FTX_SVG = ROOT / "dep" / "ha" / "assets" / "ftx-industrial.svg"


def _total_power_gauge_block(text):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "name: Total effekt":
            start = index
            while start > 0 and lines[start].strip() != "- type: gauge":
                start -= 1
            end = index + 1
            while end < len(lines) and not lines[end].startswith("      - "):
                end += 1
            return "\n".join(lines[start:end])
    raise AssertionError("Total effekt gauge block not found")


class FtxDashboardTests(unittest.TestCase):
    def test_deploy_dashboard_matches_source(self):
        self.assertEqual(SRC.read_text(encoding="utf-8"), DEP.read_text(encoding="utf-8"))

    def test_total_power_gauge_uses_450w_max(self):
        block = _total_power_gauge_block(DEP.read_text(encoding="utf-8"))

        self.assertIn("entity: sensor.ftx_total_effekt_2", block)
        self.assertIn("min: 0", block)
        self.assertIn("max: 450", block)
        self.assertIn("yellow: 300", block)
        self.assertIn("red: 400", block)
        self.assertNotIn("max: 5000", block)

    def test_ftx_svg_deploy_asset_matches_source(self):
        self.assertEqual(SRC_FTX_SVG.read_text(encoding="utf-8"), DEP_FTX_SVG.read_text(encoding="utf-8"))

    def test_ftx_svg_is_valid_svg_asset(self):
        root = ElementTree.fromstring(DEP_FTX_SVG.read_text(encoding="utf-8"))

        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertEqual(root.attrib["viewBox"], "0 0 1280 720")

    def test_ftx_svg_keeps_industrial_dark_contract(self):
        text = DEP_FTX_SVG.read_text(encoding="utf-8")

        self.assertIn('fill="#000000"', text)
        self.assertIn(">FTX<", text)
        self.assertIn(">VVX<", text)
        self.assertIn(">TILLUFT HUS<", text)
        self.assertIn(">FRANLUFT HUS<", text)
        self.assertIn(">MAX 450 W<", text)


if __name__ == "__main__":
    unittest.main()
