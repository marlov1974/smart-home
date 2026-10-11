import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import *
from scenarios import scenarios

class EvidenceTests(unittest.TestCase):
    def test_table_boundary_equality(self):
        self.assertEqual([lookup(e) for e in [-201,-200,-199,-1,0,1,250,251]],
                         [2900,2900,2850,2700,2700,2650,2450,2400])
    def test_table_saturation(self):
        self.assertEqual(lookup(-32768),2900);self.assertEqual(lookup(32767),2400)
    def test_temperature_encoding(self):
        self.assertEqual([temperature_byte(n) for n in [-1,0,1,49,50,51,8000,9000]], [0,0,1,1,1,2,160,160])
    def test_error_encoding_and_word_overflow(self):
        self.assertEqual([error_byte(e) for e in [-4001,-4000,-3951,0,200,32767]], [0,0,0,80,84,0])
    def test_floor_and_override_order(self):
        self.assertEqual(evaluate(2000,2400)['error_cC'],100)
        self.assertEqual(evaluate(5500,2000,override_4911=2)['table_value_cC'],2700)
    def test_held_error_required(self):
        self.assertEqual(evaluate(3500,3000,profile_0900=2)['status'],UNKNOWN)
        self.assertEqual(evaluate(3500,3000,profile_0900=2,held_error=-200)['table_value_cC'],2900)
    def test_unknown_does_not_become_hz(self):
        for r in [evaluate(3500,3000),evaluate(3500,3000,valid=False),evaluate(3500,3000,phase=9),evaluate(None,3000)]:
            self.assertEqual(r['actual_hz'],UNKNOWN); self.assertEqual(r['stop_restart'],UNKNOWN)
    def test_model_not_time_integrating(self):
        self.assertEqual(evaluate(3500,3000),evaluate(3500,3000))
    def test_timer_pause_resume_and_reset(self):
        t=TimerWord(0x8000|179);self.assertEqual(t.status(180),1)
        t.word=0x8000|180;self.assertEqual(t.status(180),2)
        t.pause();self.assertEqual(t.status(180),0);self.assertEqual(t.word,180)
        t.resume();self.assertEqual(t.status(180),2)
        t.reset_start();self.assertEqual(t.word,0x8000)
        t.clear();self.assertEqual(t.word,0)
    def test_pump_gates(self):
        self.assertEqual(pump_step(1,9,3,5),3)
        self.assertEqual(pump_step(1,9,3,5,mode_3d07=2),5)
        self.assertEqual(pump_step(0,8,3,5,state_3ad2=2,correction_49c7=7),0)
        self.assertEqual(pump_step(2,8,3,5,state_3ad2=2,correction_49c7=7),3)
        self.assertEqual(pump_step(1,8,3,5,state_3ad2=2,correction_49c7=7),2)
        self.assertEqual(pump_step(1,8,3,5,state_3ad2=0,correction_49c7=7),5)
    def test_balance(self):
        self.assertAlmostEqual(water_balance_delta(6000,15),5.741626794,places=7)
        self.assertEqual(water_balance_delta(6000,0),UNKNOWN)
    def test_all_scenarios_explicit_limitations(self):
        rows=scenarios();self.assertEqual([x['scenario'] for x in rows],list(range(1,9)))
        self.assertTrue(all(x['unresolved'] and x['timeline'] for x in rows))
if __name__=='__main__': unittest.main()
