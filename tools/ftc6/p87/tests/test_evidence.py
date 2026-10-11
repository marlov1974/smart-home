import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_local import derive
from replay import replay
class NegativeEvidence(unittest.TestCase):
    def test_wrong_image(self):
        with self.assertRaises(ValueError):derive(b'wrong image','')
    def test_empty_history_not_successful_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'events';p.write_text('')
            r=replay(p);self.assertEqual(r['groups'],[]);self.assertEqual(r['prediction_validation'],'UNKNOWN')
