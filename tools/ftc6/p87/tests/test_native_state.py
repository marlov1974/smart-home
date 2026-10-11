import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from native_state import *

class NativeTests(unittest.TestCase):
    def test_clock_cadence_and_coalescing(self):
        c=NativeClock()
        for _ in range(39): c.interrupt()
        self.assertEqual(c.consume(),0)
        c.interrupt(); self.assertEqual(c.consume(),1)
        for _ in range(80): c.interrupt()
        self.assertEqual(c.consume(),1)  # Two interrupts groups, one pending bit.
        self.assertEqual(c.consume(),0)
        c=NativeClock()
        masks=[]
        for _ in range(3000):
            for _ in range(40): c.interrupt()
            masks.append(c.consume())
        self.assertEqual([sum(bool(m&b) for m in masks) for b in (1,2,4,8,16)],
                         [3000,300,30,5,1])

    def test_rom_timer_vectors(self):
        t=TimerWord(0x8000|599)
        timer_event(t,HISTORY70,1); self.assertEqual(t.word,33367)
        timer_event(t,HISTORY70,2); self.assertEqual(t.word,33368)
        timer_event(t,HISTORY70,2,True); self.assertEqual(t.word,33428)
        t.word=0xfffe
        timer_event(t,HISTORY70,2,True); self.assertEqual(t.word,0xfffe)
        timer_event(t,HISTORY70,2); self.assertEqual(t.word,0xffff)
        timer_event(t,HISTORY70,2); self.assertEqual(t.word,0xffff)

    def test_rom_history70_sequence(self):
        h=History70()
        def run(error,phase,enabled=True):
            return h.evaluate(enabled=enabled,error=error,phase_3d07=phase,previous_phase_3e01=0)
        self.assertEqual(run(200,2),0)
        self.assertEqual(run(199,2),1)
        self.assertEqual(run(199,0),2)
        self.assertEqual(h.timer.word,32768)
        h.timer.word=32768|599;self.assertEqual(run(999,0),2)
        h.timer.word=32768|600;self.assertEqual(run(999,0),0)
        h.state=2;self.assertEqual(run(0,0,False),0);self.assertEqual(h.timer.word,0)

    def test_history70_reentry_overrides_expiry(self):
        h=History70(2,TimerWord(32768|600))
        self.assertEqual(h.evaluate(enabled=True,error=199,phase_3d07=2,previous_phase_3e01=0),1)
        self.assertEqual(h.timer.word,0)

    def test_rom_history50_sequence(self):
        h=History50()
        def run(error):
            return h.evaluate(enabled=True,error=error,phase_3d07=0,mode_4927=2,
                              value_3da4=5,threshold_3944=6)
        self.assertEqual(run(201),0)
        self.assertEqual(run(200),1);self.assertEqual(h.timer.word,32768)
        h.timer.word=32768|179;self.assertEqual(run(999),1)
        h.timer.word=32768|180;self.assertEqual(run(999),0);self.assertEqual(h.timer.word,0)

    def test_limit_order_is_not_minimum(self):
        self.assertEqual(heating_limit(cap_4989=20,history70=2),70)
        self.assertEqual(heating_limit(history70=2,history50=1),50)
        self.assertEqual(heating_limit(history70=2,room_start_limit=True),30)
        self.assertEqual(heating_limit(special_limit=10,zone_not_ready=True),0)
        self.assertEqual(final_limit(70,100,50),50)
        self.assertEqual([limit_code(n) for n in (0,10,30,50,70,100,255)], [10,9,7,5,3,0,0])

if __name__=='__main__':unittest.main()

class IntegratedROMTests(unittest.TestCase):
    def test_original_fixed_flow_profile_sequences(self):
        for profile in (0,1,2):
            h=FixedFlowLimits()
            args=dict(profile=profile,held_error=100)
            self.assertEqual(h.evaluate(3500,3400,phase=2,**args)['native_limit'],100)
            self.assertEqual(h.evaluate(3500,3400,phase=0,**args)['native_limit'],100 if profile==1 else 70)
            h.history70.timer.word=0x8000|600
            self.assertEqual(h.evaluate(3500,3400,phase=0,**args)['native_limit'],100)

class ROMEvidenceChecks(unittest.TestCase):
    def test_incomplete_log_rejected(self):
        from compare_rom_proof import compare
        with self.assertRaises(ValueError):compare('P87_ROM_PASS lookup/0=2700')
    def test_wrong_or_missing_observation_rejected(self):
        from compare_rom_proof import compare, expected_vectors
        text='\n'.join(f'P87_ROM_PASS {k}={v}' for k,v in expected_vectors().items())+'\nP87_ROM_PROOF_COMPLETE'
        self.assertEqual(compare(text)['observations'],53)
        with self.assertRaises(ValueError):compare(text.replace('lookup/0=2700','lookup/0=2701'))
        with self.assertRaises(ValueError):compare(text+'\nERROR script failed')
