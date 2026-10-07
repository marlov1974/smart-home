"""P0072 snapshot coherence and firmware identity, offline RPC fixtures."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import read_mvp


class CaptureTests(unittest.TestCase):
    def capture(self, change=False, stale=False, wrong=False, revision=1):
        reads = []
        def read(host, address, quantity):
            self.assertEqual(host, 'fixture')
            self.assertLessEqual(quantity, 16)
            seen = reads.count(address)
            reads.append(address)
            values = [0]*quantity
            if address == 0:
                values[:2] = [888, 71 if wrong else 72]
            elif address == 68:
                values = [1, 1, 1, 4] if revision == 1 else [revision, 1, 3, 0]
            elif address in (180, 196):
                values = [2 if change and seen else 1]*quantity
            elif address in (140, 156):
                values = [2 if stale and seen else 1]*quantity
            elif address == 283:
                values = [1,2,5,64,1104,40,0,0,257,256,0,0,0,40,6,1]
            elif address == 100:
                values[:2] = [0xffff, 0xff9c]  # signed -100 centidegrees
            return {'address': address, 'quantity': quantity, 'values': values, 'timestamp': 'fixture'}
        with patch.object(read_mvp, 'request_block', read):
            return read_mvp.capture('fixture')

    def test_control_revision(self):
        result = self.capture(revision=2)
        self.assertEqual(result["identity"], [2, 1, 3, 0])
        self.assertEqual(len(result["control_words_256_282"]), 27)

    def test_revision3_diagnostics(self):
        d = self.capture(revision=3)['controller_diagnostics']
        self.assertEqual(d['blocking_mask'],64)
        self.assertEqual(d['flags']['prohibit_heating_z1'],1)
        self.assertEqual(d['flags']['prohibit_cooling_z1'],1)
        self.assertEqual(d['last_rejected_byte'],6)
        self.assertEqual(d['age_s'],2)

    def test_signed_value(self):
        sample = self.capture()['samples']['brine_in_cC']
        self.assertEqual(sample['value'], -100)
        self.assertTrue(sample['coherent'])

    def test_cross_update(self):
        sample = self.capture(change=True)['samples']['brine_in_cC']
        self.assertFalse(sample['coherent'])
        self.assertIsNone(sample['value'])

    def test_stale_during_read(self):
        self.assertIsNone(self.capture(stale=True)['samples']['brine_in_cC']['value'])

    def test_wrong_build(self):
        with self.assertRaises(ValueError):
            self.capture(wrong=True)


if __name__ == '__main__':
    unittest.main()
