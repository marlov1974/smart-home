"""P0072 snapshot coherence and firmware identity, offline RPC fixtures."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import read_mvp


class CaptureTests(unittest.TestCase):
    def capture(self, change=False, stale=False, wrong=False, revision=1, package=72, slave=1, expected_uid=None, derived_change=False):
        reads = []
        def read(host, address, quantity, requested_slave):
            self.assertEqual(requested_slave, slave)
            self.assertEqual(host, 'fixture')
            self.assertLessEqual(quantity, 16)
            seen = reads.count(address)
            reads.append(address)
            values = [0]*quantity
            if address == 0:
                values[:2] = [888, 71 if wrong else package]
            elif address == 68:
                values = [revision, 1, 15, 0] if package == 76 else [1, 1, 1, 4] if revision == 1 else [revision, 1, 3, 0]
            elif address == 72:
                values = [1,slave,slave,3,1,1,0x0123,0x4567,0x89ab,0xcdef,0x1357,0x2468,0x60|slave,1,0]
            elif address in (180, 196):
                values = [2 if change and seen else 1]*quantity
                if address == 180 and derived_change and seen:
                    values[3] = 2
            elif address in (140, 156):
                values = [2 if stale and seen else 1]*quantity
            elif address == 283:
                values = [1,2,5,64,1104,40,0,0,257,256,0,0,0,40,6,1]
            elif address == 320:
                values = [1,2,0,6000,3800,0,6000,0,5900,0,5800,0,100,0,1,5]
            elif address == 352:
                values = [1,0,1,7,19,60,180,2,65535,0,1,4464,0,6000,0,5900]
            elif address == 368:
                values = [0,5800,65535,65436]
            elif address == 100:
                values[:2] = [0xffff, 0xff9c]  # signed -100 centidegrees
            return {'address': address, 'quantity': quantity, 'values': values, 'timestamp': 'fixture'}
        with patch.object(read_mvp, 'request_block', read):
            return read_mvp.capture('fixture',slave,expected_uid)

    def test_pause_revision_and_diagnostics(self):
        result = self.capture(package=76, revision=2)
        self.assertEqual(result['identity'], [2, 1, 15, 0])
        for quality, name in ((8, 'wait-native'), (9, 'settling')):
            words = [1, quality, 0] + [0]*17
            self.assertEqual(read_mvp.decode_feedback(words)['quality_name'], name)

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

    def test_p76_address_and_physical_identity(self):
        result = self.capture(package=76,slave=2,expected_uid='0123456789abcdef13572468')
        self.assertEqual(result['package'],76)
        self.assertEqual(result['identity'],[1,1,15,0])
        self.assertEqual(result['unit_identity']['slave_id'],2)
        self.assertEqual(result['unit_identity']['source_name'],'hardware-dip')
        self.assertEqual(result['unit_identity']['dip']['raw'],0x62)
        self.assertEqual(result['unit_identity']['uid_words'],[0x01234567,0x89abcdef,0x13572468])
        self.assertEqual(result['effect_diagnostics']['short_w'],5900)
        self.assertFalse(result['effect_diagnostics']['atomic'])
        self.assertIsNotNone(result['controller_diagnostics'])
        feedback=result['feedback_diagnostics']
        self.assertEqual(feedback['accepted_count'],70000)
        self.assertEqual(feedback['temperature_generation'],65535)
        self.assertEqual(feedback['flow_generation'],0)
        self.assertEqual(feedback['short_count'],7)
        self.assertEqual(feedback['slow_count'],19)
        self.assertEqual(feedback['short_span_s'],60)
        self.assertEqual(feedback['slow_span_s'],180)
        self.assertEqual(feedback['instant_w'],6000)
        self.assertEqual(feedback['short_w'],5900)
        self.assertEqual(feedback['slow_w'],5800)
        self.assertEqual(feedback['derivative_w_per_min'],-100)
        self.assertEqual(feedback['last_age_s'],2)
        self.assertFalse(feedback['atomic'])

    def test_expected_uid_mismatch_refused(self):
        with self.assertRaises(ValueError):
            self.capture(package=76,slave=2,expected_uid='111111112222222233333333')
        with self.assertRaises(ValueError):
            self.capture(expected_uid='0123456789abcdef13572468')

    def test_source_changed_with_unchanged_derived_counter(self):
        result=self.capture(derived_change=True)
        self.assertFalse(result['samples']['heat_W']['coherent'])
        self.assertIsNone(result['samples']['heat_W']['value'])
        self.assertTrue(result['samples']['flow_cL_min']['coherent'])

    def test_invalid_slave_never_reads(self):
        with patch.object(read_mvp,'request_block') as read:
            for slave in (0,248,-1,True,'2'):
                with self.assertRaises(ValueError):read_mvp.capture('unused',slave)
            read.assert_not_called()

    def test_addressed_read_url_and_validation(self):
        import io,json
        with patch.object(read_mvp,'urlopen',return_value=io.BytesIO(json.dumps({'values':[888,76]}).encode())) as opened:
            result=read_mvp.request_block('fixture',0,2,slave=2)
            self.assertIn('sid=2&addr=0&qty=2',opened.call_args.args[0])
            self.assertEqual(result['slave_id'],2)
        with patch.object(read_mvp,'urlopen') as opened:
            with self.assertRaises(ValueError):read_mvp.request_block('unused',0,2,slave=0)
            opened.assert_not_called()

    def test_effect_invalid_sentinel_and_signed_fields(self):
        words=[0]*32;words[0]=1;words[5]=0x8000;words[11:13]=[0xffff,0xff9c];words[19]=0xffce
        result=read_mvp.decode_effect(words)
        self.assertIsNone(result['instant_w'])
        self.assertEqual(result['error_w'],-100)
        self.assertEqual(result['last_adjustment_cC'],-50)

    def test_wrong_build(self):
        with self.assertRaises(ValueError):
            self.capture(wrong=True)

    def test_feedback_invalid_sentinels_and_unsigned_counter(self):
        words=[1,3,0,0,0,0,0,65535,0,0,65535,65535,0x8000,0,0x8000,0,0x8000,0,0xffff,0xff9c]
        feedback=read_mvp.decode_feedback(words)
        self.assertEqual(feedback['quality_name'],'stale')
        self.assertFalse(feedback['ready'])
        self.assertIsNone(feedback['last_age_s'])
        self.assertEqual(feedback['last_age_s_raw'],65535)
        self.assertEqual(feedback['accepted_count'],4294967295)
        for name in ('instant_w','short_w','slow_w'):
            self.assertIsNone(feedback[name])
        self.assertEqual(feedback['derivative_w_per_min'],-100)
        self.assertFalse(feedback['atomic'])

    def test_feedback_partial_window_and_bad_schema(self):
        words=[1,1,0,2,2,10,10,1,2,2,0,2,0,1000,0,1000,0,1000,0,0]
        result=read_mvp.decode_feedback(words)
        self.assertEqual(result['short_span_s'],10)
        self.assertEqual(result['slow_span_s'],10)
        self.assertEqual(result['slow_window_s'],180)
        self.assertFalse(result['ready'])
        self.assertIsNone(self.capture()['feedback_diagnostics'])
        for broken in (None,words[:-1],[2]+words[1:],words[:1]+[10]+words[2:],words[:2]+[2]+words[3:]):
            with self.assertRaises(ValueError):read_mvp.decode_feedback(broken)


if __name__ == '__main__':
    unittest.main()
